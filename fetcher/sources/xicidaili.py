# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     xicidaili.py
   Description :   西刺代理代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 西刺代理 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

IP_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}$')
IP_PORT_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class XicidailiFetcher(BaseFetcher):
    """西刺代理 https://www.xicidaili.com/（返回反爬 JS 跳转页，默认禁用）"""

    name = "xicidaili"
    url = "https://www.xicidaili.com/"
    enabled = False

    urls = [
        "https://www.xicidaili.com/nn/",  # 高匿
        "https://www.xicidaili.com/nt/",  # 透明
    ]

    def fetch(self):
        proxies = []
        for index, url in enumerate(self.urls):
            try:
                r = WebRequest().get(url, timeout=10, retry_time=1)
                tree = r.tree
                if tree is not None:
                    # 表格首行是表头, position()>1 跳过
                    for tr in tree.xpath('.//table[@id="ip_list"]//tr[position()>1]'):
                        row_proxies = self._parse_row(tr)
                        proxies.extend(row_proxies)
                if not proxies:
                    proxies = [p for p in self.parseProxiesFromText(r.text or "")
                               if _is_valid_proxy(p)]
            except Exception as e:
                logger.error("ProxyFetch - xicidaili: %s" % e)
            if index < len(self.urls) - 1:
                sleep(2)  # 页面之间限速
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy

    @staticmethod
    def _parse_row(tr):
        """从表格行中提取 ip:port, 跳过国家/位置等非 IP 单元格"""
        cells = [''.join(td.xpath('.//text()')).strip() for td in tr.xpath('./td')]
        for index, cell in enumerate(cells):
            if not IP_PATTERN.match(cell):
                continue
            if index + 1 >= len(cells):
                continue
            port = cells[index + 1]
            if port.isdigit() and 0 < int(port) < 65536:
                return ["%s:%s" % (cell, port)]
        return []


if __name__ == '__main__':
    for proxy in XicidailiFetcher().fetch():
        print(proxy)
