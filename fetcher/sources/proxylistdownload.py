# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxylistdownload.py
   Description :   Proxy-List.download代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 Proxy-List.download 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyListDownloadFetcher(BaseFetcher):
    """Proxy-List.download https://www.proxy-list.download/

    实测: API 连续 2 次返回 502, 暂不启用; 解析逻辑保留完整实现。
    """

    name = "proxylistdownload"
    url = "https://www.proxy-list.download/"

    # 实测 API 502, 暂不启用
    enabled = False

    api = "https://www.proxy-list.download/api/v1/get?type=http"

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - proxylistdownload: %s" % e)


if __name__ == '__main__':
    for proxy in ProxyListDownloadFetcher().fetch():
        print(proxy)
