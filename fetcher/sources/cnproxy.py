# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     cnproxy.py
   Description :   CnProxy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 cnproxy 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

# 表格中 IP 与端口相邻, 兼容空白与 td 属性
_PROXY_RE = re.compile(
    r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>[\s\S]{0,120}?'
    r'<td[^>]*>\s*(\d{2,5})\s*</td>')


class CnProxyFetcher(BaseFetcher):
    """
    墙外 cn-proxy http://cn-proxy.com/

    实测结论: 首页与 /archives/218 均被对方重置连接(Connection reset),
    站点已无法访问, 故 enabled=False; 保留完整解析逻辑。
    """

    name = "cnproxy"
    url = "http://cn-proxy.com/"
    enabled = False
    request_interval = 2

    def fetch(self):
        urls = [
            "http://cn-proxy.com/",
            "http://cn-proxy.com/archives/218",
        ]
        proxies = []
        for url in urls:
            try:
                r = WebRequest().get(url, timeout=10, retry_time=1)
                for ip, port in _PROXY_RE.findall(r.text or ''):
                    proxies.append("%s:%s" % (ip, port))
            except Exception as e:
                logger.error("ProxyFetch - %s: %s" % (self.name, e))
            sleep(self.request_interval)

        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in CnProxyFetcher().fetch():
        print(proxy)
