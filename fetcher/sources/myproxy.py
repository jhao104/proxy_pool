# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     myproxy.py
   Description :   My-Proxy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 My-Proxy 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


def _isValidProxy(ip, port):
    """校验 IPv4 与端口范围, 过滤表格中误匹配的数字"""
    try:
        octets = [int(part) for part in ip.split(".")]
        port = int(port)
    except (TypeError, ValueError):
        return False
    return (len(octets) == 4 and all(0 <= octet <= 255 for octet in octets)
            and 0 < port <= 65535)


def _parseTableProxies(text):
    """通用表格解析: 每行取第一个 IP 单元格及紧随其后的端口单元格"""
    proxies = []
    if not text:
        return proxies
    for row in re.findall(r'<tr\b[^>]*>([\s\S]*?)</tr>', text, re.I):
        cells = re.findall(r'<t[dh]\b[^>]*>([\s\S]*?)</t[dh]>', row, re.I)
        for index, cell in enumerate(cells):
            plain = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', cell)).strip()
            ip_match = re.search(
                r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?![\d.])', plain)
            if not ip_match:
                continue
            ip = ip_match.group(1)
            port = None
            port_match = re.search(r':\s*(\d{2,5})(?!\d)', plain)
            if port_match:
                port = port_match.group(1)
            elif index + 1 < len(cells):
                next_plain = re.sub(
                    r'\s+', ' ', re.sub(r'<[^>]+>', ' ', cells[index + 1])).strip()
                next_match = re.search(r'(?<!\d)(\d{2,5})(?!\d)', next_plain)
                if next_match:
                    port = next_match.group(1)
            if port and _isValidProxy(ip, port):
                proxies.append("%s:%s" % (ip, port))
            break
    return proxies


def _parseTextProxies(text):
    """从纯文本按行提取 ip:port, 跳过 socks 行(池内只校验 HTTP)"""
    proxies = []
    if not text:
        return proxies
    for line in text.splitlines():
        if "socks" in line.lower():
            continue
        proxies.extend(BaseFetcher.parseProxiesFromText(line))
    return proxies


class MyProxyFetcher(BaseFetcher):
    """My-Proxy https://www.my-proxy.com/

    enabled=False: 实测所有列表页连接超时, 站点无法访问
    """

    name = "myproxy"
    url = "https://www.my-proxy.com/"

    # 实测连接超时, 站点无法访问
    enabled = False

    urls = (
        "https://www.my-proxy.com/free-proxy-list.html",
        "https://www.my-proxy.com/free-elite-proxy.html",
        "https://www.my-proxy.com/free-anonymous-proxy.html",
        "https://www.my-proxy.com/free-transparent-proxy.html",
    )

    def fetch(self):
        proxies = []
        for index, page_url in enumerate(self.urls):
            if index:
                sleep(2)  # 页面之间休眠, 避免触发源站频控
            try:
                r = WebRequest().get(page_url, timeout=10, retry_time=1)
                proxies.extend(_parseTableProxies(r.text))
                proxies.extend(_parseTextProxies(r.text))
            except Exception as e:
                logger.error("ProxyFetch - myproxy: %s" % e)
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in MyProxyFetcher().fetch():
        print(proxy)
