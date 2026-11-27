# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ihuan_today.py
   Description :   小幻代理今日代理代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增小幻代理今日代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from lxml import etree
import requests

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class IhuanTodayFetcher(BaseFetcher):
    """小幻代理今日代理 https://ip.ihuan.me/today.html"""

    name = "ihuan_today"
    url = "https://ip.ihuan.me/today.html"

    # 实测可拿到数据
    enabled = True

    home_url = "https://ip.ihuan.me/"

    def fetch(self):
        try:
            session = requests.session()
            headers = WebRequest().header
            # 先请求首页拿到 cookie, 再请求今日代理页
            session.get(self.home_url, headers=headers, timeout=10, verify=False)
            res = session.get(self.url, headers=headers, timeout=10, verify=False)
            tree = etree.HTML(res.text) if res.text else None
            if tree is None:
                return

            proxies = []
            for item in tree.xpath("//table[@class='table table-hover table-bordered']//tr"):
                ip = "".join(item.xpath("./td[1]//text()")).strip()
                port = "".join(item.xpath("./td[2]//text()")).strip()
                if ip and port:
                    proxies.append("%s:%s" % (ip, port))

            if not proxies:
                # 新版 today.html 为按小时页面索引, 代理以纯文本列在小时页中
                hrefs = tree.xpath("//div[contains(@class, 'bs-callout')]/a/@href")
                if hrefs:
                    page = session.get(self.home_url.rstrip("/") + hrefs[0],
                                       headers=headers, timeout=10, verify=False)
                    proxies = self.parseProxiesFromText(page.text)

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - ihuan_today: %s" % e)


if __name__ == '__main__':
    for proxy in IhuanTodayFetcher().fetch():
        print(proxy)
