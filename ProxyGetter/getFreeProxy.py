# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  通过关键字扫描censys.io中的疑似ip
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2017/06/15: 通过关键字扫描censys.io中的疑似ip
-------------------------------------------------
"""

from lxml import etree
import requests
import threading

API_URL = "https://www.censys.io/ipv4/_search?q={k}&page={p}"
header = {
    'Host': 'www.censys.io',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Referer': 'https://www.censys.io/',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8'
}

KEY_WORD = ['Squid', 'CCProxy', 'Tinyproxy', 'Wingate', 'Pound', 'Proxy', 'Mikrotik']


class GetFreeProxy(object):
    """
    proxy getter
    """

    def __init__(self):
        pass

    def scanner_ip(self):
        """
        根据关键字搜索ip
        :return:
        """
        for key in KEY_WORD:
            for page in range(1, 200):
                url = API_URL.format(k=key, p=page)
                try:
                    res = requests.get(url, headers=header, timeout=30, )
                    if res.status_code != 200:
                        break
                    tree = etree.HTML(res.content)
                    ip_list_el = tree.xpath('//span[@class="ip"]/a/text()')
                    ip_list = [each.strip() for each in ip_list_el if each.strip()]
                    for each in ip_list:
                        yield each
                except Exception as e:
                    print(e)
                print('Key {k} page: {p}'.format(k=key, p=page))


class ThreadScanner(threading.Thread):
    def __init__(self, key):
        super(ThreadScanner, self).__init__()
        self.key = key
        self.query = {'query': self.key, 'page': 1, 'fields': ['ip']}

    def run(self):
        self.scanner_ip()

    def scanner_ip(self):
        for page in range(1, 200):
            url = API_URL.format(k=self.key, p=page)
            try:
                res = requests.get(url, headers=header, timeout=30, proxies={'https': 'https://106.75.87.49:53100'})
                if res.status_code == 429:
                    break
                tree = etree.HTML(res.content)
                ip_list_el = tree.xpath('//span[@class="ip"]/a/text()')
                ip_list = [each.strip() for each in ip_list_el if each.strip()]
                for each in ip_list:
                    print(each)
            except Exception as e:
                print(e)
            print('Key {k} page: {p}'.format(k=self.key, p=page))


if __name__ == '__main__':
    g = GetFreeProxy()
    for each in g.scanner_ip():
        print(each)
