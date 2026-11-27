# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     qydaili.py
   Description :   齐云代理(qydaili)代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 齐云代理(qydaili) 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class QydailiFetcher(BaseFetcher):
    """
    齐云代理 http://www.qydaili.com/free/?action=china&page=1

    注意: 当前环境域名 www.qydaili.com 已无法解析(DNS 失败),
    抓不到任何数据, 暂时禁用; 解析逻辑保留。
    """

    name = "qydaili"
    url = "http://www.qydaili.com/free/?action=china&page=1"
    enabled = False

    def fetch(self):
        urls = [
            "http://www.qydaili.com/free/?action=china&page=%d" % i
            for i in range(1, 3)
        ]
        proxies = []
        try:
            for index, url in enumerate(urls):
                if index:
                    sleep(2)  # 每页之间休眠
                r = WebRequest().get(url, timeout=10, retry_time=1)
                found = re.findall(
                    r'<td.*?>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td.*?>(\d+)</td>',
                    r.text or "")
                proxies.extend(":".join(each) for each in found)
        except Exception as e:
            logger.error("ProxyFetch - qydaili: %s" % e)
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in QydailiFetcher().fetch():
        print(proxy)
