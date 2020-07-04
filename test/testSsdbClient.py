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

    uri = "ssdb://@120.79.78.193:8888"
    db = DbClient(uri)
    db.changeTable("use_proxy")
    proxy = Proxy.createFromJson(
        '{"proxy": "27.38.96.101:9797", "fail_count": 0, "region": "", "type": "",'
        ' "source": "freeProxy03", "check_count": 0, "last_status": "", "last_time": ""}')

    print("put: ", db.put(proxy))

    print("get: ", db.get())

    print("exists: ", db.exists("27.38.96.101:9797"))

    print("exists: ", db.exists("27.38.96.101:8888"))

    print("getAll: ", db.getAll())

    print("pop: ", db.pop())

    print("getCount", db.getCount())


if __name__ == '__main__':
    testSsdbClient()
