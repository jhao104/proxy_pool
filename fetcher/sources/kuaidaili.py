# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     kuaidaili.py
   Description :   快代理代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

from time import sleep

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class KuaidailiFetcher(BaseFetcher):
    """快代理 https://www.kuaidaili.com"""

    name = "kuaidaili"
    url = "https://www.kuaidaili.com"

    def fetch(self, page_count=1):
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/',
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])


if __name__ == '__main__':
    for proxy in KuaidailiFetcher().fetch():
        print(proxy)
