# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testSsdbClient
   Description :
   Author :        JHao
   date：          2020/7/3
-------------------------------------------------
   Change Activity:
                   2020/7/3:
-------------------------------------------------
"""
__author__ = 'JHao'


def testSsdbClient():
    from db.dbClient import DbClient
    from helper.proxy import Proxy

    uri = "ssdb://@127.0.0.1:8888"
    db = DbClient(uri)
    db.changeTable("use_proxy")
    proxy = Proxy.createFromJson('{"proxy": "118.190.79.36:8090", "https": false, "fail_count": 0, "region": "", "anonymous": "", "source": "freeProxy14", "check_count": 4, "last_status": true, "last_time": "2021-05-26 10:58:04"}')

    print("put: ", db.put(proxy))

    print("get: ", db.get(https=None))

    print("exists: ", db.exists("27.38.96.101:9797"))

    print("exists: ", db.exists("27.38.96.101:8888"))

    print("getAll: ", db.getAll(https=None))

    # print("pop: ", db.pop(https=None))

    print("clear: ", db.clear())

    print("getCount", db.getCount())


if __name__ == '__main__':
    testSsdbClient()
