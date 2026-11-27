# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_raw.py
   Description :   纯文本代理源 fetcher 测试(raw 组)
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 raw 组代理源测试
-------------------------------------------------
"""
__author__ = 'JHao'

import importlib
import re
from unittest.mock import MagicMock, patch

import pytest

from fetcher.baseFetcher import BaseFetcher


# (module_path, class_name, expected_name, expected_url)
FETCHER_CLASSES = [
    ("fetcher.sources.monosans", "MonosansFetcher", "monosans",
     "https://github.com/monosans/proxy-list"),
    ("fetcher.sources.thespeedx", "TheSpeedXFetcher", "thespeedx",
     "https://github.com/TheSpeedX/SOCKS-List"),
    ("fetcher.sources.roosterkid", "RoosterkidFetcher", "roosterkid",
     "https://github.com/roosterkid/openproxylist"),
    ("fetcher.sources.openproxylist_xyz", "OpenProxyListXyzFetcher", "openproxylist_xyz",
     "https://openproxylist.xyz"),
    ("fetcher.sources.proxyspace", "ProxySpaceFetcher", "proxyspace",
     "https://proxyspace.pro"),
    ("fetcher.sources.clarketm", "ClarketmFetcher", "clarketm",
     "https://github.com/clarketm/proxy-list"),
    ("fetcher.sources.mmpx12", "Mmpx12Fetcher", "mmpx12",
     "https://github.com/mmpx12/proxy-list"),
    ("fetcher.sources.fyvri", "FyvriFetcher", "fyvri",
     "https://github.com/fyvri/fresh-proxy-list"),
    ("fetcher.sources.proxiflyraw", "ProxiflyRawFetcher", "proxifly_raw",
     "https://proxifly.dev/"),
]

PARAMS = [pytest.param(module_path, class_name, name, url,
                       id=name.replace("_", "-"))
          for module_path, class_name, name, url in FETCHER_CLASSES]


def _load(module_path, class_name):
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def _make_response(text=""):
    """构造 mock 的 WebRequest 返回对象"""
    resp = MagicMock()
    resp.text = text
    return resp


def _mock_web_request(module_path):
    return patch(module_path + ".WebRequest")


def _assert_valid_proxies(proxies):
    pattern = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')
    for p in proxies:
        assert isinstance(p, str)
        assert pattern.match(p), "Invalid proxy format: %s" % p


# --------------- 接口约定测试 ---------------

@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_interface(module_path, class_name, name, url):
    cls = _load(module_path, class_name)
    assert issubclass(cls, BaseFetcher)
    assert cls.name == name
    assert cls.url == url
    assert hasattr(cls, "enabled")
    assert isinstance(cls.enabled, bool)
    assert callable(cls.fetch)


@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_enabled_flag(module_path, class_name, name, url):
    """fyvri 单轮 24 万条且存活率仅 0.2%, 默认禁用; 其余源启用"""
    cls = _load(module_path, class_name)
    assert isinstance(cls.enabled, bool)
    if name == "fyvri":
        assert cls.enabled is False
    else:
        assert cls.enabled is True


def test_fyvri_disabled():
    from fetcher.sources.fyvri import FyvriFetcher
    assert FyvriFetcher.enabled is False


# --------------- 各源逻辑测试 ---------------

@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_fetch_parses_text(module_path, class_name, name, url):
    cls = _load(module_path, class_name)
    text = "1.2.3.4:8080\n5.6.7.8:3128\n"
    with _mock_web_request(module_path) as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(cls().fetch())
    assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]
    _assert_valid_proxies(result)


@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_fetch_dedup(module_path, class_name, name, url):
    cls = _load(module_path, class_name)
    text = "1.2.3.4:8080\n1.2.3.4:8080\n5.6.7.8:3128\n1.2.3.4:8080\n"
    with _mock_web_request(module_path) as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(cls().fetch())
    assert result.count("1.2.3.4:8080") == 1
    assert result.count("5.6.7.8:3128") == 1
    assert len(result) == 2


@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_fetch_empty_response(module_path, class_name, name, url):
    cls = _load(module_path, class_name)
    with _mock_web_request(module_path) as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(text="")
        result = list(cls().fetch())
    assert result == []


@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_fetch_no_proxy_text(module_path, class_name, name, url):
    cls = _load(module_path, class_name)
    with _mock_web_request(module_path) as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(
            text="<html><body>404: Not Found</body></html>")
        result = list(cls().fetch())
    assert result == []


@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_fetch_exception_does_not_raise(module_path, class_name, name, url):
    cls = _load(module_path, class_name)
    with _mock_web_request(module_path) as mock_wr:
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        result = list(cls().fetch())
    assert result == []


@pytest.mark.parametrize("module_path,class_name,name,url", PARAMS)
def test_request_params(module_path, class_name, name, url):
    """统一 timeout=10, retry_time=1"""
    cls = _load(module_path, class_name)
    with _mock_web_request(module_path) as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(text="1.2.3.4:8080")
        list(cls().fetch())
        kwargs = mock_wr.return_value.get.call_args[1]
        assert kwargs.get("timeout") == 10
        assert kwargs.get("retry_time") == 1


# --------------- 个别源的格式差异 ---------------

def test_proxifly_raw_strips_http_prefix():
    """proxifly 原始文本行形如 http://ip:port"""
    from fetcher.sources.proxiflyraw import ProxiflyRawFetcher
    text = "http://157.66.16.48:8181\nhttp://96.30.79.84:8081"
    with patch("fetcher.sources.proxiflyraw.WebRequest") as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxiflyRawFetcher().fetch())
    assert result == ["157.66.16.48:8181", "96.30.79.84:8081"]


def test_fyvri_ignores_non_proxy_lines():
    """fyvri 文本可能混有空行/注释等非代理内容"""
    from fetcher.sources.fyvri import FyvriFetcher
    text = "# fresh proxy list\n\n78.156.229.34:1080\n\nabc:def\n160.19.19.31:8080\n"
    with patch("fetcher.sources.fyvri.WebRequest") as mock_wr:
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(FyvriFetcher().fetch())
    assert result == ["78.156.229.34:1080", "160.19.19.31:8080"]
