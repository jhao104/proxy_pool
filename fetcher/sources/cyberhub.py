# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     cyberhub.py
   Description :   CyberHub代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 CyberHub 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


def _parseTextProxies(text):
    """从纯文本按行提取 ip:port, 跳过 socks 行(池内只校验 HTTP)"""
    proxies = []
    if not text:
        return proxies
    for line in text.splitlines():
        if "socks" in line.lower():
            continue
        proxies.extend(BaseFetcher.parseProxiesFromText(line))
    return proxies


class CyberHubFetcher(BaseFetcher):
    """CyberHub https://cyber-hub.net/

    enabled=False: 实测 HTTP 200, 但 /proxy/http.txt 返回停放域名跳转页
    (window.location.href="/lander"), 无代理数据
    """

    name = "cyberhub"
    url = "https://cyber-hub.net/"

    # 实测已变成停放域名跳转页, 无代理数据
    enabled = False

    api = "https://cyber-hub.net/proxy/http.txt"

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            proxies = _parseTextProxies(r.text)
        except Exception as e:
            logger.error("ProxyFetch - cyberhub: %s" % e)
            return
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in CyberHubFetcher().fetch():
        print(proxy)
