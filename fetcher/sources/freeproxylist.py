# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freeproxylist.py
   Description :   FreeProxyList代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from urllib import parse

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class FreeProxyListFetcher(BaseFetcher):
    """FreeProxyList https://www.freeproxylists.net/zh/"""

    name = "freeproxylist"
    url = "https://www.freeproxylists.net/zh/"

    @staticmethod
    def _parse_ip(input_str):
        html_str = parse.unquote(input_str)
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
        return ips[0] if ips else None

    def fetch(self):
        url = ("https://www.freeproxylists.net/zh/"
               "?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50")
        tree = WebRequest().get(url, verify=False).tree
        for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
            ip = self._parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
            port = "".join(tr.xpath('./td[2]/text()')).strip()
            if ip:
                yield "%s:%s" % (ip, port)


if __name__ == '__main__':
    for proxy in FreeProxyListFetcher().fetch():
        print(proxy)
