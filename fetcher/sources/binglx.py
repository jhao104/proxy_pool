# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     binglx.py
   Description :   冰凌代理代理源
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


class BinglxFetcher(BaseFetcher):
    """冰凌代理 https://www.binglx.cn"""

    name = "binglx"
    url = "https://www.binglx.cn/"

    def fetch(self):
        url = "https://www.binglx.cn/?page=1"
        try:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            print(e)


if __name__ == '__main__':
    for proxy in BinglxFetcher().fetch():
        print(proxy)