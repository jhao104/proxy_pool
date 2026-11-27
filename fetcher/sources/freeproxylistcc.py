# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freeproxylistcc.py
   Description :   FreeProxyListCc代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 FreeProxyListCc 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class FreeProxyListCcFetcher(BaseFetcher):
    """
    FreeProxyListCc https://freeproxylist.cc/

    注意: 当前实测页面返回 200, 但代理数据由 JS(/static/js/fpl20620.js)
    在浏览器端渲染, HTML 中只有表头、没有代理行, 因此暂时禁用;
    解析逻辑保留, 若站点改为服务端渲染可直接启用。
    """

    name = "freeproxylistcc"
    url = "https://freeproxylist.cc/"
    enabled = False

    def fetch(self):
        urls = [
            "https://freeproxylist.cc/servers/%d.html" % i
            for i in range(1, 4)
        ]
        proxies = []
        try:
            for index, url in enumerate(urls):
                if index:
                    sleep(5)  # 有频控, 每页之间休眠
                r = WebRequest().get(url, timeout=10, retry_time=1)
                found = re.findall(
                    r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
                    r.text or "")
                proxies.extend(":".join(each) for each in found)
        except Exception as e:
            logger.error("ProxyFetch - freeproxylistcc: %s" % e)
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in FreeProxyListCcFetcher().fetch():
        print(proxy)
