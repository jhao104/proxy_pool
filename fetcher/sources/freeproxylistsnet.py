# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     freeproxylistsnet.py
   Description :   FreeProxyListsNet代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 freeproxylistsnet 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from urllib import parse

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

_IP_RE = re.compile(r'\d{1,3}(?:\.\d{1,3}){3}')
_PORT_RE = re.compile(r'^\d{2,5}$')


class FreeProxyListsNetFetcher(BaseFetcher):
    """
    FreeProxyLists https://www.freeproxylists.net/zh/

    实测结论: 指定 URL 返回 404(页面标题 "404 Error - Not Found"),
    站点接口已变更, 故 enabled=False; 保留完整解析逻辑。
    """

    name = "freeproxylistsnet"
    url = "https://www.freeproxylists.net/zh/"
    enabled = False

    def fetch(self):
        target_url = ("https://www.freeproxylists.net/zh/"
                      "?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50")
        try:
            r = WebRequest().get(target_url, timeout=10, retry_time=1)
            tree = r.tree
            proxies = []

            if tree is not None:
                rows = tree.xpath("//tr[@class='Odd'] | //tr[@class='Even']")
                for tr in rows:
                    # 第一列 script 中 IP 被 URL 编码, 先 unquote 再提取
                    raw = "".join(tr.xpath("./td[1]//text()")).strip()
                    match = _IP_RE.search(parse.unquote(raw))
                    ip = match.group(0) if match else None
                    port = "".join(tr.xpath("./td[2]//text()")).strip()
                    if not ip or not port or not _PORT_RE.match(port):
                        continue
                    # td[3] 为协议, 过滤 socks
                    proxy_type = "".join(tr.xpath("./td[3]//text()")).strip().lower()
                    if 'socks' in proxy_type:
                        continue
                    proxies.append("%s:%s" % (ip, port))

            # 兜底: 直接从文本中提取 ip:port
            if not proxies:
                proxies = self.parseProxiesFromText(r.text)

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - %s: %s" % (self.name, e))


if __name__ == '__main__':
    for proxy in FreeProxyListsNetFetcher().fetch():
        print(proxy)
