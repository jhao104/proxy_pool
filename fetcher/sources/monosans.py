# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     monosans.py
   Description :   Monosans代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 monosans 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class MonosansFetcher(BaseFetcher):
    """Monosans Proxy List https://github.com/monosans/proxy-list"""

    name = "monosans"
    url = "https://github.com/monosans/proxy-list"
    enabled = True

    def fetch(self):
        try:
            url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - monosans: %s" % e)


if __name__ == '__main__':
    for proxy in MonosansFetcher().fetch():
        print(proxy)
