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
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from helper.proxy import Proxy


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