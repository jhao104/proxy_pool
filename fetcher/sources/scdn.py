# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     scdn.py
   Description :   SCDN代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

from lxml import etree

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class ScdnFetcher(BaseFetcher):
    """SCDN 代理接口 https://proxy.scdn.io/"""

    name = "scdn"
    url = "https://proxy.scdn.io/"

    def fetch(self):
        url = ("https://proxy.scdn.io/get_proxies.php?"
               "protocol=&country=&per_page=100&page=1")
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        try:
            data = r.json
            proxies = []
            table_html = data.get("table_html") if isinstance(data, dict) else ""
            if table_html:
                tree = etree.HTML("<table>%s</table>" % table_html)
                proxies.extend(self.parseProxiesFromTree(tree))

            if not proxies:
                proxies = self.parseProxiesFromJson(data)
            if not proxies:
                proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            print(e)


if __name__ == '__main__':
    for proxy in ScdnFetcher().fetch():
        print(proxy)
