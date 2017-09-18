# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     SsdbClient.py
   Description :  封装SSDB操作
   Author :       JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
                   2017/04/26: 添加get_status方法获取hash长度
-------------------------------------------------
"""
__author__ = 'JHao'

from Util import EnvUtil

from redis.connection import BlockingConnectionPool
from redis import Redis
import random
import json


class SsdbClient(object):
    """
    SSDB client

    SSDB中代理存放的容器为hash：
        原始代理存放在name为raw_proxy的hash中，key为代理的ip:port，value为None,以后扩展可能会加入代理属性；
        验证后供flask使用的代理存放在name为useful_proxy的hash中，key为代理的ip:port，value为None,以后扩展可能会加入代理属性；

    """

    def __init__(self, name, host, port):
        """
        init
        :param name: hash name
        :param host: ssdb host
        :param port: ssdb port
        :return:
        """
        self.name = name
        self.__conn = Redis(connection_pool=BlockingConnectionPool(host=host, port=port))

    def get(self):
        """
        get an item

        从useful_proxy_queue随机获取一个可用代理, 使用前需要调用changeTable("useful_proxy_queue")
        :return:
        """
        values = self.__conn.hkeys(name=self.name)
        keys = list(values) if EnvUtil.PY3 else values
        return random.choice(keys) if values else None

    def put(self, key):
        """
        put an  item

        将代理放入hash, 使用changeTable指定hash name
        :param key:
        :return:
        """
        key = json.dump(key, ensure_ascii=False) if isinstance(key, (dict, list)) else key
        return self.__conn.hincrby(self.name, key, 1)

    def getvalue(self, key):
        value = self.__conn.hget(self.name, key)
        return value if value else None

    def pop(self):
        """
        pop an item

        弹出一个代理， 使用changeTable指定hash name
        :return:
        """
        key = self.get()
        if key:
            self.__conn.hdel(self.name, key)
        return key

    def delete(self, key):
        """
        Remove the ``key`` from hash ``name``
        :param key:
        :return:
        """
        self.__conn.hdel(self.name, key)

    def inckey(self, key, value):
        self.__conn.hincrby(self.name, key, value)

    def getAll(self):
        keys = self.__conn.hkeys(self.name)
        return list(keys) if EnvUtil.PY3 else keys

    def get_status(self):
        """
        Return the number of elements in hash ``name``
        :return:
        """
        return self.__conn.hlen(self.name)

    def changeTable(self, name):
        self.name = name
