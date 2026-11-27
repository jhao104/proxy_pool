# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     iphai.py
   Description :   IP海代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 IP海 代理源
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
    r'<td>\s*?(\d{1,3}(?:\.\d{1,3}){3})\s*?</td>[\s\S]*?'
    r'<td>\s*?(\d{2,5})\s*?</td>')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class IphaiFetcher(BaseFetcher):
    """IP海 http://www.iphai.com/（页面全部 404，默认禁用）"""

    name = "iphai"
    url = "http://www.iphai.com/"
    enabled = False

    urls = [
        "http://www.iphai.com/free/ng",
        "http://www.iphai.com/free/np",
        "http://www.iphai.com/free/wg",
        "http://www.iphai.com/free/wp",
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
            except Exception as e:
                logger.error("ProxyFetch - iphai: %s" % e)
            if index < len(self.urls) - 1:
                sleep(2)  # 页面之间限速
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in IphaiFetcher().fetch():
        print(proxy)
