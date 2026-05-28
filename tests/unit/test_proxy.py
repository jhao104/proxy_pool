# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxy.py
   Description :   Proxy类单元测试
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
from helper.proxy import Proxy


class TestProxyInit:
    """Proxy 构造测试"""

    def test_default_values(self):
        p = Proxy("1.2.3.4:8080")
        assert p.proxy == "1.2.3.4:8080"
        assert p.fail_count == 0
        assert p.region == ""
        assert p.anonymous == ""
        assert p.source == ""
        assert p.check_count == 0
        assert p.last_status == ""
        assert p.last_time == ""
        assert p.https is False

    def test_custom_values(self):
        p = Proxy(
            "5.6.7.8:443",
            fail_count=3,
            region="US",
            anonymous="high",
            source="freeProxy01",
            check_count=10,
            last_status=True,
            last_time="2024-01-01 00:00:00",
            https=True,
        )
        assert p.proxy == "5.6.7.8:443"
        assert p.fail_count == 3
        assert p.region == "US"
        assert p.anonymous == "high"
        assert p.source == "freeProxy01"
        assert p.check_count == 10
        assert p.last_status is True
        assert p.last_time == "2024-01-01 00:00:00"
        assert p.https is True

    def test_source_with_slash(self):
        """source 含 / 时应被拆分为列表，读回时用 / 连接"""
        p = Proxy("1.2.3.4:8080", source="freeProxy01/freeProxy02")
        assert p.source == "freeProxy01/freeProxy02"


class TestProxySerialization:
    """序列化 / 反序列化测试"""

    def test_to_dict_keys(self):
        p = Proxy("1.2.3.4:8080")
        d = p.to_dict
        expected_keys = {"proxy", "https", "fail_count", "region", "anonymous",
                         "source", "check_count", "last_status", "last_time"}
        assert set(d.keys()) == expected_keys

    def test_to_dict_values(self):
        p = Proxy("1.2.3.4:8080", source="test", https=True)
        d = p.to_dict
        assert d["proxy"] == "1.2.3.4:8080"
        assert d["https"] is True
        assert d["source"] == "test"
        assert d["fail_count"] == 0

    def test_to_json_is_valid_json(self):
        p = Proxy("1.2.3.4:8080", source="test")
        j = p.to_json
        d = json.loads(j)
        assert d["proxy"] == "1.2.3.4:8080"

    def test_create_from_json_roundtrip(self):
        """to_json -> createFromJson 往返一致性"""
        original = Proxy("10.0.0.1:3128", source="freeProxy01/freeProxy02",
                         https=True, fail_count=2, region="CN")
        restored = Proxy.createFromJson(original.to_json)
        assert restored.proxy == original.proxy
        assert restored.https == original.https
        assert restored.fail_count == original.fail_count
        assert restored.region == original.region
        assert restored.source == original.source

    def test_create_from_json_minimal(self):
        """createFromJson 缺少字段时使用默认值"""
        j = '{"proxy": "1.2.3.4:8080"}'
        p = Proxy.createFromJson(j)
        assert p.proxy == "1.2.3.4:8080"
        assert p.fail_count == 0
        assert p.https is False

    def test_create_from_json_with_slash_source(self):
        """source 含 / 的 JSON 反序列化"""
        j = '{"proxy": "1.2.3.4:8080", "source": "freeProxy01/freeProxy02", "https": false}'
        p = Proxy.createFromJson(j)
        assert p.source == "freeProxy01/freeProxy02"

    def test_to_dict_to_json_consistency(self):
        """to_dict 和 to_json 数据一致"""
        p = Proxy("1.2.3.4:8080", source="test", https=True, fail_count=1)
        d = p.to_dict
        j = json.loads(p.to_json)
        assert d == j


class TestProxySetters:
    """setter 测试"""

    def test_fail_count_setter(self):
        p = Proxy("1.2.3.4:8080")
        p.fail_count = 5
        assert p.fail_count == 5

    def test_check_count_setter(self):
        p = Proxy("1.2.3.4:8080")
        p.check_count = 10
        assert p.check_count == 10

    def test_last_status_setter(self):
        p = Proxy("1.2.3.4:8080")
        p.last_status = True
        assert p.last_status is True

    def test_last_time_setter(self):
        p = Proxy("1.2.3.4:8080")
        p.last_time = "2024-01-01 12:00:00"
        assert p.last_time == "2024-01-01 12:00:00"

    def test_https_setter(self):
        p = Proxy("1.2.3.4:8080")
        p.https = True
        assert p.https is True

    def test_region_setter(self):
        p = Proxy("1.2.3.4:8080")
        p.region = "US"
        assert p.region == "US"


class TestProxyAddSource:
    """add_source 测试"""

    def test_add_source(self):
        p = Proxy("1.2.3.4:8080", source="src1")
        p.add_source("src2")
        assert "src1" in p.source
        assert "src2" in p.source

    def test_add_source_dedup(self):
        """重复 source 不应重复添加"""
        p = Proxy("1.2.3.4:8080", source="src1")
        p.add_source("src1")
        assert p.source.count("src1") == 1

    def test_add_source_empty_string(self):
        """空字符串不应添加"""
        p = Proxy("1.2.3.4:8080", source="src1")
        p.add_source("")
        assert p.source == "src1"

    def test_add_source_none(self):
        """None 不应添加"""
        p = Proxy("1.2.3.4:8080", source="src1")
        p.add_source(None)
        assert p.source == "src1"