# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testRedisClient
   Description :
   Author :        JHao
   date：          2020/6/23
-------------------------------------------------
   Change Activity:
                   2020/6/23:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import  os
sys.path.append(os.getcwd())

def testRedisClient():
    from db.dbClient import DbClient
    from helper.proxy import Proxy

    uri = "redis://:123456@127.0.0.1:6379"
    db = DbClient(uri)
    db.changeTable("use_proxy")
    proxy = Proxy.createFromJson(
        '{"proxy": "27.38.96.101:9797", "fail_count": 0, "region": "", "type": "",'
        ' "source": "freeProxy03", "check_count": 0, "last_status": "", "last_time": ""}')

    # print("put: ", db.put(proxy))

    # print("put: ", db.putTag(tag='test', proxy='1238:7'))
    # print("del: ", db.deleteTag(tag='test', proxy='1234'))
    print("get: ", db.getByTag(tag='test'))

    # print("get: ", db.get(last_status=1))

    # print("exists: ", db.exists("27.38.96.101:9797"))

    # print("exists: ", db.exists("27.38.96.101:8888"))

    # print("pop: ", db.pop())

    # print("getAll: ", db.getAll())

    # print("getCount", db.getCount())


if __name__ == '__main__':
    testRedisClient()
