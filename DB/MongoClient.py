#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    MongoClient.py
   Description :  封装 MongoDB 操作
   Author :       Fbigun
   date：         2016/12/18
-------------------------------------------------
"""
__author__ = 'Fbigun'

import random
import json
import pymongo
from pymongo.errors import OperationFailure

class MongoClient(object):
    """
    mongoDB Client
    """

    def __init__(self, name, host, port, uname, passwd):
        self.__uri = "mongodb://{0}:{1}".format(host, port)
        self.__client = pymongo.MongoClient(self.__uri)
        self.__db = self.__client[name]
        try:
            self.__db.authenticate(uname, passwd)
        except OperationFailure as e:
            print "Wrong username or password"
            print e

    def get(self):
        """
        get an item
        :return:
        """
        values = self.getAll()
        return random.choice(values) if values else None

    def put(self, value):
        """
        put an  item
        :param value:
        :param value:
        :return:
        """
        value = json.dump(value, ensure_ascii=False).encode('utf-8') if isinstance(value, (dict, list)) else value
        return self.collection.insert({"proxy": value})

    def pop(self):
        """
        pop an item
        :return:
        """
        value = self.get()
        if value:
            self.collection.find_one_and_delete({"proxy": value})
        return value

    def delete(self, value):
        """
        delete an item
        :param key:
        :return:
        """
        cursor = self.collection.find({"proxy": value})
        self.collection.delete(cursor)

    def getAll(self):
        values = []
        for x in self.collection.find({}, {"_id": False}):
            values.extend(list(x.values()))
        return values

    def changeTable(self, name):
        self.collection = self.__db[name]
