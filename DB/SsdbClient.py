# -*- coding: utf-8 -*-
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

    def get(self, **kwargs):
        """
        get an item from the queue front
        :return:
        """
        value = self.__conn.qfront(name=self.name)
        return value

    def put(self, value, **kwargs):
        """
        put an  item in the back of a queue
        :param value:
        :return:
        """
        value = json.dump(value, ensure_ascii=False).encode('utf-8') if isinstance(value, (dict, list)) else value
        return self.__conn.qpush_back(self.name, value, **kwargs)

    def pop(self, **kwargs):
        """
        pop an item from the queue front
        :return:
        """
        value = self.__conn.qpop_front(self.name)
        return value[0] if value else value
