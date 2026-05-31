# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     kxdaili.py
   Description :   开心代理代理源
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


class KxdailiFetcher(BaseFetcher):
    """开心代理 http://www.kxdaili.com/"""

    name = "kxdaili"
    url = "http://www.kxdaili.com/dailiip.html"

    def fetch(self):
        target_urls = [
            "http://www.kxdaili.com/dailiip.html",
            "http://www.kxdaili.com/dailiip/2/1.html",
        ]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)


if __name__ == '__main__':
    for proxy in KxdailiFetcher().fetch():
        print(proxy)
