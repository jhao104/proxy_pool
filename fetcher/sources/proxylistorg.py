# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxylistorg.py
   Description :   ProxyListOrg代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ProxyListOrg 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import base64
import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyListOrgFetcher(BaseFetcher):
    """
    ProxyListOrg https://proxy-list.org/english/index.php

    注意: 当前环境该站点两次实测均连接超时, 抓不到任何数据, 暂禁用;
    解析逻辑保留, 网络恢复后可直接启用。
    """

    name = "proxylistorg"
    url = "https://proxy-list.org/english/index.php"
    enabled = False

    # 只保留合法的 ip:port, 避免 base64 解出无关内容
    _proxy_pattern = re.compile(
        r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')

    def fetch(self):
        urls = [
            "https://proxy-list.org/english/index.php?p=%s" % n
            for n in range(1, 10)
        ]
        proxies = []
        try:
            for index, url in enumerate(urls):
                if index:
                    sleep(2)  # 有频控, 每页之间休眠
                r = WebRequest().get(url, timeout=10, retry_time=1)
                encoded = re.findall(r"Proxy\('(.*?)'\)", r.text or "")
                for item in encoded:
                    try:
                        decoded = base64.b64decode(item).decode("utf-8").strip()
                    except Exception:
                        continue  # 解码失败跳过该条
                    if self._proxy_pattern.match(decoded):
                        proxies.append(decoded)
        except Exception as e:
            logger.error("ProxyFetch - proxylistorg: %s" % e)
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ProxyListOrgFetcher().fetch():
        print(proxy)
