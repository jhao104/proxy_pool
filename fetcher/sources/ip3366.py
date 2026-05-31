# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ip3366.py
   Description :   云代理代理源
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


class Ip3366Fetcher(BaseFetcher):
    """云代理 http://www.ip3366.net/"""

    name = "ip3366"
    url = "http://www.ip3366.net/"

    def fetch(self):
        urls = [
            'http://www.ip3366.net/free/?stype=1',
            "http://www.ip3366.net/free/?stype=2",
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
                r.text)
            for proxy in proxies:
                yield ":".join(proxy)


if __name__ == '__main__':
    for proxy in Ip3366Fetcher().fetch():
        print(proxy)