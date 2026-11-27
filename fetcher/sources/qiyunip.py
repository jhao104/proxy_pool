# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     qiyunip.py
   Description :   齐云代理代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 齐云代理 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class QiyunipFetcher(BaseFetcher):
    """齐云代理 https://www.qiyunip.com/freeProxy/"""

    name = "qiyunip"
    url = "https://www.qiyunip.com/freeProxy/"
    enabled = True

    _ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    def fetch(self):
        try:
            tree = WebRequest().get(
                self.url, timeout=10, retry_time=1).tree
            proxies = []
            if tree is not None:
                for tr in tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./th[1]/text()")).strip()
                    port = "".join(tr.xpath("./th[2]/text()")).strip()
                    if self._ip_pattern.match(ip) and port.isdigit():
                        proxies.append("%s:%s" % (ip, port))
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - qiyunip: %s" % e)


if __name__ == '__main__':
    for proxy in QiyunipFetcher().fetch():
        print(proxy)
