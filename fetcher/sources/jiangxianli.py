# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     jiangxianli.py
   Description :   免费代理库代理源
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


class JiangxianliFetcher(BaseFetcher):
    """免费代理库 http://ip.jiangxianli.com/"""

    name = "jiangxianli"
    url = "http://ip.jiangxianli.com/"

    def fetch(self, page_count=1):
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()


if __name__ == '__main__':
    for proxy in JiangxianliFetcher().fetch():
        print(proxy)
