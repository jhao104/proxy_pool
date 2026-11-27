# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy5.py
   Description :   Proxy5代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 Proxy5 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Proxy5Fetcher(BaseFetcher):
    """
    Proxy5 https://proxy5.net/cn/free-proxy

    注意: 当前实测该站点返回 403(反爬拦截), 抓不到任何数据, 暂时禁用;
    解析逻辑保留。
    """

    name = "proxy5"
    url = "https://proxy5.net/cn/free-proxy"
    enabled = False

    _ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    def fetch(self):
        try:
            tree = WebRequest().get(
                self.url, timeout=10, retry_time=1).tree
            proxies = []
            if tree is not None:
                for tr in tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/strong/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    if self._ip_pattern.match(ip) and port.isdigit():
                        proxies.append("%s:%s" % (ip, port))
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - proxy5: %s" % e)


if __name__ == '__main__':
    for proxy in Proxy5Fetcher().fetch():
        print(proxy)
