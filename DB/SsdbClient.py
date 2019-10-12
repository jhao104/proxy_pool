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
                   2017/09/22: PY3中 redis-py返回的数据是bytes型
                   2017/09/27: 修改pop()方法 返回{proxy:value}字典
-------------------------------------------------
"""
__author__ = 'JHao'

from Config.setting import PY3

from redis.connection import BlockingConnectionPool
from redis import Redis


class SsdbClient(object):
    """
    SSDB client

    SSDB中代理存放的结构为hash：
        原始代理存放在name为raw_proxy的hash中, key为代理的ip:por, value为代理属性的字典;
        验证后的代理存放在name为useful_proxy的hash中, key为代理的ip:port, value为代理属性的字典;

    """
    def __init__(self, name, **kwargs):
        """
        init
        :param name: hash name
        :param host: host
        :param port: port
        :param password: password
        :return:
        """
        self.name = name
        self.__conn = Redis(connection_pool=BlockingConnectionPool(**kwargs))

    def get(self, proxy_str):
        """
        从hash中获取对应的proxy, 使用前需要调用changeTable()
        :param proxy_str: proxy str
        :return:
        """
        data = self.__conn.hget(name=self.name, key=proxy_str)
        if data:
            return data.decode('utf-8') if PY3 else data
        else:
            return None

    def put(self, proxy_obj):
        """
        将代理放入hash, 使用changeTable指定hash name
        :param proxy_obj: Proxy obj
        :return:
        """
        data = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.info_json)
        return data

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
        self.__conn.hset(self.name,  proxy_obj.proxy, proxy_obj.info_json)

    def pop(self):
        """
        弹出一个代理
        :return: dict {proxy: value}
        """
        # proxies = self.__conn.hkeys(self.name)
        # if proxies:
        #     proxy = random.choice(proxies)
        #     value = self.__conn.hget(self.name, proxy)
        #     self.delete(proxy)
        #     return {'proxy': proxy.decode('utf-8') if PY3 else proxy,
        #             'value': value.decode('utf-8') if PY3 and value else value}
        return None

    def getAll(self):
        """
        列表形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        item_dict = self.__conn.hgetall(self.name)
        if PY3:
            return [value.decode('utf8') for key, value in item_dict.items()]
        else:
            return item_dict.values()

    def clear(self):
        """
        清空所有代理, 使用changeTable指定hash name
        :return:
        """
        return self.__conn.execute_command("hclear", self.name)

    def getNumber(self):
        """
        返回代理数量
        :return:
        """
        return self.__conn.hlen(self.name)

    def changeTable(self, name):
        """
        切换操作对象
        :param name: raw_proxy/useful_proxy
        :return:
        """
        self.name = name
