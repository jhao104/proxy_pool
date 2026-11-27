# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     roosterkid.py
   Description :   Roosterkid代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 roosterkid 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class RoosterkidFetcher(BaseFetcher):
    """Roosterkid OpenProxyList https://github.com/roosterkid/openproxylist"""

    name = "roosterkid"
    url = "https://github.com/roosterkid/openproxylist"
    enabled = True

    def fetch(self):
        try:
            url = "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - roosterkid: %s" % e)


if __name__ == '__main__':
    for proxy in RoosterkidFetcher().fetch():
        print(proxy)
