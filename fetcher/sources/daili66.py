# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     daili66.py
   Description :   66代理
   Author :        JHao
   date：          2026/06/08
-------------------------------------------------
   Change Activity:
                   2026/06/08:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

class DaiLi66Fetcher(BaseFetcher):
    """66代理 https://www.66daili.com"""

    name = "daili66"
    url = "https://www.66daili.com"

    enabled = True

    def fetch(self):
        url = "http://api.66daili.com/?format=json"
        r = WebRequest().get(url, timeout=10)
        try:
            for each in r.json.get("data", []):
                yield "%s:%s" % (each["ip"], each["port"])
        except Exception as e:
            logger.error("ProxyFetch - daili66: %s" % e)



if __name__ == '__main__':
    for proxy in DaiLi66Fetcher().fetch():
        print(proxy)
