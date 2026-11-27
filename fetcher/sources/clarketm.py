# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     clarketm.py
   Description :   Clarketm代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 clarketm 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ClarketmFetcher(BaseFetcher):
    """Clarketm Proxy List https://github.com/clarketm/proxy-list"""

    name = "clarketm"
    url = "https://github.com/clarketm/proxy-list"
    enabled = True

    def fetch(self):
        try:
            url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - clarketm: %s" % e)


if __name__ == '__main__':
    for proxy in ClarketmFetcher().fetch():
        print(proxy)
