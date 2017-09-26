# coding: utf-8

__author__ = 'Maps'

from pymongo import MongoClient
import random
import json


class MongodbClient(object):
    def __init__(self, name, host, port):
        self.name = name
        self.client = MongoClient(host, port)
        self.db = self.client.proxy

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
        value = list(self.db[self.name].aggregate([{'$sample': {'size': 1}}]))[0]['proxy']
        if value:
            self.delete(value)
        return value

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
        return True if self.db[self.name].find({'proxy': key}) == None else False

    def getNumber(self):
        return self.db[self.name].count()


if __name__ == "__main__":
    db = MongodbClient('first', 'localhost', 27017)
    db.put('127.0.0.1:1')
    db2 = MongodbClient('second', 'localhost', 27017)
    db2.put('127.0.0.1:2')
    db.clean()
