# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     parserpp.py
   Description :   parserpp代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 parserpp 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import json

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ParserppFetcher(BaseFetcher):
    """parserpp ip_ports https://github.com/parserpp/ip_ports

    实测: 数据源返回 JSONL(每行一个 JSON 对象, 字段 type/host/port),
    并非任务描述的 {分类名: [...]} 结构, 因此两种格式都兼容。
    """

    name = "parserpp"
    url = "https://github.com/parserpp/ip_ports"

    enabled = True

    api = "https://raw.githubusercontent.com/parserpp/ip_ports/main/proxyinfo.json"

    @staticmethod
    def _isHttpProxy(item):
        """只保留 http/https 代理; 无协议字段的条目默认保留"""
        protocol = item.get("protocol") or item.get("type") or ""
        if not protocol:
            return True
        return "http" in str(protocol).lower()

    def fetch(self):
        try:
            r = WebRequest().get(self.api, timeout=10, retry_time=1)
            items = []
            payload = r.json
            if isinstance(payload, dict) and payload:
                # {分类名: [{host, port, protocol?}, ...]}
                for value in payload.values():
                    if isinstance(value, list):
                        items.extend(value)
                    elif isinstance(value, dict):
                        items.append(value)
            else:
                # 实测为 JSONL, WebRequest().json 解析失败返回 {}, 改为逐行解析
                for line in (r.text or "").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(obj, dict):
                        items.append(obj)

            proxies = []
            for item in items:
                if not isinstance(item, dict) or not self._isHttpProxy(item):
                    continue
                host = item.get("host") or item.get("ip")
                port = item.get("port")
                if host and port:
                    proxies.append("%s:%s" % (host, port))

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - parserpp: %s" % e)


if __name__ == '__main__':
    for proxy in ParserppFetcher().fetch():
        print(proxy)
