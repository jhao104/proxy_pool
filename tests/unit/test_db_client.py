# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testDbClient.py
   Description :   DbClient URI解析单元测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from db.dbClient import DbClient


class TestParseDbConn:

    def test_redis_uri(self):
        DbClient.parseDbConn("redis://:password@127.0.0.1:6379/1")
        assert DbClient.db_type == "REDIS"
        assert DbClient.db_pwd == "password"
        assert DbClient.db_host == "127.0.0.1"
        assert DbClient.db_port == 6379
        assert DbClient.db_name == "1"

    def test_ssdb_uri(self):
        DbClient.parseDbConn("ssdb://:password@127.0.0.1:8888")
        assert DbClient.db_type == "SSDB"
        assert DbClient.db_pwd == "password"
        assert DbClient.db_host == "127.0.0.1"
        assert DbClient.db_port == 8888

    def test_redis_uri_no_password(self):
        DbClient.parseDbConn("redis://127.0.0.1:6379/0")
        assert DbClient.db_type == "REDIS"
        assert DbClient.db_pwd is None
        assert DbClient.db_host == "127.0.0.1"
        assert DbClient.db_port == 6379
        assert DbClient.db_name == "0"

    def test_ssdb_uri_no_password(self):
        DbClient.parseDbConn("ssdb://@127.0.0.1:8888")
        assert DbClient.db_type == "SSDB"
        assert DbClient.db_host == "127.0.0.1"
        assert DbClient.db_port == 8888

    def test_unknown_db_type_raises(self):
        with pytest.raises(AssertionError):
            DbClient("mysql://127.0.0.1:3306")

    @pytest.mark.parametrize("uri,expected_type", [
        ("redis://:pwd@10.0.0.1:6380/2", "REDIS"),
        ("ssdb://:pwd@10.0.0.1:8899", "SSDB"),
    ])
    def test_parse_returns_cls(self, uri, expected_type):
        """parseDbConn 返回 cls 以支持链式调用"""
        result = DbClient.parseDbConn(uri)
        assert result is DbClient
        assert DbClient.db_type == expected_type