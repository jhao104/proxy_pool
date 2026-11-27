# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ip89_web.py
   Description :   89免费代理批量提取代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 89免费代理批量提取源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Ip89WebFetcher(BaseFetcher):
    """89免费代理批量提取 https://www.89ip.cn/"""

    name = "ip89_web"
    url = "https://www.89ip.cn/"

    # 实测可拿到数据
    enabled = True

    api = "https://www.89ip.cn/tqdl.html"

    headers = {
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,"
                   "image/avif,image/webp,image/apng,*/*;q=0.8,"
                   "application/signed-exchange;v=b3;q=0.7"),
        "Referer": "https://www.89ip.cn/ti.html",
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/123.0.0.0 Safari/537.36"),
    }

    params = {
        "num": "9999",
        "address": "",
        "kill_address": "",
        "port": "",
        "kill_port": "",
        "isp": "",
    }

    def fetch(self):
        try:
            r = WebRequest().get(self.api, header=self.headers,
                                 params=self.params, timeout=10, retry_time=1)
            # 响应是混着广告 HTML 的纯文本 ip:port 列表, 用基类方法提取
            proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - ip89_web: %s" % e)


if __name__ == '__main__':
    for proxy in Ip89WebFetcher().fetch():
        print(proxy)
