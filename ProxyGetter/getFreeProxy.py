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

import json
import requests
import threading

API_URL = "https://www.censys.io/api/v1/search/"
UID = "45bbe9db-87c9-4256-b1f0-0509037f1e84"
SECRET = "DqtxZX43liWHZPY0gNLkorptTCIaAgyu"
KEY_WORD = ['Squid', 'CCProxy', 'Tinyproxy', 'Wingate', 'Pound', 'Proxy', 'Mikrotik']


class GetFreeProxy(object):
    """
    proxy getter
    """

    def __init__(self):
        pass

    @staticmethod
    def scanner_ip():
        for key in KEY_WORD:
            print('Search Key: {key}'.format(key=key))
            t = ThreadScanner(key)
            t.start()


class ThreadScanner(threading.Thread):
    def __init__(self, key):
        super(ThreadScanner, self).__init__()
        self.key = key
        self.query = {'query': self.key, 'page': 1, 'fields': ['ip']}

    def run(self):
        self.scanner_ip()

    def get_total_page(self):
        res = requests.post(API_URL + 'ipv4', data=json.dumps(self.query),
                           auth=(UID, SECRET), timeout=30)
        res_result = res.json()
        total_page = res_result.get('metadata').get('pages', 400)
        return total_page

    def scanner_ip(self):
        total_page = self.get_total_page()
        for page in range(1, total_page):
            self.query.update({'page': page})
            try:
                res = requests.post(API_URL + 'ipv4', data=json.dumps(self.query),
                                    auth=(UID, SECRET), timeout=30)
                res_result = res.json()
                total_page = res_result.get('metadata').get('pages')
                ip_results = res_result.get('results')
            except Exception as e:
                ip_results = list()
            for each_ip in ip_results:
                ip = each_ip.get('ip')
                print(ip)
            if page >= total_page:
                break
            print('Key {k} page: {p}'.format(k=self.key, p=page))


if __name__ == '__main__':
    g = GetFreeProxy()
    g.scanner_ip()