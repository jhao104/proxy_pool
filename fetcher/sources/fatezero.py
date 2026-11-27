# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fatezero.py
   Description :   FateZero代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 FateZero 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import json

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class FateZeroFetcher(BaseFetcher):
    """FateZero http://proxylist.fatezero.org/

    实测: 域名 proxylist.fatezero.org 无法解析(DNS 失败), 站点疑似下线,
    暂不启用; 解析逻辑保留完整实现。
    """

    name = "fatezero"
    url = "http://proxylist.fatezero.org/"

    # 实测域名无法解析, 站点已下线
    enabled = False

    api = "http://proxylist.fatezero.org/proxy.list"

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            proxies = []
            for line in (r.text or "").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    info = json.loads(line)
                except ValueError:
                    # 空行/坏行跳过
                    continue
                if not isinstance(info, dict):
                    continue
                if info.get("country") != "CN":
                    continue
                host = info.get("host")
                port = info.get("port")
                if host and port:
                    proxies.append("%s:%s" % (host, port))

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - fatezero: %s" % e)


if __name__ == '__main__':
    for proxy in FateZeroFetcher().fetch():
        print(proxy)
