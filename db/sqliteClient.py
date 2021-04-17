#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: jaxon
@Time: 2020-12-18 23:42
"""

import sqlite3


class sqliteClient(object):
    def __init__(self, **kwargs):
        self.name = ""
        kwargs.pop("username")
        self.__conn = sqlite3.connect(**kwargs)
        self.__cursor = self.__conn.cursor()
        
    def get(self, proxy):
        """
        返回一个代理
        :return:
        """
        SQL_QUERY_ONE_DATA = "SELECT * FROM PEOPLE WHERE proxy={}"
        self.__cursor.execute(SQL_QUERY_ONE_DATA.format(proxy))
        # fetchone():查询第一条数据
        # fetchall()：查询所有数据
        # fetchmany(1):查询固定的数量的数据
        proxy = self.__cursor.fetchone()
        if proxy:
            return proxy
        else:
            return False
    
    def put(self, proxy, num=1):
        """
        """
        SQL_INSERT_ONE_DATA = "INSERT INTO PEOPLE(id,name,age) VALUES(3,'xag',23);"
        if self.db[self.name].find_one({'proxy': proxy}):
            return None
        else:
            self.db[self.name].insert({'proxy': proxy, 'num': num})
        return data
    
    def pop(self):
        """
        弹出一个代理
        :return: dict {proxy: value}
        """
        proxies = self.__conn.hkeys(self.name)
        for proxy in proxies:
            proxy_info = self.__conn.hget(self.name, proxy)
            self.__conn.hdel(self.name, proxy)
            return proxy_info
        else:
            return False
    
    def delete(self, proxy_str):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        return self.__conn.hdel(self.name, proxy_str)
    
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
        return self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

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