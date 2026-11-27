# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxiflyraw.py
   Description :   Proxifly Raw文本代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 proxifly_raw 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxiflyRawFetcher(BaseFetcher):
    """Proxifly Free Proxy List(纯文本 http 列表) https://proxifly.dev/"""

    name = "proxifly_raw"
    url = "https://proxifly.dev/"
    enabled = True

    def fetch(self):
        try:
            url = ("https://raw.githubusercontent.com/proxifly/free-proxy-list/"
                   "main/proxies/protocols/http/data.txt")
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - proxifly_raw: %s" % e)


if __name__ == '__main__':
    for proxy in ProxiflyRawFetcher().fetch():
        print(proxy)
