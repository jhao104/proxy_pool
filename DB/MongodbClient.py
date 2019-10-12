# coding: utf-8
"""
-------------------------------------------------
   File Name：    MongodbClient.py
   Description :  封装mongodb操作
   Author :       ndiy
   date：          2019/10/12
-------------------------------------------------
   Change Activity:
                   2019/10/12:完成对mongodb的支持
-------------------------------------------------
"""
__author__ = 'ndiy'

from pymongo import MongoClient


class MongodbClient(object):
    def __init__(self, name, host, port, **kwargs):
        self.name = name
        self.client = MongoClient(host, int(port), **kwargs)
        self.db = self.client.proxy

    def changeTable(self, name):
        self.name = name

    def get(self, proxy_obj):
        data = self.db[self.name].find_one({'proxy': proxy_obj.proxy},{'_id':0, 'info_json': 1})
        return data['info_json'] if data else None

    def put(self, proxy_obj):
        if self.db[self.name].find_one({'proxy': proxy_obj.proxy}):
            return None
        else:
            self.db[self.name].insert({'proxy': proxy_obj.proxy, 'info_json': proxy_obj.info_json})

    def pop(self):
        return None

    def delete(self, proxy_str):
        self.db[self.name].remove({'proxy': proxy_str})

    def getAll(self):
        return [p['info_json'] for p in self.db[self.name].find({},{'_id': 0, 'info_json':1})]

    def clear(self):
        self.db[self.name].remove()

    def update(self, proxy_obj):
        self.db[self.name].update({'proxy': proxy_obj.proxy}, {'info_json': proxy_obj.info_json})

    def exists(self, proxy_str):
        return True if self.db[self.name].find_one({'proxy': proxy_str}) is not None else False

    def getNumber(self):
        return self.db[self.name].count()
