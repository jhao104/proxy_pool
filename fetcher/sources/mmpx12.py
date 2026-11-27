# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     mmpx12.py
   Description :   Mmpx12代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 mmpx12 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Mmpx12Fetcher(BaseFetcher):
    """Mmpx12 Proxy List https://github.com/mmpx12/proxy-list"""

    name = "mmpx12"
    url = "https://github.com/mmpx12/proxy-list"
    enabled = True

    def fetch(self):
        try:
            url = "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - mmpx12: %s" % e)


if __name__ == '__main__':
    for proxy in Mmpx12Fetcher().fetch():
        print(proxy)
