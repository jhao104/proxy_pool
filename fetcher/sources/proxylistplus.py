# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxylistplus.py
   Description :   ProxyListPlus代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ProxyListPlus 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyListPlusFetcher(BaseFetcher):
    """ProxyListPlus https://list.proxylistplus.com/"""

    name = "proxylistplus"
    url = "https://list.proxylistplus.com/"

    def fetch(self):
        urls = [
            "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1",
            "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-2",
        ]
        proxies = []
        try:
            for index, url in enumerate(urls):
                if index:
                    sleep(2)  # 两页之间必须间隔, 否则第二页取不到数据
                r = WebRequest().get(url, timeout=10, retry_time=1)
                found = re.findall(
                    r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
                    r.text or "")
                proxies.extend(":".join(each) for each in found)
        except Exception as e:
            logger.error("ProxyFetch - proxylistplus: %s" % e)
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ProxyListPlusFetcher().fetch():
        print(proxy)
