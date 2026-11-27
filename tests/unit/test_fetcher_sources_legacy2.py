# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_legacy2.py
   Description :   legacy2 组各代理源 fetcher 测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 legacy2 组代理源测试
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from unittest.mock import patch, MagicMock

from fetcher.baseFetcher import BaseFetcher


# --------------- 辅助工具 ---------------

def _make_response(text="", tree=None, json_data=None):
    """构造 mock 的 WebRequest 返回对象"""
    resp = MagicMock()
    resp.text = text
    resp.tree = tree
    resp.json = json_data if json_data is not None else {}
    return resp


def _table(rows):
    """快速生成 HTML table 字符串"""
    html = "<table>"
    for ip, port in rows:
        html += "<tr><td>%s</td><td>%s</td></tr>" % (ip, port)
    html += "</table>"
    return html


def _assert_valid_proxies(proxies):
    """验证所有 proxy 符合 ip:port 格式"""
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')
    for proxy in proxies:
        assert pattern.match(proxy), "Invalid proxy format: %s" % proxy


# --------------- 接口约定测试 ---------------

class TestFetcherInterface(object):
    """legacy2 组 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.proxz", "ProxzFetcher"),
        ("fetcher.sources.myproxy", "MyProxyFetcher"),
        ("fetcher.sources.proxylistsnet", "ProxyListsNetFetcher"),
        ("fetcher.sources.hidemy", "HidemyFetcher"),
        ("fetcher.sources.torvpn", "TorVpnFetcher"),
        ("fetcher.sources.httptunnel", "HttpTunnelFetcher"),
        ("fetcher.sources.cyberhub", "CyberHubFetcher"),
        ("fetcher.sources.webhostapp", "WebHostAppFetcher"),
        ("fetcher.sources.nntime", "NntimeFetcher"),
    ]

    def test_all_fetchers_have_name_url_enabled(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name, "%s missing name" % class_name
            assert cls.url, "%s missing url" % class_name
            assert hasattr(cls, 'enabled'), "%s missing enabled" % class_name

    def test_all_fetchers_subclass_base(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert issubclass(cls, BaseFetcher), \
                "%s not subclass of BaseFetcher" % class_name

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), "%s missing fetch method" % class_name

    def test_names_are_unique(self):
        names = []
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            names.append(getattr(module, class_name).name)
        assert len(names) == len(set(names))

    def test_all_disabled_by_default(self):
        """实测这些老站/可疑来源均不可用, 默认应禁用"""
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.enabled is False, "%s should be disabled" % class_name


# --------------- Proxz ---------------

class TestProxzFetcher(object):

    @patch("fetcher.sources.proxz.sleep", return_value=None)
    @patch("fetcher.sources.proxz.WebRequest")
    def test_fetch_table(self, mock_wr, mock_sleep):
        from fetcher.sources.proxz import ProxzFetcher
        html = _table([("1.2.3.4", "8080"), ("5.6.7.8", "3128"),
                       ("999.1.1.1", "80")])
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(ProxzFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "999.1.1.1:80" not in result  # 非法 IPv4 被过滤
        _assert_valid_proxies(result)

    @patch("fetcher.sources.proxz.sleep", return_value=None)
    @patch("fetcher.sources.proxz.WebRequest")
    def test_fetch_dedup_across_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.proxz import ProxzFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080")]))
        result = list(ProxzFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxz.sleep", return_value=None)
    @patch("fetcher.sources.proxz.WebRequest")
    def test_sleep_between_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.proxz import ProxzFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        list(ProxzFetcher().fetch())
        assert mock_sleep.call_count == len(ProxzFetcher.urls) - 1
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 2

    @patch("fetcher.sources.proxz.sleep", return_value=None)
    @patch("fetcher.sources.proxz.WebRequest")
    def test_one_page_failure_does_not_abort_others(self, mock_wr, mock_sleep):
        from fetcher.sources.proxz import ProxzFetcher
        ok = _make_response(text=_table([("5.6.7.8", "3128")]))

        def side_effect(url, **kwargs):
            if "high_anonymous" in url:
                raise RuntimeError("boom")
            return ok

        mock_wr.return_value.get.side_effect = side_effect
        result = list(ProxzFetcher().fetch())
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxz.sleep", return_value=None)
    @patch("fetcher.sources.proxz.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.proxz import ProxzFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxzFetcher().fetch()) == []

    @patch("fetcher.sources.proxz.sleep", return_value=None)
    @patch("fetcher.sources.proxz.WebRequest")
    def test_exception_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.proxz import ProxzFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxzFetcher().fetch()) == []


# --------------- My-Proxy ---------------

class TestMyProxyFetcher(object):

    @patch("fetcher.sources.myproxy.sleep", return_value=None)
    @patch("fetcher.sources.myproxy.WebRequest")
    def test_fetch_table(self, mock_wr, mock_sleep):
        from fetcher.sources.myproxy import MyProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")]))
        result = list(MyProxyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.myproxy.sleep", return_value=None)
    @patch("fetcher.sources.myproxy.WebRequest")
    def test_fetch_plain_text_fallback(self, mock_wr, mock_sleep):
        from fetcher.sources.myproxy import MyProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n5.6.7.8:3128")
        result = list(MyProxyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.myproxy.sleep", return_value=None)
    @patch("fetcher.sources.myproxy.WebRequest")
    def test_fetch_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.myproxy import MyProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("1.2.3.4", "8080")]))
        result = list(MyProxyFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.myproxy.sleep", return_value=None)
    @patch("fetcher.sources.myproxy.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.myproxy import MyProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(MyProxyFetcher().fetch()) == []

    @patch("fetcher.sources.myproxy.sleep", return_value=None)
    @patch("fetcher.sources.myproxy.WebRequest")
    def test_exception_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.myproxy import MyProxyFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(MyProxyFetcher().fetch()) == []

    @patch("fetcher.sources.myproxy.sleep", return_value=None)
    @patch("fetcher.sources.myproxy.WebRequest")
    def test_one_page_failure_does_not_abort_others(self, mock_wr, mock_sleep):
        from fetcher.sources.myproxy import MyProxyFetcher
        ok = _make_response(text=_table([("5.6.7.8", "3128")]))

        def side_effect(url, **kwargs):
            if "free-elite" in url:
                raise RuntimeError("boom")
            return ok

        mock_wr.return_value.get.side_effect = side_effect
        result = list(MyProxyFetcher().fetch())
        assert "5.6.7.8:3128" in result


# --------------- Proxylists.net ---------------

class TestProxyListsNetFetcher(object):

    @patch("fetcher.sources.proxylistsnet.WebRequest")
    def test_fetch_table(self, mock_wr):
        from fetcher.sources.proxylistsnet import ProxyListsNetFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")]))
        result = list(ProxyListsNetFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.proxylistsnet.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.proxylistsnet import ProxyListsNetFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("1.2.3.4", "8080")]))
        result = list(ProxyListsNetFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxylistsnet.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.proxylistsnet import ProxyListsNetFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxyListsNetFetcher().fetch()) == []

    @patch("fetcher.sources.proxylistsnet.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.proxylistsnet import ProxyListsNetFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyListsNetFetcher().fetch()) == []


# --------------- HideMy.name ---------------

class TestHidemyFetcher(object):

    @patch("fetcher.sources.hidemy.WebRequest")
    def test_fetch_table_with_nested_tags(self, mock_wr):
        from fetcher.sources.hidemy import HidemyFetcher
        html = ('<table><tr><th>IP</th><th>Port</th></tr>'
                '<tr><td><span>1.2.3.4</span></td><td><span>8080</span></td></tr>'
                '<tr><td><a>5.6.7.8</a></td><td>3128</td></tr></table>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(HidemyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.hidemy.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.hidemy import HidemyFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(HidemyFetcher().fetch()) == []

    @patch("fetcher.sources.hidemy.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.hidemy import HidemyFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(HidemyFetcher().fetch()) == []


# --------------- TorVPN ---------------

class TestTorVpnFetcher(object):

    @patch("fetcher.sources.torvpn.WebRequest")
    def test_fetch_table(self, mock_wr):
        from fetcher.sources.torvpn import TorVpnFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")]))
        result = list(TorVpnFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.torvpn.WebRequest")
    def test_fetch_plain_text_fallback(self, mock_wr):
        from fetcher.sources.torvpn import TorVpnFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n5.6.7.8:3128")
        result = list(TorVpnFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.torvpn.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.torvpn import TorVpnFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(TorVpnFetcher().fetch()) == []

    @patch("fetcher.sources.torvpn.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.torvpn import TorVpnFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(TorVpnFetcher().fetch()) == []


# --------------- HttpTunnel ---------------

class TestHttpTunnelFetcher(object):

    @patch("fetcher.sources.httptunnel.WebRequest")
    def test_fetch_table(self, mock_wr):
        from fetcher.sources.httptunnel import HttpTunnelFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")]))
        result = list(HttpTunnelFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.httptunnel.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.httptunnel import HttpTunnelFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(HttpTunnelFetcher().fetch()) == []

    @patch("fetcher.sources.httptunnel.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.httptunnel import HttpTunnelFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(HttpTunnelFetcher().fetch()) == []


# --------------- CyberHub ---------------

class TestCyberHubFetcher(object):

    @patch("fetcher.sources.cyberhub.WebRequest")
    def test_fetch_plain_text(self, mock_wr):
        from fetcher.sources.cyberhub import CyberHubFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n5.6.7.8:3128\n")
        result = list(CyberHubFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.cyberhub.WebRequest")
    def test_fetch_dedup_and_filters_socks(self, mock_wr):
        from fetcher.sources.cyberhub import CyberHubFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n1.2.3.4:8080\nsocks5://9.9.9.9:1080\n")
        result = list(CyberHubFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1
        assert "9.9.9.9:1080" not in result

    @patch("fetcher.sources.cyberhub.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.cyberhub import CyberHubFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(CyberHubFetcher().fetch()) == []

    @patch("fetcher.sources.cyberhub.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.cyberhub import CyberHubFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(CyberHubFetcher().fetch()) == []


# --------------- WebHostApp ---------------

class TestWebHostAppFetcher(object):

    @patch("fetcher.sources.webhostapp.WebRequest")
    def test_fetch_plain_text(self, mock_wr):
        from fetcher.sources.webhostapp import WebHostAppFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n5.6.7.8:3128")
        result = list(WebHostAppFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.webhostapp.WebRequest")
    def test_fetch_dedup_and_filters_socks(self, mock_wr):
        from fetcher.sources.webhostapp import WebHostAppFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n1.2.3.4:8080\nsocks4://9.9.9.9:1080")
        result = list(WebHostAppFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1
        assert "9.9.9.9:1080" not in result

    @patch("fetcher.sources.webhostapp.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.webhostapp import WebHostAppFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(WebHostAppFetcher().fetch()) == []

    @patch("fetcher.sources.webhostapp.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.webhostapp import WebHostAppFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(WebHostAppFetcher().fetch()) == []


# --------------- Nntime ---------------

class TestNntimeFetcher(object):

    @patch("fetcher.sources.nntime.WebRequest")
    def test_fetch_table(self, mock_wr):
        from fetcher.sources.nntime import NntimeFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text=_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")]))
        result = list(NntimeFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.nntime.WebRequest")
    def test_fetch_plain_text_fallback(self, mock_wr):
        from fetcher.sources.nntime import NntimeFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n5.6.7.8:3128")
        result = list(NntimeFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.nntime.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.nntime import NntimeFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(NntimeFetcher().fetch()) == []

    @patch("fetcher.sources.nntime.WebRequest")
    def test_exception_returns_empty(self, mock_wr):
        from fetcher.sources.nntime import NntimeFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(NntimeFetcher().fetch()) == []
