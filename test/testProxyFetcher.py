# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyFetcher
   Description :
   Author :        JHao
   date：          2020/6/23
-------------------------------------------------
   Change Activity:
                   2020/6/23:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler


def testProxyFetcher():
    conf = ConfigHandler()
    proxy_getter_functions = conf.fetchers
    for proxyGetter in proxy_getter_functions:
        proxy_count = 0
        for proxy in getattr(ProxyFetcher, proxyGetter.strip())():
            if proxy:
                print('{func}: fetch proxy {proxy},proxy_count:{proxy_count}'.format(func=proxyGetter, proxy=proxy,
                                                                                     proxy_count=proxy_count))
                proxy_count += 1


if __name__ == '__main__':
    testProxyFetcher()
