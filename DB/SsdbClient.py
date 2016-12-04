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
-------------------------------------------------
"""
__author__ = 'JHao'

from ssdb.connection import BlockingConnectionPool
from ssdb import SSDB
import random
import json


class SsdbClient(object):
    """
    SSDB client
    """

    def __init__(self, name, host, port):
        """
        init
        :param name:
        :param host:
        :param port:
        :return:
        """
        self.name = name
        self.__conn = SSDB(connection_pool=BlockingConnectionPool(host=host, port=port))

    def get(self):
        """
        get an item
        :return:
        """
        values = self.__conn.hgetall(name=self.name)
        return random.choice(values.keys()) if values else None

    def put(self, value):
        """
        put an  item
        :param value:
        :return:
        """
        value = json.dump(value, ensure_ascii=False).encode('utf-8') if isinstance(value, (dict, list)) else value
        return self.__conn.hset(self.name, value, None)

    def pop(self):
        """
        pop an item
        :return:
        """
        key = self.get()
        if key:
            self.__conn.hdel(self.name, key)
        return key

    def delete(self, key):
        """
        delete an item
        :param key:
        :return:
        """
        self.__conn.hdel(self.name, key)

    def getAll(self):
        return self.__conn.hgetall(self.name).keys()

    def changeTable(self, name):
        self.name = name
