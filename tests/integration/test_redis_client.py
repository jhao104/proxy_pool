# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testRedisClient.py
   Description :   RedisClient集成测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import pytest
import fakeredis
from unittest.mock import patch, MagicMock
from db.redisClient import RedisClient
from helper.proxy import Proxy


@pytest.fixture
def redis_client(fake_redis):
    """RedisClient 实例，内部连接替换为 fakeredis"""
    with patch("db.redisClient.BlockingConnectionPool"):
        with patch("db.redisClient.Redis", return_value=fake_redis):
            client = RedisClient(host="localhost", port=6379,
                                 username=None, password=None, db="0")
            client.changeTable("test_proxy")
            return client


def _make_proxy(proxy_str, https=False, source="test"):
    return Proxy(proxy_str, source=https and "https_test" or "http_test",
                 https=https)


class TestRedisPutGet:

    def test_put_and_get(self, redis_client):
        proxy = _make_proxy("1.2.3.4:8080")
        redis_client.put(proxy)
        result = redis_client.get(https=False)
        assert result is not None
        data = json.loads(result)
        assert data["proxy"] == "1.2.3.4:8080"

    def test_get_https(self, redis_client):
        proxy = _make_proxy("5.6.7.8:443", https=True)
        redis_client.put(proxy)
        result = redis_client.get(https=True)
        assert result is not None
        data = json.loads(result)
        assert data["https"] is True

    def test_get_https_excludes_http(self, redis_client):
        proxy = _make_proxy("1.2.3.4:8080", https=False)
        redis_client.put(proxy)
        result = redis_client.get(https=True)
        assert result is None

    def test_get_empty_returns_none(self, redis_client):
        result = redis_client.get(https=False)
        assert result is None


class TestRedisExists:

    def test_exists_true(self, redis_client):
        proxy = _make_proxy("1.2.3.4:8080")
        redis_client.put(proxy)
        assert redis_client.exists("1.2.3.4:8080") is True

    def test_exists_false(self, redis_client):
        assert redis_client.exists("9.9.9.9:9999") is False


class TestRedisDelete:

    def test_delete(self, redis_client):
        proxy = _make_proxy("1.2.3.4:8080")
        redis_client.put(proxy)
        redis_client.delete("1.2.3.4:8080")
        assert redis_client.exists("1.2.3.4:8080") is False


class TestRedisPop:

    def test_pop_removes_proxy(self, redis_client):
        proxy = _make_proxy("1.2.3.4:8080")
        redis_client.put(proxy)
        popped = redis_client.pop(https=False)
        assert popped is not None
        assert redis_client.exists("1.2.3.4:8080") is False

    def test_pop_empty_returns_none(self, redis_client):
        result = redis_client.pop(https=False)
        assert result is None


class TestRedisGetAll:

    def test_get_all(self, redis_client):
        redis_client.put(_make_proxy("1.2.3.4:8080"))
        redis_client.put(_make_proxy("5.6.7.8:443", https=True))
        all_proxies = redis_client.getAll(https=False)
        assert len(all_proxies) == 2

    def test_get_all_https_filter(self, redis_client):
        redis_client.put(_make_proxy("1.2.3.4:8080", https=False))
        redis_client.put(_make_proxy("5.6.7.8:443", https=True))
        https_proxies = redis_client.getAll(https=True)
        assert len(https_proxies) == 1


class TestRedisGetCount:

    def test_get_count(self, redis_client):
        redis_client.put(_make_proxy("1.2.3.4:8080", https=False))
        redis_client.put(_make_proxy("5.6.7.8:443", https=True))
        count = redis_client.getCount()
        assert count["total"] == 2
        assert count["https"] == 1

    def test_get_count_empty(self, redis_client):
        count = redis_client.getCount()
        assert count["total"] == 0
        assert count["https"] == 0


class TestRedisClear:

    def test_clear(self, redis_client):
        redis_client.put(_make_proxy("1.2.3.4:8080"))
        redis_client.put(_make_proxy("5.6.7.8:443"))
        redis_client.clear()
        count = redis_client.getCount()
        assert count["total"] == 0


class TestRedisChangeTable:

    def test_change_table_isolation(self, redis_client):
        redis_client.put(_make_proxy("1.2.3.4:8080"))
        redis_client.changeTable("other_table")
        assert redis_client.getCount()["total"] == 0
        redis_client.changeTable("test_proxy")
        assert redis_client.getCount()["total"] == 1