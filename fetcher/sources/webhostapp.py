# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     webhostapp.py
   Description :   WebHostApp代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 WebHostApp 代理源
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


class WebHostAppFetcher(BaseFetcher):
    """WebHostApp https://jffjdjkbfek.000webhostapp.com/

    enabled=False: 实测域名已失效(DNS 无法解析), 且来源可疑(匿名免费空间)
    """

    name = "webhostapp"
    url = "https://jffjdjkbfek.000webhostapp.com/"

    # 域名已失效, 且来源可疑(匿名免费空间), 默认禁用
    enabled = False

    api = "https://jffjdjkbfek.000webhostapp.com/proxy.txt"

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            proxies = _parseTextProxies(r.text)
        except Exception as e:
            logger.error("ProxyFetch - webhostapp: %s" % e)
            return
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in WebHostAppFetcher().fetch():
        print(proxy)
