# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     metapool.py
   Description :   MetaPool聚合代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 MetaPool 聚合代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class MetaPoolFetcher(BaseFetcher):
    """MetaPool 聚合接口(抓取其他代理池 /all/)"""

    name = "metapool"
    url = "https://github.com/jhao104/proxy_pool"

    # 聚合类源, 抓取其他代理池, 来源不可控, 默认关闭避免循环抓取
    enabled = False

    target_urls = (
        "http://42.192.20.108:5000/all/",
        "http://117.72.44.211:5010/all/",
        "http://124.221.144.122:5010/all/",
        "http://119.45.214.228:5010/all/",
        "http://106.52.214.84:5010/all/",
        "http://152.69.217.58:5010/all/",
        "http://47.116.207.92:5010/all/",
    )

    def fetch(self):
        """逐个聚合接口抓取, 单个失败不影响其他"""
        proxies = []
        for url in self.target_urls:
            try:
                r = WebRequest().get(url, timeout=10, retry_time=1)
                payload = r.json
                if isinstance(payload, list):
                    for each in payload:
                        if not isinstance(each, dict):
                            continue
                        proxy = each.get("proxy", "")
                        if proxy:
                            proxies.append(proxy)
                else:
                    # 非标准 JSON 响应时退化为文本提取
                    proxies.extend(self.parseProxiesFromText(r.text))
            except Exception as e:
                logger.error("ProxyFetch - metapool: %s" % e)

        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in MetaPoolFetcher().fetch():
        print(proxy)
