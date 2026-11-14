# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyApi.py
   Description :   Flask API全路由测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
                   2026/08/30: 新增 /count/source 来源统计接口测试
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
import time
from unittest.mock import patch, MagicMock
from helper.proxy import Proxy
from api.proxyApi import JsonResponse


@pytest.fixture
def mocks(app):
    """快捷访问 app._test_mocks"""
    return app._test_mocks


class TestIndex:

    def test_index_returns_api_list(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "url" in data
        assert len(data["url"]) > 0


class TestGet:

    def test_get_returns_proxy(self, client, mocks):
        proxy = Proxy("1.2.3.4:8080", source="test", https=False)
        mocks["get"].return_value = proxy

        resp = client.get("/get/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["proxy"] == "1.2.3.4:8080"
        assert data["https"] is False

    def test_get_no_proxy(self, client, mocks):
        mocks["get"].return_value = None

        resp = client.get("/get/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == 0
        assert data["src"] == "no proxy"

    def test_get_https_filter(self, client, mocks):
        proxy = Proxy("5.6.7.8:443", source="test", https=True)
        mocks["get"].return_value = proxy

        resp = client.get("/get/?type=https")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["https"] is True
        mocks["get"].assert_called_with(True)

    def test_get_http_filter(self, client, mocks):
        mocks["get"].return_value = None

        client.get("/get/")
        mocks["get"].assert_called_with(False)


class TestPop:

    def test_pop_returns_proxy(self, client, mocks):
        proxy = Proxy("1.2.3.4:8080", source="test")
        mocks["pop"].return_value = proxy

        resp = client.get("/pop/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["proxy"] == "1.2.3.4:8080"

    def test_pop_no_proxy(self, client, mocks):
        mocks["pop"].return_value = None

        resp = client.get("/pop/")
        data = resp.get_json()
        assert data["code"] == 0


class TestAll:

    def test_all_returns_list(self, client, mocks):
        proxies = [
            Proxy("1.2.3.4:8080", source="test"),
            Proxy("5.6.7.8:443", source="test", https=True),
        ]
        mocks["getAll"].return_value = proxies

        resp = client.get("/all/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 2
        assert data[0]["proxy"] == "1.2.3.4:8080"
        assert data[1]["proxy"] == "5.6.7.8:443"

    def test_all_empty(self, client, mocks):
        mocks["getAll"].return_value = []

        resp = client.get("/all/")
        data = resp.get_json()
        assert data == []


class TestDelete:

    def test_delete_calls_handler(self, client, mocks):
        mocks["delete"].return_value = True

        resp = client.get("/delete/?proxy=1.2.3.4:8080")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == 0
        assert data["src"] is True
        mocks["delete"].assert_called_once()


class TestCount:

    def test_count_returns_stats(self, client, mocks):
        proxies = [
            Proxy("1.2.3.4:8080", source="freeProxy01", https=False),
            Proxy("5.6.7.8:443", source="freeProxy02", https=True),
        ]
        mocks["getAll"].return_value = proxies

        resp = client.get("/count/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] == 2
        assert data["http_type"]["http"] == 1
        assert data["http_type"]["https"] == 1
        assert data["source"]["freeProxy01"] == 1
        assert data["source"]["freeProxy02"] == 1

    def test_count_empty(self, client, mocks):
        mocks["getAll"].return_value = []

        resp = client.get("/count/")
        data = resp.get_json()
        assert data["count"] == 0
        assert data["http_type"] == {}
        assert data["source"] == {}


class TestCountSource:

    def test_count_source(self, client, mocks):
        proxies = [
            Proxy("1.2.3.4:8080", source="ip89"),
            Proxy("5.6.7.8:443", source="ip89/kuaidaili", https=True),
            Proxy("6.6.6.6:80", source="kuaidaili"),
        ]
        mocks["getAll"].return_value = proxies
        mocks["getSourceStat"].return_value = {
            "ip89": {"fetched": 10, "valid": 4, "last_fetch_time": "2026-11-14 10:00:00"},
            "kuaidaili": {"fetched": 8, "valid": 2, "last_fetch_time": "2026-11-14 10:05:00"},
        }

        resp = client.get("/count/source/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] == 3
        # 多来源代理在各来源下分别计数
        assert data["source"]["ip89"]["pool_count"] == 2
        assert data["source"]["kuaidaili"]["pool_count"] == 2

    def test_count_source_includes_fetch_stats(self, client, mocks):
        mocks["getAll"].return_value = [Proxy("1.2.3.4:8080", source="ip89")]
        mocks["getSourceStat"].return_value = {
            "ip89": {"fetched": 10, "valid": 4, "last_fetch_time": "2026-11-14 10:00:00"},
        }

        resp = client.get("/count/source/")
        stat = resp.get_json()["source"]["ip89"]
        assert stat["fetched"] == 10
        assert stat["valid"] == 4
        assert stat["survival_rate"] == 0.4
        assert stat["last_fetch_time"] == "2026-11-14 10:00:00"

    def test_count_source_zero_fetched_rate(self, client, mocks):
        """抓取数为 0 时存活率返回 0.0, 不除零"""
        mocks["getAll"].return_value = []
        mocks["getSourceStat"].return_value = {
            "empty_src": {"fetched": 0, "valid": 0, "last_fetch_time": "2026-11-14 10:00:00"},
        }

        stat = client.get("/count/source/").get_json()["source"]["empty_src"]
        assert stat["survival_rate"] == 0.0

    def test_count_source_merges_pool_only_source(self, client, mocks):
        """池中存在但无统计记录的来源也要返回, 统计字段取默认值"""
        mocks["getAll"].return_value = [Proxy("1.2.3.4:8080", source="legacy")]
        mocks["getSourceStat"].return_value = {}

        stat = client.get("/count/source/").get_json()["source"]["legacy"]
        assert stat["pool_count"] == 1
        assert stat["fetched"] == 0
        assert stat["valid"] == 0
        assert stat["survival_rate"] == 0.0
        assert stat["last_fetch_time"] == ""

    def test_count_source_empty(self, client, mocks):
        mocks["getAll"].return_value = []
        mocks["getSourceStat"].return_value = {}

        resp = client.get("/count/source/")
        data = resp.get_json()
        assert data["source"] == {}
        assert data["count"] == 0


class TestCountSpeed:

    def test_count_speed_empty(self, client, mocks):
        mocks["getSpeedStat"].return_value = []

        resp = client.get("/count/speed/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["speed"]["1min"]["count"] == 0
        assert data["speed"]["1min"]["speed"] == 0.0

    def test_count_speed_recent_events(self, client, mocks):
        now = time.time()
        mocks["getSpeedStat"].return_value = [now] * 30

        data = client.get("/count/speed/").get_json()
        assert data["speed"]["1min"]["count"] == 30
        assert data["speed"]["1min"]["speed"] == 0.5  # 30/60
        assert data["speed"]["5min"]["count"] == 30

    def test_count_speed_old_events_excluded(self, client, mocks):
        now = time.time()
        # 7 分钟前的 10 条只应出现在 10min 窗口
        mocks["getSpeedStat"].return_value = [now - 420] * 10

        data = client.get("/count/speed/").get_json()
        assert data["speed"]["1min"]["count"] == 0
        assert data["speed"]["5min"]["count"] == 0
        assert data["speed"]["10min"]["count"] == 10


class TestRefresh:
    def test_refresh_returns_success(self, client):
        resp = client.get("/refresh/")
        assert resp.status_code == 200
        assert b"success" in resp.data


class TestJsonResponse:

    def test_force_type_with_dict(self, app):
        """dict -> JSON Response"""
        with app.app_context():
            resp = JsonResponse.force_type({"key": "val"})
            assert resp.content_type == "application/json"

    def test_force_type_with_list(self, app):
        """list -> JSON Response"""
        with app.app_context():
            resp = JsonResponse.force_type([1, 2, 3])
            assert resp.content_type == "application/json"


class TestRunFlask:

    @patch("api.proxyApi.platform")
    @patch("api.proxyApi.app")
    def test_runflask_windows_path(self, mock_app, mock_platform):
        """Windows 下调用 app.run()"""
        mock_platform.system.return_value = "Windows"
        from api.proxyApi import runFlask
        runFlask()
        mock_app.run.assert_called_once()