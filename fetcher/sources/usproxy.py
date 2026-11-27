# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     usproxy.py
   Description :   USProxy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 usproxy 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

_ROW_RE = re.compile(
    r'<td[^>]*>\s*(\d{1,3}(?:\.\d{1,3}){3})\s*</td>\s*'
    r'<td[^>]*>\s*(\d{2,5})\s*</td>')
_IP_PORT_RE = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})$')


class UsProxyFetcher(BaseFetcher):
    """
    US Proxy https://www.us-proxy.org/

    实测结论: 站点 DNS 被污染(解析到不可达地址)且多次连接超时,
    无法获取数据, 故 enabled=False; 保留完整解析逻辑。
    """

    name = "usproxy"
    url = "https://www.us-proxy.org/"
    enabled = False

    def fetch(self):
        try:
            r = WebRequest().get(self.url, timeout=10, retry_time=1)
            text = r.text or ''
            proxies = []

            # 优先按 tbody 分段解析
            sections = text.split("<tbody>")
            if len(sections) > 1:
                body = sections[1].split("</tbody>")[0]
                for row in body.split("<tr>"):
                    match = _ROW_RE.search(row)
                    if not match:
                        continue
                    proxy = "%s:%s" % (match.group(1), match.group(2))
                    if _IP_PORT_RE.match(proxy):
                        proxies.append(proxy)

            # 兜底 1: 全文本正则
            if not proxies:
                for ip, port in _ROW_RE.findall(text):
                    proxy = "%s:%s" % (ip, port)
                    if _IP_PORT_RE.match(proxy):
                        proxies.append(proxy)

            # 兜底 2: 纯文本 ip:port
            if not proxies:
                proxies = self.parseProxiesFromText(text)

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - %s: %s" % (self.name, e))


if __name__ == '__main__':
    for proxy in UsProxyFetcher().fetch():
        print(proxy)
