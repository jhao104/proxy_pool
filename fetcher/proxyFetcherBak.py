# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcherBak
   Description :   原文件改为自动加载爬虫程序,所以调试中或者失效的程序也会加载,
                    把调试中的程序,或者失效程序,放到这个文件里面.
   Author :        wingser
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcherBak
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import re
from time import sleep

from util.webRequest import WebRequest
from pyquery import PyQuery as pq


class ProxyFetcherBak(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy04():
        """ FreeProxyList https://www.freeproxylists.net/zh/ """
        url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
        tree = WebRequest().get(url, verify=False).tree
        from urllib import parse

        def parse_ip(input_str):
            html_str = parse.unquote(input_str)
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
            return ips[0] if ips else None

        for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
            ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
            port = "".join(tr.xpath('./td[2]/text()')).strip()
            if ip:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        url = 'https://ip.ihuan.me/'
        tree = WebRequest().get(url, verify=False).tree
        hrefs = tree.xpath("//ul[@class='pagination']/li/a/@href")

        for href in hrefs:
            r = WebRequest().get(url + href, timeout=10)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)
            sleep(10)

    @staticmethod
    def freeProxy09(page_count=1):
        """ 免费代理库 """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()


if __name__ == '__main__':
    p = ProxyFetcherBak()
    for _ in p.freeProxy09():
        print(_)




# http://nntime.com/proxy-list-01.htm

