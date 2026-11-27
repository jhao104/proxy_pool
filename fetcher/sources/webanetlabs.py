# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     webanetlabs.py
   Description :   Webanetlabs代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 Webanetlabs 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

IP_PORT_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')

TABLE_PROXY_PATTERN = re.compile(
    r'<td.*?>[\s\S]*?(\d{1,3}(?:\.\d{1,3}){3})[\s\S]*?</td>[\s\S]*?'
    r'<td.*?>[\s\S]*?(\d{2,5})[\s\S]*?</td>')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class WebanetlabsFetcher(BaseFetcher):
    """Webanetlabs http://webanetlabs.net/publ/24（列表最后更新于 2023 年, 数据可能陈旧）"""

    name = "webanetlabs"
    url = "http://webanetlabs.net/publ/24"
    enabled = True

    def fetch(self):
        try:
            r = WebRequest().get(self.url, timeout=10, retry_time=1)
            text = r.text or ""
            # 该页把代理以纯文本 "ip:port" 罗列在 <p> 中, 优先按文本提取
            proxies = [p for p in self.parseProxiesFromText(text)
                       if _is_valid_proxy(p)]
            if not proxies:
                # 页面结构变化时回退到通用表格正则
                for ip, port in TABLE_PROXY_PATTERN.findall(text):
                    proxy = "%s:%s" % (ip, port)
                    if _is_valid_proxy(proxy):
                        proxies.append(proxy)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - webanetlabs: %s" % e)


if __name__ == '__main__':
    for proxy in WebanetlabsFetcher().fetch():
        print(proxy)
