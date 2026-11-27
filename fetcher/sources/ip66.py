# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ip66.py
   Description :   代理66代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增代理66代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class Ip66Fetcher(BaseFetcher):
    """代理66 http://www.66ip.cn/

    实测该站批量提取接口已返回 404, 且首页需要 JS 计算 __jsl_clearance cookie,
    当前默认禁用; 保留解析逻辑, 站点恢复后可直接启用。
    """

    name = "ip66"
    url = "http://www.66ip.cn/"
    enabled = False

    urls = [
        ("http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa="
         "&submit=%CC%E1++%C8%A1&textarea="),
        ("http://www.66ip.cn/nmtq.php?getnum={}&isp=0&anonymoustype=0&"
         "start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip"),
    ]

    def fetch(self, count=100):
        seen = set()
        for url in self.urls:
            try:
                r = WebRequest().get(url.format(count), timeout=10, retry_time=1)
                for proxy in self.parseProxiesFromText(r.text):
                    if proxy not in seen:
                        seen.add(proxy)
                        yield proxy
            except Exception as e:
                logger.error("ProxyFetch - ip66: %s" % e)


if __name__ == '__main__':
    for proxy in Ip66Fetcher().fetch():
        print(proxy)
