# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freeproxyworld.py
   Description :   FreeProxyWorld代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 freeproxyworld 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

_IP_RE = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}$')
_PORT_RE = re.compile(r'^\d{2,5}$')


class FreeProxyWorldFetcher(BaseFetcher):
    """FreeProxyWorld https://www.freeproxy.world/ (实测可用)"""

    name = "freeproxyworld"
    url = "https://www.freeproxy.world/"
    enabled = True
    request_interval = 2

    def fetch(self, page_count=5):
        proxies = []
        for page in range(1, page_count + 1):
            url = ("https://www.freeproxy.world/?type=&anonymity=&country="
                   "&speed=&port=&page=%d" % page)
            try:
                r = WebRequest().get(url, timeout=10, retry_time=1)
                tree = r.tree
                if tree is not None:
                    for tr in tree.xpath("//table//tr"):
                        ip = "".join(tr.xpath("./td[1]/text()")).strip()
                        port = "".join(tr.xpath("./td[2]/a/text()")).strip()
                        proxy_type = "".join(tr.xpath("./td[6]/a/text()")).strip().lower()
                        if not _IP_RE.match(ip) or not _PORT_RE.match(port):
                            continue
                        # 只保留 HTTP/HTTPS, 过滤 socks
                        if 'socks' in proxy_type:
                            continue
                        if proxy_type and 'http' not in proxy_type:
                            continue
                        proxies.append("%s:%s" % (ip, port))
            except Exception as e:
                logger.error("ProxyFetch - %s: %s" % (self.name, e))
            sleep(self.request_interval)

        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in FreeProxyWorldFetcher().fetch():
        print(proxy)
