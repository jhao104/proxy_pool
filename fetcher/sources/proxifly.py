# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxifly.py
   Description :   Proxifly代理源
   Author :        JHao
   date：          2026/06/01
-------------------------------------------------
   Change Activity:
                   2026/06/01:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxiFlyFetcher(BaseFetcher):
    """Proxifly https://proxifly.dev"""

    name = "proxifly"
    url = "https://proxifly.dev/"

    enabled = True  # 是否启用

    def fetch(self):
        r = WebRequest().get("https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.json", timeout=10)
        try:
            for each in r.json:
                if each.get("geolocation", {}).get("country", "") == "CN" and each.get("protocol") == "http":
                    yield self.parseProxiesFromText(each.get('proxy', "")).pop()
        except Exception as e:
            logger.error("ProxyFetch - proxifly: %s" % e)


if __name__ == '__main__':
    for proxy in ProxiFlyFetcher().fetch():
        print(proxy)