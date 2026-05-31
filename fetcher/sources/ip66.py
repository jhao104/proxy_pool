# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ip66.py
   Description :   代理66代理源
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


class Ip66Fetcher(BaseFetcher):
    """代理66 http://www.66ip.cn/"""

    name = "ip66"
    url = "http://www.66ip.cn/"

    def fetch(self):
        url = "http://www.66ip.cn/"
        resp = WebRequest().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)


if __name__ == '__main__':
    for proxy in Ip66Fetcher().fetch():
        print(proxy)
