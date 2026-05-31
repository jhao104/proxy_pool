# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freevpnnode.py
   Description :   FreeVPNNode代理源
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


class FreeVPNNodeFetcher(BaseFetcher):
    """FreeVPNNode https://cn.freevpnnode.com/free-proxy/"""

    name = "freevpnnode"
    url = "https://cn.freevpnnode.com/free-proxy/"

    def fetch(self):
        url = "https://cn.freevpnnode.com/free-proxy/"
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        proxies = self.parseProxiesFromTree(r.tree)
        proxies.extend(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in FreeVPNNodeFetcher().fetch():
        print(proxy)
