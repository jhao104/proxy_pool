# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
                   2026/11/14: 新增采集统计的保存与查询
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from db.dbClient import DbClient
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    def get(self, https=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(https)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        self.db.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = self.db.getAll(https)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.proxy)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}

    def saveSourceStat(self, stat_dict):
        """
        保存各源采集统计
        :param stat_dict: {source: {fetched, valid, last_fetch_time}}
        :return:
        """
        return self.db.putSourceStat(stat_dict)

    def getSourceStat(self):
        """
        读取各源采集统计
        :return: {source: {fetched, valid, last_fetch_time}}
        """
        return self.db.getSourceStat()

    def saveSpeedStat(self, events):
        """
        保存校验时间戳列表
        :param events: 时间戳列表
        :return:
        """
        return self.db.putSpeedStat(events)

    def getSpeedStat(self):
        """
        读取校验时间戳列表
        :return: 时间戳列表
        """
        return self.db.getSpeedStat()
