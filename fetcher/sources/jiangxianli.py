# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     jiangxianli.py
   Description :   免费代理库代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 jiangxianli 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

_IP_RE = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}$')
_PORT_RE = re.compile(r'^\d{2,5}$')


class JiangxianliFetcher(BaseFetcher):
    """
    免费代理库 http://ip.jiangxianli.com/

    实测结论: 站点连接被对方重置(Connection reset), 已无法访问,
    故 enabled=False; 保留完整解析逻辑。
    """

    name = "jiangxianli"
    url = "http://ip.jiangxianli.com/"
    enabled = False

    def fetch(self):
        url = "http://ip.jiangxianli.com/?country=中国&page=1"
        try:
            r = WebRequest().get(url, timeout=10, retry_time=1)
            tree = r.tree
            if tree is None:
                return

            proxies = []
            for index, tr in enumerate(tree.xpath("//table//tr")):
                if index == 0:
                    continue
                tds = [each.strip() for each in tr.xpath("./td/text()")]
                if len(tds) < 2:
                    continue
                ip, port = tds[0], tds[1]
                if not _IP_RE.match(ip) or not _PORT_RE.match(port):
                    continue
                proxies.append("%s:%s" % (ip, port))

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - %s: %s" % (self.name, e))


if __name__ == '__main__':
    for proxy in JiangxianliFetcher().fetch():
        print(proxy)
