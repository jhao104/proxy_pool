# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_poolaggr.py
   Description :   公共代理池聚合源测试
   Author :        JHao
   date：          2026/11/22
-------------------------------------------------
   Change Activity:
                   2026/11/22: 新增 poolaggr 聚合源测试
-------------------------------------------------
"""
__author__ = 'JHao'

from unittest.mock import MagicMock, patch

import pytest

from fetcher.baseFetcher import BaseFetcher


CLASSES = [
    ("PoolAggrAli39105Fetcher", "poolaggr_ali_39_105", "http://39.105.98.233:5009", True),
    ("PoolAggrTencent182Fetcher", "poolaggr_tencent_182_254", "http://182.254.172.218:5010", True),
    ("PoolAggrTencentHk43Fetcher", "poolaggr_tencent_hk_43_154", "http://43.154.125.140:5010", True),
    ("PoolAggrAli47120Fetcher", "poolaggr_ali_47_120", "http://47.120.7.67:5010", True),
    ("PoolAggrLinode172Fetcher", "poolaggr_linode_172_104", "http://172.104.79.56:5050", True),
    ("PoolAggrAli12079Fetcher", "poolaggr_ali_120_79", "http://120.79.73.8:5010", True),
    ("PoolAggrAli47102Fetcher", "poolaggr_ali_47_102", "http://47.102.218.41:5010", True),
    ("PoolAggrHostPapa180Fetcher", "poolaggr_hostpapa_172_245_180", "http://172.245.180.249:5010", True),
    ("PoolAggrHostPapa240Fetcher", "poolaggr_hostpapa_172_245_240", "http://172.245.240.207:5010", False),
    ("PoolAggrAli47106Fetcher", "poolaggr_ali_47_106", "http://47.106.153.111:5010", True),
    ("PoolAggrPsychz108Fetcher", "poolaggr_psychz_108_181", "http://108.181.20.225:5010", True),
    ("PoolAggrTelecom120Fetcher", "poolaggr_telecom_120_132", "http://120.132.146.118:25010", True),
]


def _response(json_data=None, text=""):
    resp = MagicMock()
    resp.json = json_data if json_data is not None else {}
    resp.text = text
    return resp


def _cls(name):
    import fetcher.sources.poolaggr as module
    return getattr(module, name)


@pytest.mark.parametrize("class_name,name,url,enabled", CLASSES)
def test_interface(class_name, name, url, enabled):
    cls = _cls(class_name)
    assert issubclass(cls, BaseFetcher)
    assert cls.name == name
    assert cls.url == url
    assert cls.endpoint == url + "/all/"
    assert cls.enabled is enabled
    assert cls.interval == 6 * 60 * 60
    assert callable(cls.fetch)


def test_parse_list_filters_dead_and_dedups():
    cls = _cls("PoolAggrAli39105Fetcher")
    payload = [
        {"proxy": "1.2.3.4:8080", "last_status": True},
        {"proxy": "1.2.3.4:8080", "last_status": True},
        {"proxy": "5.6.7.8:3128", "last_status": False},
        {"proxy": "bad-value"},
        {"ip": "9.9.9.9", "port": 80, "last_status": True},
        "8.8.8.8:8000",
    ]
    with patch("fetcher.sources.poolaggr.WebRequest") as mock_wr:
        mock_wr.return_value.get.return_value = _response(json_data=payload)
        result = list(cls().fetch())
    assert result == ["1.2.3.4:8080", "9.9.9.9:80", "8.8.8.8:8000"]


def test_parse_dict_payload():
    cls = _cls("PoolAggrTencent182Fetcher")
    payload = {"proxies": [{"proxy": "1.2.3.4:8080"}, {"proxy": "5.6.7.8:3128"}]}
    with patch("fetcher.sources.poolaggr.WebRequest") as mock_wr:
        mock_wr.return_value.get.return_value = _response(json_data=payload)
        result = list(cls().fetch())
    assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]


def test_text_fallback():
    cls = _cls("PoolAggrAli47106Fetcher")
    with patch("fetcher.sources.poolaggr.WebRequest") as mock_wr:
        mock_wr.return_value.get.return_value = _response(
            json_data={}, text="1.2.3.4:8080\n5.6.7.8:3128")
        result = list(cls().fetch())
    assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]


def test_request_exception_does_not_raise():
    cls = _cls("PoolAggrPsychz108Fetcher")
    with patch("fetcher.sources.poolaggr.WebRequest") as mock_wr:
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(cls().fetch()) == []


def test_uses_own_endpoint():
    cls = _cls("PoolAggrTelecom120Fetcher")
    with patch("fetcher.sources.poolaggr.WebRequest") as mock_wr:
        mock_wr.return_value.get.return_value = _response(json_data=[])
        list(cls().fetch())
    assert mock_wr.return_value.get.call_args[0][0] == "http://120.132.146.118:25010/all/"
    assert mock_wr.return_value.get.call_args[1]["timeout"] == 10
    assert mock_wr.return_value.get.call_args[1]["retry_time"] == 1
