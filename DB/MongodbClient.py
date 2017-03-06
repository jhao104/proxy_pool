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


	def get(self):
		proxy = self.getAll()
		return random.choice(proxy) if proxy else None


	def put(self, value):
		if self.db[self.name].find_one({'proxy': value}):
			return None
		else:
			self.db[self.name].insert({'proxy': value})


	def pop(self):
		value = self.get()
		if value:
			self.delete(value)
		return value


	def delete(self, value):
		self.db[self.name].remove({'proxy': value})


	def getAll(self):
		return [p['proxy'] for p in self.db[self.name].find()]


	def clean(self):
		self.client.drop_database('proxy')


	def delete_all(self):
		self.db[self.name].remove()


if __name__ == "__main__":
	db = MongodbClient('first', 'localhost', 27017)
	db.put('127.0.0.1:1')
	db2 = MongodbClient('second', 'localhost', 27017)
	db2.put('127.0.0.1:2')
	db.clean()

