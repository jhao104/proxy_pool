# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     roundproxies.py
   Description :   Roundproxies
   Author :        JHao
   date：          2026/06/09
-------------------------------------------------
   Change Activity:
                   2026/06/09:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

class RoundProxiesFetcher(BaseFetcher):
    """Roundproxies https://roundproxies.com/free-proxy-list"""

    name = "roundproxies"
    url = "https://roundproxies.com/free-proxy-list"

    enabled = True

    def fetch(self):
        page_size = 50
        _url = f"https://roundproxies.com/api/get-free-proxies/?limit={page_size}&page=1&sort_by=lastChecked&sort_type=desc"
        r = WebRequest().get(_url, timeout=10)
        try:
            for each in r.json.get("data", []):
                yield "%s:%s" % (each["ip"], each["port"])
        except Exception as e:
            logger.error("ProxyFetch - roundproxies: %s" % e)



if __name__ == '__main__':
    for proxy in RoundProxiesFetcher().fetch():
        print(proxy)
