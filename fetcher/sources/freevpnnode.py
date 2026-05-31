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

import re

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class FreeVPNNodeFetcher(BaseFetcher):
    """FreeVPNNode https://cn.freevpnnode.com/free-proxy/"""

    name = "freevpnnode"
    url = "https://cn.freevpnnode.com/free-proxy/"

    def fetch(self):
        url = "https://cn.freevpnnode.com/free-proxy/"
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        proxies = []
        if r.tree is not None:
            for tr in r.tree.xpath("//tr"):
                cells = [" ".join(td.xpath(".//text()")).strip() for td in tr.xpath("./td")]
                if len(cells) >= 2:
                    ip_match = re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', cells[0])
                    port_match = re.match(r'^\d{2,5}$', cells[1])
                    if ip_match and port_match:
                        proxies.append("%s:%s" % (cells[0], cells[1]))
        proxies.extend(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in FreeVPNNodeFetcher().fetch():
        print(proxy)
