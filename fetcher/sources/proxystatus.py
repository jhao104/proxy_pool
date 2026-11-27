# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxystatus.py
   Description :   ProxyStatus聚合代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ProxyStatus 聚合代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxyStatusFetcher(BaseFetcher):
    """ProxyStatus 聚合接口(抓取其他代理池 /proxies_status)"""

    name = "proxystatus"
    url = "https://github.com/jhao104/proxy_pool"

    # 聚合类源, 抓取其他代理池, 来源不可控, 默认关闭避免循环抓取
    enabled = False

    target_urls = (
        "https://106.14.14.210/proxies_status",
        "http://47.243.63.109:5000/proxies_status",
        "http://142.171.31.40:5010/proxies_status",
    )

    def fetch(self):
        """逐个接口抓取, 只保留 HTTP/HTTPS, 单个失败不影响其他"""
        proxies = []
        for url in self.target_urls:
            try:
                # IP 直连的 HTTPS 证书通常不匹配, 关闭校验
                r = WebRequest().get(url, timeout=10, retry_time=1, verify=False)
                payload = r.json
                items = payload.get("proxies", []) if isinstance(payload, dict) else []
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    # 池内验证只走 HTTP, socks 一律过滤
                    protocol = str(item.get("protocol", "")).upper()
                    if protocol not in ("HTTP", "HTTPS"):
                        continue
                    ip = item.get("ip", "")
                    port = item.get("port", "")
                    if ip and port:
                        proxies.append("%s:%s" % (ip, port))
            except Exception as e:
                logger.error("ProxyFetch - proxystatus: %s" % e)

        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ProxyStatusFetcher().fetch():
        print(proxy)
