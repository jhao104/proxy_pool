# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     baseFetcher.py
   Description :   代理源基类
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

import re


class BaseFetcher(object):
    """代理源基类"""

    # ---- 子类必须声明 ----
    name = ""        # 唯一标识，如 "zdaye"
    url = ""         # 源网站首页 URL

    # ---- 子类可覆盖 ----
    enabled = True   # 是否启用，设为 False 可禁用该源

    def fetch(self):
        """爬取代理，yield "host:port" 字符串"""
        raise NotImplementedError

    @staticmethod
    def parseProxiesFromText(text):
        """从文本中用正则提取 ip:port"""
        if not text:
            return []
        proxy_pattern = re.compile(
            r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?:\s*:\s*|\s+)(\d{2,5})(?!\d)')
        return ["%s:%s" % proxy for proxy in proxy_pattern.findall(text)]

    @staticmethod
    def parseProxiesFromJson(data):
        """从 JSON 结构中递归提取 ip:port"""
        proxies = []
        if isinstance(data, dict):
            proxy = data.get("proxy") or data.get("addr") or data.get("address")
            if proxy:
                proxies.extend(BaseFetcher.parseProxiesFromText(str(proxy)))

            ip = data.get("ip") or data.get("host") or data.get("server")
            port = data.get("port")
            if ip and port:
                proxies.append("%s:%s" % (ip, port))

            parsed_keys = {"proxy", "addr", "address", "ip", "host", "server", "port"}
            for key, value in data.items():
                if key in parsed_keys:
                    continue
                proxies.extend(BaseFetcher.parseProxiesFromJson(value))
        elif isinstance(data, list):
            for item in data:
                proxies.extend(BaseFetcher.parseProxiesFromJson(item))
        elif isinstance(data, str):
            proxies.extend(BaseFetcher.parseProxiesFromText(data))
        return proxies

    @staticmethod
    def parseProxiesFromTree(tree):
        """从 lxml tree 的 table 行中提取 ip:port"""
        proxies = []
        if tree is None:
            return proxies
        for tr in tree.xpath("//tr"):
            cells = [" ".join(td.xpath(".//text()")).strip() for td in tr.xpath("./td")]
            if len(cells) < 2:
                continue
            ip = ""
            port = ""
            for cell in cells:
                ip_match = re.search(r'\d{1,3}(?:\.\d{1,3}){3}', cell)
                port_match = re.search(r'\b\d{2,5}\b', cell)
                if ip_match and not ip:
                    ip = ip_match.group()
                    continue
                if port_match and not port:
                    port = port_match.group()
            if ip and port:
                proxies.append("%s:%s" % (ip, port))
        return proxies

    @staticmethod
    def yieldUniqueProxies(proxies):
        """去重 yield"""
        seen = set()
        for proxy in proxies:
            if proxy not in seen:
                seen.add(proxy)
                yield proxy