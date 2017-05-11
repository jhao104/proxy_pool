# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     DbClient.py
   Description :  DB工厂类
   Author :       JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys

from Util.GetConfig import GetConfig
from Util.utilClass import Singleton

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DbClient(object):
    """
    DbClient DB工厂类 提供get/put/pop/delete/getAll/changeTable方法

    目前存放代理的table/collection/hash有两种：
        raw_proxy： 存放原始的代理；
        useful_proxy_queue： 存放检验后的代理；

    抽象方法定义：
        get: 随机返回一个代理；
        put: 放回一个代理；
        getvalue: 返回代理属性（一个计数器）；
        inckey: 修改代理属性计数器的值;
        delete: 删除指定代理；
        getAll: 返回所有代理；
        changeTable: 切换 table or collection or hash;

        所有方法需要相应类去具体实现：
            SSDB：SsdbClient.py
            REDIS:RedisClient.py

    """

    __metaclass__ = Singleton

    def __init__(self):
        """
        init
        :return:
        """
        self.config = GetConfig()
        self.__initDbClient()

    def __initDbClient(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SSDB" == self.config.db_type:
            __type = "SsdbClient"
        elif "REDIS" == self.config.db_type:
            __type = "RedisClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(self.config.db_type)
        self.client = getattr(__import__(__type), __type)(name=self.config.db_name,
                                                          host=self.config.db_host,
                                                          port=self.config.db_port)

    def get(self, **kwargs):
        return self.client.get(**kwargs)

    def put(self, key, **kwargs):
        return self.client.put(key, **kwargs)

    def getvalue(self, key, **kwargs):
        return self.client.getvalue(key, **kwargs)

    def pop(self, **kwargs):
        return self.client.pop(**kwargs)

    def inckey(self, key, value, **kwargs):
        return self.client.inckey(key, value, **kwargs)

    def delete(self, key, **kwargs):
        return self.client.delete(key, **kwargs)

    def getAll(self):
        return self.client.getAll()

    def changeTable(self, name):
        self.client.changeTable(name)

    def get_status(self):
        return self.client.get_status()


if __name__ == "__main__":
    account = DbClient()
    print(account.get())
    account.changeTable('use')
    account.put('ac')
    print(account.get())
