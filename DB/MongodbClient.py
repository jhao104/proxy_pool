# coding: utf-8
"""
-------------------------------------------------
   File Name：    MongodbClient.py
   Description :  封装mongodb操作
   Author :       Maps netAir
   date：          2017/3/3
-------------------------------------------------
   Change Activity:
                   2017/3/3:
                   2017/9/26:完成对mongodb的支持
                   2017/10/13:添加mongodb对用户名密码的支持
-------------------------------------------------
"""
__author__ = 'Maps netAir'

from pymongo import MongoClient


class MongodbClient(object):
    def __init__(self, config):
        self.name = config.db_name
        self.client = MongoClient(host=config.db_host, port=config.db_port)
        self.db = self.client.proxy
        try:
            self.db.authenticate(config.db_username, config.db_password)
        except:
            pass

    def changeTable(self, name):
        self.name = name

    def get(self, proxy):
        data = self.db[self.name].find_one({'proxy': proxy})
        return data['num'] if data != None else None

    def put(self, proxy, num=1):
        if self.db[self.name].find_one({'proxy': proxy}):
            return None
        else:
            self.db[self.name].insert({'proxy': proxy, 'num': num})

    def pop(self):
        data = list(self.db[self.name].aggregate([{'$sample': {'size': 1}}]))
        if data:
            data = data[0]
            value = data['proxy']
            self.delete(value)
            return {'proxy': value, 'value': data['num']}
        return None

    def delete(self, value):
        self.db[self.name].remove({'proxy': value})

    def getAll(self):
        return {p['proxy']: p['num'] for p in self.db[self.name].find()}

    def clean(self):
        self.client.drop_database('proxy')

    def delete_all(self):
        self.db[self.name].remove()

    def update(self, key, value):
        self.db[self.name].update({'proxy': key}, {'$inc': {'num': value}})

    def exists(self, key):
        return True if self.db[self.name].find_one({'proxy': key}) != None else False

    def getNumber(self):
        return self.db[self.name].count()
