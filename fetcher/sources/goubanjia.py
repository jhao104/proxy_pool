# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     goubanjia.py
   Description :   狗搬家代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 狗搬家 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

IP_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}$')
IP_PORT_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')


def _is_valid_proxy(proxy):
    """校验 ip:port 字符串格式及端口范围"""
    if not IP_PORT_PATTERN.match(proxy):
        return False
    return 0 < int(proxy.rsplit(':', 1)[1]) < 65536


class GoubanjiaFetcher(BaseFetcher):
    """狗搬家 http://www.goubanjia.com/（页面 404，默认禁用）"""

    name = "goubanjia"
    url = "http://www.goubanjia.com/"
    enabled = False

    def fetch(self):
        try:
            r = WebRequest().get(self.url, timeout=10, retry_time=1)
            tree = r.tree
            proxies = []
            if tree is not None:
                # 此网站会插入 display:none 的干扰数字, 需过滤
                xpath_str = (".//*[not(contains(@style, 'display: none'))"
                             " and not(contains(@style, 'display:none'))"
                             " and not(contains(@class, 'port'))]/text()")
                for td in tree.xpath('//td[@class="ip"]'):
                    proxy = self._parse_td(td, xpath_str)
                    if proxy:
                        proxies.append(proxy)
            # IP 常被 span 混淆, 解析失败时用正则从全文兜底
            if not proxies:
                proxies = [p for p in self.parseProxiesFromText(r.text or "")
                           if _is_valid_proxy(p)]
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - goubanjia: %s" % e)

    @staticmethod
    def _parse_td(td, xpath_str):
        """解析单个 td.ip: 拼接 IP 文本, 端口由 class 字母编码解码"""
        try:
            ip_addr = ''.join(td.xpath(xpath_str))
            ip_addr = re.sub(r'\s+', '', ip_addr).rstrip(':')
            if not IP_PATTERN.match(ip_addr):
                return None
            classnames = td.xpath(".//span[contains(@class, 'port')]/attribute::class")
            if not classnames:
                return None
            port_code = classnames[0].replace('port', '', 1).strip()
            port_sum = 0
            for char in port_code:
                port_sum = port_sum * 10 + (ord(char) - ord('A'))
            proxy = "%s:%d" % (ip_addr, port_sum // 8)
            return proxy if _is_valid_proxy(proxy) else None
        except Exception as e:
            logger.error("ProxyFetch - goubanjia: %s" % e)
            return None


if __name__ == '__main__':
    for proxy in GoubanjiaFetcher().fetch():
        print(proxy)
