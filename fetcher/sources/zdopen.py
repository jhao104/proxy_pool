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
-------------------------------------------------
"""
__author__ = 'JHao'

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

    # 运营商可选值: 电信、联通、移动、铁通、教育网、阿里云、腾讯云; 留空则不限制
    isp = ""

    # return_type=3 返回 JSON, 便于直接取 ip/port
    api = ("http://www.zdopen.com/FreeProxy/Get/"
           "?app_id=202601221510072813&akey=febfef47436c13bf&dalu=1&return_type=3")

    def fetch(self):
        url = self.api
        if self.isp:
            url = "%s&isp=%s" % (url, quote(self.isp))
        r = WebRequest().get(url, timeout=10)
        try:
            payload = r.json or {}
            if str(payload.get("code")) != "10001":
                logger.error("ProxyFetch - zdopen: %s" % payload.get("msg", "unknown error"))
                return
            for each in payload.get("data", {}).get("proxy_list", []):
                # 池内验证只走 HTTP, socks 代理无法直接使用
                if each.get("protocol") != "http":
                    continue
                yield "%s:%s" % (each["ip"], each["port"])
        except Exception as e:
            logger.error("ProxyFetch - zdopen: %s" % e)


if __name__ == '__main__':
    for proxy in ZdopenFetcher().fetch():
        print(proxy)
