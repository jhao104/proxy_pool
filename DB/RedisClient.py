# -*- coding: utf-8 -*-
# !/usr/bin/env python

'''
self.name为Redis中的一个key
'''

import random
import json
import redis

class ReidsClient(object):
    """
    Reids client
    """

    def __init__(self, name, host, port):
        """
        init
        :param name:
        :param host:
        :param port:
        :return:
        """
        self.name = name
        self.__conn = redis.Redis(host=host, port=port, db=0)

    def get(self):
        """
        get an item
        :return:
        """
        values = self.__conn.smembers(name=self.name)

        return random.choice(list(values)) if values else None

    def put(self, value):
        """
        put an  item
        :param value:
        :return:
        """
        value = json.dump(value, ensure_ascii=False).encode('utf-8') if isinstance(value, (dict, list)) else value
        return self.__conn.sadd(self.name, value)

    def pop(self):
        """
        pop an item
        :return:
        """
        value = self.get()
        if value:
            self.__conn.spop(self.name, value)
        return value

    def delete(self, value):
        """
        delete an item
        :param key:
        :return:
        """
        self.__conn.srem(self.name, value)

    def getAll(self):
        return self.__conn.smembers(self.name)


