# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ihuan.py
   Description :   小幻代理代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class IhuanFetcher(BaseFetcher):
    """小幻代理 https://ip.ihuan.me/"""

    name = "ihuan"
    url = "https://ip.ihuan.me/"

    def fetch(self):
        request = WebRequest()
        ti_url = "https://ip.ihuan.me/ti.html"
        tqdl_url = "https://ip.ihuan.me/tqdl.html"
        ti_resp = request.get(ti_url, timeout=10, verify=False)
        form_data = {}
        if ti_resp.tree is not None:
            for input_tag in ti_resp.tree.xpath("//form//input[@name]"):
                name = "".join(input_tag.xpath("./@name")).strip()
                value = "".join(input_tag.xpath("./@value")).strip()
                if name:
                    form_data[name] = value

        key = form_data.get("key")
        if not key:
            key_match = re.search(
                r'name=["\']key["\'][^>]*value=["\']([^"\']+)', ti_resp.text)
            if not key_match:
                key_match = re.search(
                    r'key["\']?\s*[:=]\s*["\']([0-9a-f]{16,})', ti_resp.text)
            key = key_match.group(1) if key_match else ""

        if not key:
            return

        header = {
            "Origin": "https://ip.ihuan.me",
            "Referer": ti_url,
        }
        data = form_data.copy()
        data.update({
            "num": "2000",
            "port": "",
            "kill_port": "",
            "address": "",
            "kill_address": "",
            "anonymity": "",
            "type": "",
            "post": "",
            "sort": "1",
            "key": key,
        })
        r = request.post(tqdl_url, header=header, data=data, timeout=10, verify=False)
        proxies = self.parseProxiesFromTree(r.tree)
        proxies.extend(self.parseProxiesFromText(r.text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in IhuanFetcher().fetch():
        print(proxy)
