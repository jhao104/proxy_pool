# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     thespeedx.py
   Description :   TheSpeedX代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 thespeedx 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class TheSpeedXFetcher(BaseFetcher):
    """TheSpeedX SOCKS-List(仅取 http 列表) https://github.com/TheSpeedX/SOCKS-List"""

    name = "thespeedx"
    url = "https://github.com/TheSpeedX/SOCKS-List"
    enabled = True

    def fetch(self):
        try:
            url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - thespeedx: %s" % e)


if __name__ == '__main__':
    for proxy in TheSpeedXFetcher().fetch():
        print(proxy)
