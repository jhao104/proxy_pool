# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyscrape.py
   Description :   ProxyScrape代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ProxyScrape 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyScrapeFetcher(BaseFetcher):
    """ProxyScrape https://proxyscrape.com/

    实测: 当前网络环境连接 api.proxyscrape.com 超时(重试 2 次均失败),
    解析逻辑保留完整实现。
    """

    name = "proxyscrape"
    url = "https://proxyscrape.com/"

    # 实测连接超时, 暂不启用
    enabled = False

    api = ("https://api.proxyscrape.com/v2/?request=displayproxies"
           "&protocol=http&timeout=10000&country=all")

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - proxyscrape: %s" % e)


if __name__ == '__main__':
    for proxy in ProxyScrapeFetcher().fetch():
        print(proxy)
