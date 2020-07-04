# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testDbClient
   Description :
   Author :        JHao
   date：          2020/6/23
-------------------------------------------------
   Change Activity:
                   2020/6/23:
-------------------------------------------------
"""
__author__ = 'JHao'

from db.dbClient import DbClient


def testDbClient():
    #  ############### ssdb ###############
    ssdb_uri = "ssdb://:password@127.0.0.1:8888"
    s = DbClient.parseDbConn(ssdb_uri)
    assert s.db_type == "SSDB"
    assert s.db_pwd == "password"
    assert s.db_host == "127.0.0.1"
    assert s.db_port == 8888

    #  ############### redis ###############
    redis_uri = "redis://:password@127.0.0.1:6379/1"
    r = DbClient.parseDbConn(redis_uri)
    assert r.db_type == "REDIS"
    assert r.db_pwd == "password"
    assert r.db_host == "127.0.0.1"
    assert r.db_port == 6379
    assert r.db_name == "1"
    print("DbClient ok!")


if __name__ == '__main__':
    testDbClient()
