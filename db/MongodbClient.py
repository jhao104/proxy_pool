# coding: utf-8
"""
-------------------------------------------------
   File Name：    MongodbClient.py
   Description :  封装mongodb操作
   Author :       JHao netAir
   date：          2017/3/3
-------------------------------------------------
   Change Activity:
                   2017/3/3:
                   2017/9/26:完成对mongodb的支持
-------------------------------------------------
"""
__author__ = 'Maps netAir'

from pymongo import MongoClient


class MongodbClient(object):
    def __init__(self, host, port, **kwargs):
        self.name = ""
        self._db_name = kwargs.pop('db')
        self.client = MongoClient(host, port, **kwargs)
        self.db = self.client[self._db_name]

    def changeTable(self, name):
        self.name = name

    def get(self):
        data = self.db[self.name].find_one()
        return data

    def put(self, proxy_obj):
        if self.db[self.name].find_one({'proxy': proxy_obj.proxy}):
            return None
        else:
            self.db[self.name].insert(proxy_obj.to_dict)

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
        return {p['proxy'] for p in self.db[self.name].find()}

    def clean(self):
        self.client.drop_database(self._db_name)

    def delete_all(self):
        self.db[self.name].remove()

    def update(self, key, value):
        self.db[self.name].update({'proxy': key}, {'$inc': {'num': value}})

    def exists(self, key):
        return True if self.db[self.name].find_one({'proxy': key}) != None else False

    def getNumber(self):
        return self.db[self.name].count()


if __name__ == "__main__":
    db = MongodbClient('first', 'localhost', 27017)
    # db.put('127.0.0.1:1')
    # db2 = MongodbClient('second', 'localhost', 27017)
    # db2.put('127.0.0.1:2')
    print(db.pop())
