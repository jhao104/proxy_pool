# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     docip.py
   Description :   稻壳代理代理源
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


class DocipFetcher(BaseFetcher):
    """稻壳代理 https://www.docip.net/"""

    name = "docip"
    url = "https://www.docip.net/"

    def fetch(self):
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)


if __name__ == '__main__':
    for proxy in DocipFetcher().fetch():
        print(proxy)