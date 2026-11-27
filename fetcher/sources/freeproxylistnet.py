# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freeproxylistnet.py
   Description :   FreeProxyListNet代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 FreeProxyListNet 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class FreeProxyListNetFetcher(BaseFetcher):
    """
    FreeProxyListNet https://free-proxy-list.net/

    注意: 当前环境该站点仅解析到 IPv6 地址且连接失败(两次实测均超时),
    抓不到任何数据, 因此暂时禁用; 解析逻辑保留, 网络恢复后可直接启用。
    """

    name = "freeproxylistnet"
    url = "https://free-proxy-list.net/"
    enabled = False

    def fetch(self):
        try:
            r = WebRequest().get(self.url, timeout=10, retry_time=1)
            proxies = []
            # 优先解析页面内的 raw textarea, 失败则从全文正则提取
            tree = r.tree
            if tree is not None:
                nodes = tree.xpath("//*[@id='raw']/div/div/div[2]/textarea/text()")
                if nodes:
                    proxies = self.parseProxiesFromText("".join(nodes))
            if not proxies:
                proxies = self.parseProxiesFromText(r.text)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - freeproxylistnet: %s" % e)


if __name__ == '__main__':
    for proxy in FreeProxyListNetFetcher().fetch():
        print(proxy)
