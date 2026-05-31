# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     goodips.py
   Description :   谷德代理代理源
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


class GoodipsFetcher(BaseFetcher):
    """谷德代理 https://www.goodips.com/"""

    name = "goodips"
    url = "https://www.goodips.com/"

    def fetch(self):
        url = "https://www.goodips.com/"
        tree = WebRequest().get(url, verify=False).tree
        for item in tree.xpath("//div[@class='table-list']"):
            ip = "".join(item.xpath("./ul/li[1]/text()")).strip()
            port = "".join(item.xpath("./ul/li[2]/text()")).strip()
            if ip and port:
                yield "%s:%s" % (ip, port)


if __name__ == '__main__':
    for proxy in GoodipsFetcher().fetch():
        print(proxy)