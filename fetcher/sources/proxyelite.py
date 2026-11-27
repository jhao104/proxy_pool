# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyelite.py
   Description :   ProxyElite代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 proxyelite 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from lxml import etree

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

_AJAX_URL = "https://proxyelite.info/wp-admin/admin-ajax.php"
_NONCE_RE = re.compile(r'"nonce":"([^"]+)"')
_IP_PORT_RE = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})$')


def _parseRows(tree):
    """解析 fpb 表格行, 只保留支持 HTTP/HTTPS 的代理"""
    proxies = []
    if tree is None:
        return proxies
    for tr in tree.xpath("//tr[@data-ix]"):
        protocols = (tr.get("data-protos") or "").lower()
        # data-protos 形如 "HTTP|SOCKS4|SOCKS5", 没有 http 的整行跳过
        if "http" not in protocols:
            continue
        ips = tr.xpath(".//*[@data-ip]/@data-ip")
        ports = tr.xpath(".//*[@data-port]/@data-port")
        if not ips or not ports:
            continue
        ip = ips[0].strip()
        port = ports[0].strip()
        if _IP_PORT_RE.match("%s:%s" % (ip, port)):
            proxies.append("%s:%s" % (ip, port))
    return proxies


def _parseRowsFromHtml(html):
    """解析 AJAX 返回的 rows 片段"""
    if not html:
        return []
    try:
        return _parseRows(etree.HTML(html))
    except Exception:
        return []


class ProxyEliteFetcher(BaseFetcher):
    """
    ProxyElite https://proxyelite.info/free-proxy-list/

    实测结论: 首页返回 200 且包含可解析代理行(可用); 先从首页提取 nonce,
    再 POST admin-ajax.php 的 proxylister_load_more 接口(当前返回空 rows),
    因此以首页服务端渲染的表格为准, POST 结果作为补充。
    """

    name = "proxyelite"
    url = "https://proxyelite.info/free-proxy-list/"
    enabled = True

    def fetch(self):
        request = WebRequest()
        proxies = []
        try:
            r = request.get(self.url, timeout=10, retry_time=1)
            tree = r.tree
            proxies.extend(_parseRows(tree))

            # 新版站点 nonce 需从首页获取; 接口不可用时忽略
            match = _NONCE_RE.search(r.text or "")
            if match:
                data = {
                    'action': 'proxylister_load_more',
                    'nonce': match.group(1),
                    'page': '1',
                    'atts[downloads]': 'true',
                }
                try:
                    resp = request.post(_AJAX_URL, data=data,
                                        timeout=10, retry_time=1)
                    payload = resp.json
                    rows = ''
                    if isinstance(payload, dict):
                        rows = (payload.get('data') or {}).get('rows') or ''
                    proxies.extend(_parseRowsFromHtml(rows))
                except Exception as e:
                    logger.error("ProxyFetch - %s: %s" % (self.name, e))
        except Exception as e:
            logger.error("ProxyFetch - %s: %s" % (self.name, e))

        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in ProxyEliteFetcher().fetch():
        print(proxy)
