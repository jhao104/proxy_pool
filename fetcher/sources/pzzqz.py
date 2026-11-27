# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     pzzqz.py
   Description :   PzzQz代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 PzzQz 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

import requests
from lxml import etree

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler

logger = LogHandler("fetcher")


class PzzqzFetcher(BaseFetcher):
    """PzzQz https://pzzqz.com/

    实测: 域名 pzzqz.com 无法解析(DNS 失败), 站点疑似下线, 暂不启用;
    解析逻辑保留完整实现。
    """

    name = "pzzqz"
    url = "https://pzzqz.com/"

    # 实测域名无法解析, 站点已下线
    enabled = False

    api = "https://pzzqz.com/"

    def fetch(self):
        try:
            session = requests.Session()
            index_resp = session.get(self.api, timeout=10)
            token = re.findall(r'X-CSRFToken": "(.*?)"', index_resp.text or "")
            if not token:
                logger.error("ProxyFetch - pzzqz: csrf token not found")
                return

            payload = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
            proxy_resp = session.post(
                self.api,
                headers={"X-CSRFToken": token[0]},
                json=payload,
                timeout=10)
            data = proxy_resp.json()

            proxies = []
            tree = etree.HTML(data.get("proxy_html", "") or "")
            if tree is not None:
                for tr in tree.xpath("//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    if ip and port:
                        proxies.append("%s:%s" % (ip, port))

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - pzzqz: %s" % e)


if __name__ == '__main__':
    for proxy in PzzqzFetcher().fetch():
        print(proxy)
