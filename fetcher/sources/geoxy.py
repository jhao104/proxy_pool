# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     geoxy.py
   Description :   Geoxy代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 Geoxy 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from time import sleep

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class GeoxyFetcher(BaseFetcher):
    """Geoxy https://geoxy.io/

    实测: 带固定 authorization token 请求返回 200 且含 http 代理数据。
    注意 token 可能过期, 过期后接口返回 401/403 或空数据, 需重新抓取 token。
    """

    name = "geoxy"
    url = "https://geoxy.io/"

    enabled = True

    api = "https://geoxy.io/proxies?page=%d&count=50"
    max_page = 16
    request_interval = 1  # 页间隔, 避免触发频控

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'BgPXfhUc8CAhK7wGOqzqz9m77j3sH7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://geoxy.io/',
        'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': ('Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/130.0.0.0 Mobile Safari/537.36'),
    }

    @staticmethod
    def _isHttpProxy(protocols):
        """protocols 为列表, 只保留含 http/https 的条目"""
        if not protocols:
            return False
        for protocol in protocols:
            if "http" in str(protocol).lower():
                return True
        return False

    def fetch(self):
        seen = set()
        for page in range(1, self.max_page + 1):
            if page > 1:
                sleep(self.request_interval)
            url = self.api % page
            try:
                r = WebRequest().get(
                    url, header=self.headers, verify=False,
                    timeout=10, retry_time=1)
                data = r.json
                if not isinstance(data, list) or not data:
                    # 401/403 或空数据: token 可能已过期
                    logger.error("ProxyFetch - geoxy: page %d empty or unauthorized" % page)
                    break
                for each in data:
                    if not isinstance(each, dict):
                        continue
                    if not self._isHttpProxy(each.get("protocols")):
                        continue
                    address = each.get("address")
                    if address and address not in seen:
                        seen.add(address)
                        yield address
            except Exception as e:
                logger.error("ProxyFetch - geoxy: %s" % e)
                break


if __name__ == '__main__':
    for proxy in GeoxyFetcher().fetch():
        print(proxy)
