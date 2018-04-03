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

from Util import EnvUtil
from DB.DbClient import DbClient
from Util.GetConfig import GetConfig
from Util.LogHandler import LogHandler
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.config = GetConfig()
        self.raw_proxy_queue = 'raw_proxy'
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = 'useful_proxy'

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        for proxyGetter in self.config.proxy_getter_functions:
            # fetch
            proxy_set = set()
            try:
                self.log.info("{func}: fetch proxy start".format(func=proxyGetter))
                proxy_iter = [_ for _ in getattr(GetFreeProxy, proxyGetter.strip())()]
            except Exception as e:
                self.log.error("{func}: fetch proxy fail".format(func=proxyGetter))
                continue
            for proxy in proxy_iter:
                proxy = proxy.strip()
                if proxy and verifyProxyFormat(proxy):
                    self.log.info('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                    proxy_set.add(proxy)
                else:
                    self.log.error('{func}: fetch proxy {proxy} error'.format(func=proxyGetter, proxy=proxy))

            # store
            for proxy in proxy_set:
                self.db.changeTable(self.useful_proxy_queue)
                if self.db.exists(proxy):
                    continue
                self.db.changeTable(self.raw_proxy_queue)
                self.db.put(proxy)

    def get(self):
        """
        return a useful proxy
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if item_dict:
            if EnvUtil.PY3:
                return random.choice(list(item_dict.keys()))
            else:
                return random.choice(item_dict.keys())
        return None
        # return self.db.pop()

    def delete(self, proxy):
        """
        delete proxy from pool
        :param proxy:
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        self.db.delete(proxy)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def getNumber(self):
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()
        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}


if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
