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
                   2021/05/26: 区分http和https代理
                   2026/11/14: 新增按来源采集统计的读写
-------------------------------------------------
"""
__author__ = 'JHao'
from redis.exceptions import TimeoutError, ConnectionError, ResponseError
from redis.connection import BlockingConnectionPool
from handler.logHandler import LogHandler
from random import choice
from redis import Redis
import json


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
        self.__conn = Redis(connection_pool=BlockingConnectionPool(decode_responses=True,
                                                                   timeout=5,
                                                                   socket_timeout=5,
                                                                   protocol=2,
                                                                   **kwargs))

    def get(self, https):
        """
        从hash中随机返回一个代理
        :return:
        """
        if https:
            items_dict = self.__conn.hgetall(self.name)
            proxies = list(filter(lambda x: json.loads(x).get("https"), items_dict.values()))
            return choice(proxies) if proxies else None
        else:
            proxies = self.__conn.hkeys(self.name)
            proxy = choice(proxies) if proxies else None
            return self.__conn.hget(self.name, proxy) if proxy else None

    def put(self, proxy_obj):
        """
        将代理放入hash
        :param proxy_obj: Proxy obj
        :return:
        """
        result = self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)
        return result

    def pop(self, https):
        """
        顺序弹出一个代理
        :return: proxy
        """
        proxy = self.get(https)
        if proxy:
            self.__conn.hdel(self.name, json.loads(proxy).get("proxy", ""))
        return proxy if proxy else None

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

    def getAll(self, https):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        item_dict = self.__conn.hgetall(self.name)
        if https:
            return list(filter(lambda x: json.loads(x).get("https"), item_dict.values()))
        else:
            return item_dict.values()

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
        proxies = self.getAll(https=False)
        return {'total': len(proxies), 'https': len(list(filter(lambda x: json.loads(x).get("https"), proxies)))}

    def changeTable(self, name):
        """
        切换操作对象
        :param name:
        :return:
        """
        self.name = name

    def putSourceStat(self, stat_dict):
        """
        保存各源采集统计, 存放在独立hash: <TABLE_NAME>:source_stat
        :param stat_dict: {source: {fetched, valid, last_fetch_time}}
        :return:
        """
        if not stat_dict:
            return
        stat_key = "%s:source_stat" % self.name
        # SSDB 经 redis 协议兼容层, 逐条写入避免不支持 mapping 批量参数
        for source, stat in stat_dict.items():
            self.__conn.hset(stat_key, source, json.dumps(stat, ensure_ascii=False))

    def getSourceStat(self):
        """
        读取各源采集统计
        :return: {source: {fetched, valid, last_fetch_time}}
        """
        stat_key = "%s:source_stat" % self.name
        items = self.__conn.hgetall(stat_key)
        result = {}
        for source, value in items.items():
            try:
                result[source] = json.loads(value)
            except (ValueError, TypeError):
                continue
        return result

    def putSpeedStat(self, events):
        """
        保存校验时间戳列表, 存放在独立hash: <TABLE_NAME>:speed_stat
        :param events: 时间戳列表(最近10分钟)
        :return:
        """
        stat_key = "%s:speed_stat" % self.name
        return self.__conn.hset(stat_key, "events", json.dumps(list(events)))

    def getSpeedStat(self):
        """
        读取校验时间戳列表
        :return: 时间戳列表, 无数据返回 []
        """
        stat_key = "%s:speed_stat" % self.name
        value = self.__conn.hget(stat_key, "events")
        if not value:
            return []
        try:
            data = json.loads(value)
        except (ValueError, TypeError):
            return []
        return data if isinstance(data, list) else []

    def test(self):
        log = LogHandler('ssdb_client')
        try:
            self.getCount()
        except TimeoutError as e:
            log.error('ssdb connection time out: %s' % str(e), exc_info=True)
            return e
        except ConnectionError as e:
            log.error('ssdb connection error: %s' % str(e), exc_info=True)
            return e
        except ResponseError as e:
            log.error('ssdb connection error: %s' % str(e), exc_info=True)
            return e
