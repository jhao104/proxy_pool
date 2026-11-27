# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     charlespikachu.py
   Description :   CharlesPikachu freeproxy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 CharlesPikachu 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class CharlesPikachuFetcher(BaseFetcher):
    """CharlesPikachu freeproxy https://github.com/CharlesPikachu/freeproxy

    实测: 返回 {"data": [{ip, port, protocol}, ...]}, protocol 可能是
    "Http" / "Https" / "Http, Https" 等组合值。
    """

    name = "charlespikachu"
    url = "https://github.com/CharlesPikachu/freeproxy"

    enabled = True

    api = ("https://raw.githubusercontent.com/CharlesPikachu/"
           "freeproxy/master/proxies.json")

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            payload = r.json
            if not isinstance(payload, dict):
                return
            proxies = []
            for each in payload.get("data", []):
                if not isinstance(each, dict):
                    continue
                protocol = str(each.get("protocol", "")).lower()
                # 只保留 http/https, socks 代理池内无法验证
                if "http" not in protocol:
                    continue
                ip = each.get("ip")
                port = each.get("port")
                if ip and port:
                    proxies.append("%s:%s" % (ip, port))

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - charlespikachu: %s" % e)


if __name__ == '__main__':
    for proxy in CharlesPikachuFetcher().fetch():
        print(proxy)
