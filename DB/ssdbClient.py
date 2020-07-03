# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ssdbClient.py
   Description :   封装SSDB操作
   Author :        JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2:
                   2017/09/22: PY3中 redis-py返回的数据是bytes型
                   2017/09/27: 修改pop()方法 返回{proxy:value}字典
                   2020/07/03: 2.1.0 优化代码结构
-------------------------------------------------
"""
__author__ = 'JHao'

from redis.connection import BlockingConnectionPool
from random import choice
from redis import Redis


class SsdbClient(object):
    """
    SSDB client

    SSDB中代理存放的结构为hash：
    key为代理的ip:por, value为代理属性的字典;
    """

    def __init__(self, **kwargs):
        """
        init
        :param host: host
        :param port: port
        :param password: password
        :return:
        """
        self.name = ""
        kwargs.pop("username")
        self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True, **kwargs))

    def get(self):
        """
        从hash中随机返回一个代理
        :return:
        """
        proxies = self.__conn.hkeys(self.name)
        proxy = choice(proxies) if proxies else None
        if proxy:
            return self.__conn.hget(self.name, proxy)
        else:
            return None

    def put(self, proxy_obj):
        """
        将代理放入hash
        :param proxy_obj: Proxy obj
        :return:
        """
        result = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
        return result

    def pop(self):
        """
        顺序弹出一个代理
        :return: proxy
        """
        proxies = self.__conn.hkeys(self.name)
        for proxy in proxies:
            proxy_info = self.__conn.hget(self.name, proxy)
            self.__conn.hdel(self.name, proxy)
            return proxy_info
        else:
            return None

    def delete(self, proxy_str):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        self.__conn.hdel(self.name, proxy_str)

    def exists(self, proxy_str):
        """
        判断指定代理是否存在, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hexists(self.name, proxy_str)

    def update(self, proxy_obj):
        """
        更新 proxy 属性
        :param proxy_obj:
        :return:
        """
        self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    def getAll(self):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        item_dict = self.__conn.hgetall(self.name)
        return item_dict

    def clear(self):
        """
        清空所有代理, 使用changeTable指定hash name
        :return:
        """
        return self.__conn.delete(self.name)

    def getCount(self):
        """
        返回代理数量
        :return:
        """
        return self.__conn.hlen(self.name)

    def changeTable(self, name):
        """
        切换操作对象
        :param name:
        :return:
        """
        self.name = name
