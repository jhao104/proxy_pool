# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetchScheduler
   Description :
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06:
-------------------------------------------------
"""
__author__ = 'JHao'

from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()

    def fetch(self):
        """
        fetch proxy into db with proxyFetcher
        :return:
        """
        proxy_set = set()
        self.log.info("ProxyFetcher : start")
        for fetch_name in self.conf.fetchers:
            self.log.info("ProxyFetcher - {func}: start".format(func=fetch_name))
            fetcher = getattr(ProxyFetcher, fetch_name, None)
            if not fetcher:
                self.log.error("ProxyFetcher - {func}: class method not exists!")
                continue
            if not callable(fetcher):
                self.log.error("ProxyFetcher - {func}: must be class method")
                continue

            try:
                for proxy in fetcher():
                    proxy = proxy.strip()
                    if not proxy or not verifyProxyFormat(proxy):
                        self.log.error('ProxyFetch - {func}: '
                                       '{proxy} illegal'.format(func=proxyGetter, proxy=proxy.ljust(20)))
                        continue
                    elif proxy in proxy_set:
                        self.log.info('ProxyFetch - {func}: '
                                      '{proxy} exist'.format(func=proxyGetter, proxy=proxy.ljust(20)))
                        continue
                    else:
                        self.log.info('ProxyFetch - {func}: '
                                      '{proxy} success'.format(func=proxyGetter, proxy=proxy.ljust(20)))
                        self.db.put(Proxy(proxy, source=proxyGetter))
                        proxy_set.add(proxy)
            except Exception as e:
                self.log.error("ProxyFetch - {func}: error".format(func=proxyGetter))
                self.log.error(str(e))


if __name__ == '__main__':
    a = callable(getattr(ProxyFetcher, 'freeProxy01'))
    pass
