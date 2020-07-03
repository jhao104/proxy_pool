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


def main():
    from db.dbClient import DbClient
    from helper.proxy import Proxy

    db = DbClient("redis://:_@Fintell@10.10.61.65:6379")
    db.changeTable("use_proxy")
    proxy = Proxy.createFromJson(
        '{"proxy": "27.38.96.101:9797", "fail_count": 0, "region": "", "type": "",'
        ' "source": "freeProxy03", "check_count": 0, "last_status": "", "last_time": ""}')

    print("put: ", db.put(proxy))

    print("get: ", db.get())

    print("exists: ", db.exists("27.38.96.101:9797"))

    print("exists: ", db.exists("27.38.96.101:8888"))

    print("pop: ", db.pop())

    print("getAll: ", db.getAll())

    print("getCount", db.getCount())


if __name__ == '__main__':
    main()
