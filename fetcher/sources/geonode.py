# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     geonode.py
   Description :   Geonode代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class GeonodeFetcher(BaseFetcher):
    """Geonode Free Proxy https://geonode.com/free-proxy-list/"""

    name = "geonode"
    url = "https://geonode.com/free-proxy-list/"

    def fetch(self):
        url = ("https://proxylist.geonode.com/api/proxy-list?"
               "limit=500&page=1&sort_by=lastChecked&sort_type=desc")
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        try:
            proxies = self.parseProxiesFromJson(r.json)
            if not proxies:
                proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            print(e)


if __name__ == '__main__':
    for proxy in GeonodeFetcher().fetch():
        print(proxy)