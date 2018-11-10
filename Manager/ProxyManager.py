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
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy
from Log.LogManager import log


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.config = GetConfig()
        self.raw_proxy_queue = 'raw_proxy'
        self.useful_proxy_queue = 'useful_proxy'

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        for proxyGetter in self.config.proxy_getter_functions:
            # fetch
            try:
                log.info("Fetch Proxy Start, func:{func}".format(func=proxyGetter))

                total = 0
                succ = 0
                fail = 0
                for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
                    # 挨个存储 proxy，优化raw 队列的 push 速度，进而加快 check proxy 的速度
                    proxy = proxy.strip()
                    if proxy and verifyProxyFormat(proxy):
                        log.debug('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                        self.db.put(proxy)
                        succ = succ + 1
                    else:
                        fail = fail + 1
                        log.error('{func}: fetch proxy {proxy} error'.format(func=proxyGetter, proxy=proxy))

                    total = total + 1
                
                log.info("fetch proxy end, func:{func}, total:{total}, succ:{succ} fail:{fail}".format(func=proxyGetter, total=total, succ=succ, fail=fail))

            except Exception as e:
                log.error("{func}: fetch proxy fail".format(func=proxyGetter))
                continue

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
                item_list = item_dict.keys()

        if item_list:
            item = random.choice(item_list)

        log.debug('Get Random Proxy {item} of {total}'.format(item=item, total=len(item_list)))
        return item
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
