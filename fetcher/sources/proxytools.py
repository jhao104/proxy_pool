# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxytools.py
   Description :   ProxyTools代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ProxyTools 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyToolsFetcher(BaseFetcher):
    """
    ProxyTools https://cn.proxy-tools.com/

    注意: 当前实测页面只给出 IP, 端口在 td[2] 中是“显示端口”按钮,
    真实端口藏于需过验证码的 modal(showPorts)之后, HTML 中没有端口。
    旧实现把端口硬编码成 80 不可信, 这里只解析真实端口、解析不到则跳过。
    由于拿不到端口, 暂时禁用; 若站点改为直接返回端口可直接启用。
    """

    name = "proxytools"
    url = "https://cn.proxy-tools.com/"
    enabled = False

    _ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    def fetch(self):
        urls = ["https://cn.proxy-tools.com/proxy"]
        urls.extend(
            "https://cn.proxy-tools.com/proxy?page=%d" % i
            for i in range(2, 9)
        )
        proxies = []
        try:
            for index, url in enumerate(urls):
                if index:
                    sleep(5)  # 有频控, 每页之间休眠
                r = WebRequest().get(url, timeout=10, retry_time=1)
                tree = r.tree
                if tree is None:
                    continue
                for tr in tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    # 端口必须是真实数字, 不硬编码 80
                    if self._ip_pattern.match(ip) and port.isdigit():
                        proxies.append("%s:%s" % (ip, port))
        except Exception as e:
            logger.error("ProxyFetch - proxytools: %s" % e)
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ProxyToolsFetcher().fetch():
        print(proxy)
