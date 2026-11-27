# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     aliveproxy.py
   Description :   AliveProxy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 AliveProxy 代理源
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


class AliveProxyFetcher(BaseFetcher):
    """AliveProxy http://www.aliveproxy.com/（域名已停放/连接超时，默认禁用）"""

    name = "aliveproxy"
    url = "http://www.aliveproxy.com/"
    enabled = False

    urls = [
        "http://www.aliveproxy.com/high-anonymity-proxy-list/",
        "http://www.aliveproxy.com/anonymous-proxy-list/",
        "http://www.aliveproxy.com/fastest-proxies/",
        "http://www.aliveproxy.com/us-proxy-list/",
        "http://www.aliveproxy.com/gb-proxy-list/",
        "http://www.aliveproxy.com/fr-proxy-list/",
        "http://www.aliveproxy.com/de-proxy-list/",
        "http://www.aliveproxy.com/jp-proxy-list/",
        "http://www.aliveproxy.com/ca-proxy-list/",
        "http://www.aliveproxy.com/ru-proxy-list/",
        "http://www.aliveproxy.com/proxy-list-port-80/",
        "http://www.aliveproxy.com/proxy-list-port-81/",
        "http://www.aliveproxy.com/proxy-list-port-3128/",
        "http://www.aliveproxy.com/proxy-list-port-8000/",
        "http://www.aliveproxy.com/proxy-list-port-8080/",
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
                # 单个 URL 失败不影响其他 URL
                logger.error("ProxyFetch - aliveproxy: %s" % e)
            if index < len(self.urls) - 1:
                sleep(2)  # 页面之间限速
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in AliveProxyFetcher().fetch():
        print(proxy)
