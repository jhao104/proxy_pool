# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxydb.py
   Description :   ProxyDB代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ProxyDB 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")


class ProxydbFetcher(BaseFetcher):
    """ProxyDB https://proxydb.net/

    实测: 原 POST /list JSON 接口已返回 404(接口变更), 首页
    https://proxydb.net/?offset=N 仍提供 HTML 表格数据, 因此 POST 失败时
    回退解析首页表格, 保证数据可用。
    """

    name = "proxydb"
    url = "https://proxydb.net/list"

    enabled = True

    api = "https://proxydb.net/list"
    page_url = "https://proxydb.net/?offset=%d"
    page_count = 2

    @staticmethod
    def _isHttpProxy(protocol):
        """只保留 http/https 协议"""
        if not protocol:
            return True
        return "http" in str(protocol).lower()

    def fetch(self):
        """抓取 2 页, 跨页去重"""
        seen = set()
        for index in range(self.page_count):
            for proxy in self.fetchPage(index):
                if proxy not in seen:
                    seen.add(proxy)
                    yield proxy

    def fetchPage(self, index):
        """抓取单页: 优先 POST JSON 接口, 失败回退首页 HTML 表格"""
        try:
            payload = {"protocols": [], "anonlvls": [], "offset": index * 30}
            r = WebRequest().post(self.api, json=payload, timeout=10, retry_time=1)
            data = r.json
            if isinstance(data, dict) and isinstance(data.get("proxies"), list):
                for each in data["proxies"]:
                    ip = each.get("ip")
                    port = each.get("port")
                    if ip and port and self._isHttpProxy(each.get("protocol")):
                        yield "%s:%s" % (ip, port)
                return

            # JSON 接口不可用时回退解析首页 HTML 表格
            for proxy in self.parsePageHtml(index):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - proxydb: %s" % e)

    def parsePageHtml(self, index):
        """解析首页表格: td[1]=ip, td[2]=port(链接文本), td[3]=协议"""
        r = WebRequest().get(self.page_url % (index * 30), timeout=10, retry_time=1)
        tree = r.tree
        if tree is None:
            return
        for tr in tree.xpath("//table//tr"):
            ip = "".join(tr.xpath("./td[1]//text()")).strip()
            port_nodes = tr.xpath("./td[2]//a/text()")
            if port_nodes:
                port = "".join(port_nodes).strip()
            else:
                port = "".join(tr.xpath("./td[2]//text()")).strip()
            protocol = "".join(tr.xpath("./td[3]//text()")).strip()
            if ip and port and self._isHttpProxy(protocol):
                yield "%s:%s" % (ip, port)


if __name__ == '__main__':
    for proxy in ProxydbFetcher().fetch():
        print(proxy)
