# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     openproxylist_xyz.py
   Description :   OpenProxyList.xyz代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 openproxylist_xyz 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class OpenProxyListXyzFetcher(BaseFetcher):
    """OpenProxyList.xyz https://openproxylist.xyz"""

    name = "openproxylist_xyz"
    url = "https://openproxylist.xyz"
    enabled = True

    def fetch(self):
        try:
            url = "https://openproxylist.xyz/http.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - openproxylist_xyz: %s" % e)


if __name__ == '__main__':
    for proxy in OpenProxyListXyzFetcher().fetch():
        print(proxy)
