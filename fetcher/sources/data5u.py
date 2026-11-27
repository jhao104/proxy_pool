# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     data5u.py
   Description :   无忧代理代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 无忧代理 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

IP_PORT_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class Data5uFetcher(BaseFetcher):
    """无忧代理 http://www.data5u.com/（页面全部 404，默认禁用）"""

    name = "data5u"
    url = "http://www.data5u.com/"
    enabled = False

    urls = [
        "http://www.data5u.com/free/gngn/index.shtml",
        "http://www.data5u.com/free/gnpt/index.shtml",
    ]

    # 端口以 class 名中的字母编码, 字母表对应 0-9
    port_key = 'ABCDEFGHIZ'

    def fetch(self):
        proxies = []
        for index, url in enumerate(self.urls):
            try:
                r = WebRequest().get(url, timeout=10, retry_time=1)
                tree = r.tree
                if tree is not None:
                    for ul in tree.xpath('//ul[@class="l2"]'):
                        proxy = self._parse_ul(ul)
                        if proxy:
                            proxies.append(proxy)
                if not proxies:
                    proxies = [p for p in self.parseProxiesFromText(r.text or "")
                               if _is_valid_proxy(p)]
            except Exception as e:
                logger.error("ProxyFetch - data5u: %s" % e)
            if index < len(self.urls) - 1:
                sleep(2)  # 页面之间限速
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy

    def _parse_ul(self, ul):
        """解析 <ul class="l2"> 中的 ip 与 class 编码端口"""
        try:
            ip_list = ul.xpath('./span[1]/li/text()')
            classnames = ul.xpath('./span[2]/li/attribute::class')
            if not ip_list or not classnames:
                return None
            ip = ip_list[0].strip()
            tokens = [token for token in classnames[0].split() if token != 'port']
            if not tokens:
                return None
            port_sum = 0
            for char in tokens[0]:
                port_sum = port_sum * 10 + self.port_key.index(char)
            proxy = "%s:%d" % (ip, port_sum >> 3)
            return proxy if _is_valid_proxy(proxy) else None
        except Exception as e:
            logger.error("ProxyFetch - data5u: %s" % e)
            return None


if __name__ == '__main__':
    for proxy in Data5uFetcher().fetch():
        print(proxy)
