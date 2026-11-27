# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fyvri.py
   Description :   Fyvri代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 fyvri 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class FyvriFetcher(BaseFetcher):
    """Fyvri Fresh Proxy List https://github.com/fyvri/fresh-proxy-list

    实测单轮约 24 万条, 存活率仅 0.2%, 会把验证队列打爆, 默认禁用。
    """

    name = "fyvri"
    url = "https://github.com/fyvri/fresh-proxy-list"
    enabled = False

    def fetch(self):
        try:
            url = ("https://raw.githubusercontent.com/fyvri/fresh-proxy-list/"
                   "archive/storage/classic/http.txt")
            r = WebRequest().get(url, timeout=10, retry_time=1)
            for proxy in self.yieldUniqueProxies(self.parseProxiesFromText(r.text)):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - fyvri: %s" % e)


if __name__ == '__main__':
    for proxy in FyvriFetcher().fetch():
        print(proxy)
