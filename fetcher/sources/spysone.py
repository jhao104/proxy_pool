# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     spysone.py
   Description :   Spys.one代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 Spys.one 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

IP_PORT_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')

TABLE_PROXY_PATTERN = re.compile(
    r'<td.*?>[\s\S]*?(\d{1,3}(?:\.\d{1,3}){3})[\s\S]*?</td>[\s\S]*?'
    r'<td.*?>[\s\S]*?(\d{2,5})[\s\S]*?</td>')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class SpysOneFetcher(BaseFetcher):
    """Spys.one http://spys.one/en/http-proxy-list/（连接超时，默认禁用）"""

    name = "spysone"
    url = "http://spys.one/en/http-proxy-list/"
    enabled = False

    urls = [
        "http://spys.one/en/http-proxy-list/",
        "http://spys.one/en/https-ssl-proxy",
    ]

    def fetch(self):
        proxies = []
        for index, url in enumerate(self.urls):
            try:
                r = WebRequest().get(url, timeout=10, retry_time=1)
                for ip, port in TABLE_PROXY_PATTERN.findall(r.text or ""):
                    proxy = "%s:%s" % (ip, port)
                    if _is_valid_proxy(proxy):
                        proxies.append(proxy)
                if not proxies:
                    proxies = [p for p in self.parseProxiesFromText(r.text or "")
                               if _is_valid_proxy(p)]
            except Exception as e:
                logger.error("ProxyFetch - spysone: %s" % e)
            if index < len(self.urls) - 1:
                sleep(2)  # 页面之间限速
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in SpysOneFetcher().fetch():
        print(proxy)
