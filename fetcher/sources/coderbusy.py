# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     coderbusy.py
   Description :   CoderBusy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 CoderBusy 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

IP_PORT_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class CoderBusyFetcher(BaseFetcher):
    """码农代理 https://proxy.coderbusy.com/（站点域名已失效，默认禁用）"""

    name = "coderbusy"
    url = "https://proxy.coderbusy.com/"
    enabled = False

    def fetch(self):
        try:
            r = WebRequest().get(self.url, timeout=10, retry_time=1)
            tree = r.tree
            proxies = []
            if tree is not None:
                for tr in tree.xpath('.//table//tr'):
                    cells = [''.join(td.xpath('.//text()')).strip()
                             for td in tr.xpath('./td')]
                    cells = [cell for cell in cells if cell]
                    if len(cells) < 2:
                        continue
                    proxy = "%s:%s" % (cells[0], cells[1])
                    if _is_valid_proxy(proxy):
                        proxies.append(proxy)
            if not proxies:
                proxies = [p for p in self.parseProxiesFromText(r.text)
                           if _is_valid_proxy(p)]
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - coderbusy: %s" % e)


if __name__ == '__main__':
    for proxy in CoderBusyFetcher().fetch():
        print(proxy)
