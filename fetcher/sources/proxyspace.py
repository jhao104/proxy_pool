# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyspace.py
   Description :   ProxySpace代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 proxyspace 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxySpaceFetcher(BaseFetcher):
    """ProxySpace https://proxyspace.pro"""

    name = "proxyspace"
    url = "https://proxyspace.pro"
    enabled = True

    def fetch(self):
        try:
            url = "https://proxyspace.pro/http.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - proxyspace: %s" % e)


if __name__ == '__main__':
    for proxy in ProxySpaceFetcher().fetch():
        print(proxy)
