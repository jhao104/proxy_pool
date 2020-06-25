# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
-------------------------------------------------
"""
__author__ = 'JHao'

import random
import json

from ProxyHelper import Proxy
from DB.DbClient import DbClient
from Config.ConfigGetter import config
from Util.LogHandler import LogHandler
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.raw_proxy_queue = 'raw_proxy'
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = 'useful_proxy'

    def fetch(self):
        """
        fetch proxy into db by ProxyGetter
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        proxy_set = set()
        self.log.info("ProxyFetch : start")

        for proxyGetter in config.proxy_getter_functions:
            self.log.info(
                "ProxyFetch - {func}: start".format(func=proxyGetter))
            try:
                for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
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
                        self.db.put(
                            Proxy(proxy, source=proxyGetter))
                        proxy_set.add(proxy)
            except Exception as e:
                self.log.error(
                    "ProxyFetch - {func}: error".format(func=proxyGetter))
                self.log.error(str(e))

    def get(self):
        """
        return a useful proxy
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_list = self.db.getAll()

        if item_list:
            random_choice = random.choice(item_list)

            return Proxy.newProxyFromJson(random_choice)

        return None

    def get_http(self):
        """
        return a http proxy
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_list = self.db.getAll()

        if item_list:
            for _ in item_list:
                random_choice = random.choice(item_list)
                proxy_type = json.loads(random_choice)['proxy'].split("://")[0]

                if proxy_type == 'http':
                    return Proxy.newProxyFromJson(random_choice)

        return None

    def get_socks(self):
        """
        return a useful socks proxy
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_list = self.db.getAll()

        if item_list:
            for _ in item_list:
                random_choice = random.choice(item_list)
                proxy_type = json.loads(random_choice)['proxy'].split("://")[0]

                if proxy_type == 'socks4':
                    return Proxy.newProxyFromJson(random_choice)

        return None

    def delete(self, proxy_str):
        """
        delete proxy from pool
        :param proxy_str:
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        self.db.delete(proxy_str)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_list = self.db.getAll()

        return [Proxy.newProxyFromJson(_) for _ in item_list]

    def getNumber(self):
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()

        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}


if __name__ == '__main__':
    pp = ProxyManager()
    pp.fetch()
