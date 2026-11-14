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


class TestRedisAclUsername:

    def test_username_passed_to_pool(self):
        """ACL 用户名必须传给连接池, 否则 default 用户被禁用时无法认证"""
        with patch("db.redisClient.BlockingConnectionPool") as mock_pool:
            RedisClient(host="localhost", port=6379,
                        username="redis", password="pwd", db="0")
        kwargs = mock_pool.call_args[1]
        assert kwargs.get("username") == "redis"
        assert kwargs.get("password") == "pwd"

    def test_no_username_omitted(self):
        """无用户名时不传 username, 保持兼容旧配置"""
        with patch("db.redisClient.BlockingConnectionPool") as mock_pool:
            RedisClient(host="localhost", port=6379,
                        username=None, password="pwd", db="0")
        kwargs = mock_pool.call_args[1]
        assert "username" not in kwargs
        assert kwargs.get("password") == "pwd"


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


class TestRedisSourceStat:

    def test_put_and_get_source_stat(self, redis_client):
        """统计写入独立 hash, 可原样读回"""
        stat = {"ip89": {"fetched": 10, "valid": 4, "last_fetch_time": "2026-11-14 10:00:00"}}
        redis_client.putSourceStat(stat)
        assert redis_client.getSourceStat() == stat

    def test_get_source_stat_empty(self, redis_client):
        assert redis_client.getSourceStat() == {}

    def test_put_source_stat_empty_noop(self, redis_client):
        """空字典不写入"""
        redis_client.putSourceStat({})
        assert redis_client.getSourceStat() == {}

    def test_source_stat_does_not_pollute_proxy_hash(self, redis_client):
        """统计存放于 <table>:source_stat, 不影响代理 hash"""
        redis_client.put(_make_proxy("1.2.3.4:8080"))
        redis_client.putSourceStat({"ip89": {"fetched": 1, "valid": 1, "last_fetch_time": ""}})
        assert redis_client.getCount()["total"] == 1

    def test_put_source_stat_overwrites(self, redis_client):
        """同一源再次写入覆盖旧统计"""
        redis_client.putSourceStat({"ip89": {"fetched": 1, "valid": 0, "last_fetch_time": "t1"}})
        redis_client.putSourceStat({"ip89": {"fetched": 9, "valid": 5, "last_fetch_time": "t2"}})
        assert redis_client.getSourceStat()["ip89"]["fetched"] == 9

    def test_get_source_stat_skips_corrupt_value(self, redis_client, fake_redis):
        """非法 JSON 值被跳过, 不抛异常"""
        fake_redis.hset("test_proxy:source_stat", "broken", "not-json")
        fake_redis.hset("test_proxy:source_stat", "ok",
                        '{"fetched": 1, "valid": 1, "last_fetch_time": "t"}')
        result = redis_client.getSourceStat()
        assert "broken" not in result
        assert result["ok"]["fetched"] == 1


class TestRedisSpeedStat:

    def test_put_and_get_speed_stat(self, redis_client):
        """时间戳列表可原样读回"""
        events = [1700000000.0, 1700000001.5]
        redis_client.putSpeedStat(events)
        assert redis_client.getSpeedStat() == events

    def test_get_speed_stat_empty(self, redis_client):
        assert redis_client.getSpeedStat() == []

    def test_put_empty_list(self, redis_client):
        redis_client.putSpeedStat([])
        assert redis_client.getSpeedStat() == []

    def test_put_overwrites(self, redis_client):
        redis_client.putSpeedStat([1.0, 2.0])
        redis_client.putSpeedStat([3.0])
        assert redis_client.getSpeedStat() == [3.0]

    def test_does_not_pollute_proxy_hash(self, redis_client):
        """速度统计独立存放, 不影响代理 hash"""
        redis_client.put(_make_proxy("1.2.3.4:8080"))
        redis_client.putSpeedStat([1.0, 2.0])
        assert redis_client.getCount()["total"] == 1

    def test_corrupt_value_returns_empty(self, redis_client, fake_redis):
        fake_redis.hset("test_proxy:speed_stat", "events", "not-json")
        assert redis_client.getSpeedStat() == []

    def test_non_list_value_returns_empty(self, redis_client, fake_redis):
        fake_redis.hset("test_proxy:speed_stat", "events", '{"a": 1}')
        assert redis_client.getSpeedStat() == []