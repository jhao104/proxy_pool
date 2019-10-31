# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    DbClient.py
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

from Config.ConfigGetter import config
from Util import Singleton

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class DbClient(object):
    """
    DbClient DB工厂类 提供get/put/update/pop/delete/exists/getAll/clean/getNumber/changeTable方法

    目前存放代理的有两种, 使用changeTable方法切换操作对象：
        raw_proxy： 存放原始的代理；
        useful_proxy： 存放检验后的代理；


    抽象方法定义：
        get(proxy): 返回指定proxy的信息;
        put(proxy): 存入一个proxy信息;
        pop(): 返回并删除一个proxy信息;
        update(proxy): 更新指定proxy信息;
        delete(proxy): 删除指定proxy;
        exists(proxy): 判断指定proxy是否存在;
        getAll(): 列表形式返回所有代理;
        clean(): 清除所有proxy信息;
        getNumber(): 返回proxy数据量;
        changeTable(name): 切换操作对象 raw_proxy/useful_proxy


        所有方法需要相应类去具体实现：
            ssdb: SsdbClient.py
            redis: RedisClient.py
            mongodb: MongodbClient.py

    """

    __metaclass__ = Singleton

    def __init__(self):
        """
        init
        :return:
        """
        self.__initDbClient()

    def __initDbClient(self):
        """
        init DB Client
        :return:
        """
        __type = None
        if "SSDB" == config.db_type:
            __type = "SsdbClient"
        elif "REDIS" == config.db_type:
            __type = "RedisClient"
        elif "MONGODB" == config.db_type:
            __type = "MongodbClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(config.db_type)
        self.client = getattr(__import__(__type), __type)(name=config.db_name,
                                                          host=config.db_host,
                                                          port=config.db_port,
                                                          password=config.db_password)

    def get(self, key, **kwargs):
        return self.client.get(key, **kwargs)

    def put(self, key, **kwargs):
        return self.client.put(key, **kwargs)

    def update(self, key, value, **kwargs):
        return self.client.update(key, value, **kwargs)

    def delete(self, key, **kwargs):
        return self.client.delete(key, **kwargs)

    def exists(self, key, **kwargs):
        return self.client.exists(key, **kwargs)

    def pop(self, **kwargs):
        return self.client.pop(**kwargs)

    def getAll(self):
        return self.client.getAll()

    def clear(self):
        return self.client.clear()

    def changeTable(self, name):
        self.client.changeTable(name)

    def getNumber(self):
        return self.client.getNumber()
