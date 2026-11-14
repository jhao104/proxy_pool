# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     zdopen.py
   Description :   站大爷开放接口代理源
   Author :        JHao
   date：          2026/11/14
-------------------------------------------------
   Change Activity:
                   2026/11/14: 新增站大爷开放接口源, 每2小时抓取一轮(接口限流 10 秒 2 次)
                   2026/11/14: 每轮依次抓取各运营商, 请求间按限流间隔休眠
-------------------------------------------------
"""
__author__ = 'JHao'

from time import sleep
from urllib.parse import quote

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ZdopenFetcher(BaseFetcher):
    """站大爷免费代理开放接口 http://www.zdopen.com/FreeProxy/Get/"""

    name = "zdopen"
    url = "http://www.zdopen.com/FreeProxy/Get/"

    enabled = True

    # 接口每 10 秒只允许请求 2 次, 且代理更新周期较长, 每 2 小时抓取一轮
    interval = 2 * 60 * 60

    # 每轮依次抓取的运营商(顺序即请求顺序)
    isp_list = ("电信", "联通", "移动", "铁通", "教育网", "阿里云", "腾讯云")

    # 限流: 每 10 秒最多 2 次 -> 请求间隔 7 秒, 任意 10 秒窗口内不超过 2 次
    request_interval = 7

    # return_type=3 返回 JSON, 便于直接取 ip/port
    api = ("http://www.zdopen.com/FreeProxy/Get/"
           "?app_id=202601221510072813&akey=febfef47436c13bf&dalu=1&return_type=3")

    def fetch(self):
        """依次抓取各运营商, 跨运营商去重后 yield"""
        seen = set()
        for index, isp in enumerate(self.isp_list):
            # 第一个运营商无需等待, 之后每个请求前休眠, 避免触发限流
            if index:
                sleep(self.request_interval)
            for proxy in self.fetchByIsp(isp):
                if proxy not in seen:
                    seen.add(proxy)
                    yield proxy

    def fetchByIsp(self, isp):
        """抓取单个运营商的代理, 失败只记日志不影响后续运营商"""
        url = "%s&isp=%s" % (self.api, quote(isp))
        try:
            # retry_time=1: 不重试, 避免失败重试叠加请求次数超出限流
            r = WebRequest().get(url, timeout=10, retry_time=1)
            payload = r.json or {}
            if str(payload.get("code")) != "10001":
                logger.error("ProxyFetch - zdopen[%s]: %s" % (isp, payload.get("msg", "unknown error")))
                return
            for each in payload.get("data", {}).get("proxy_list", []):
                # 池内验证只走 HTTP, socks 代理无法直接使用
                if each.get("protocol") != "http":
                    continue
                yield "%s:%s" % (each["ip"], each["port"])
        except Exception as e:
            logger.error("ProxyFetch - zdopen[%s]: %s" % (isp, e))


if __name__ == '__main__':
    for proxy in ZdopenFetcher().fetch():
        print(proxy)
