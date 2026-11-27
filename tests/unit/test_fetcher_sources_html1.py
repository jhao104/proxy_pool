# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_html1.py
   Description :   html1 组各代理源 fetcher 测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 html1 组代理源测试
-------------------------------------------------
"""
__author__ = 'JHao'

import base64
import re
from unittest.mock import patch, MagicMock

from lxml import etree

from fetcher.baseFetcher import BaseFetcher


# --------------- 辅助工具 ---------------

def _make_response(text="", tree=None, json_data=None):
    """构造 mock 的 WebRequest 返回对象"""
    resp = MagicMock()
    resp.text = text
    resp.tree = tree
    resp.json = json_data if json_data is not None else {}
    return resp


def _assert_valid_proxies(proxies):
    """验证所有 proxy 符合 ip:port 格式"""
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')
    for p in proxies:
        assert pattern.match(p), f"Invalid proxy format: {p}"


# --------------- 接口约定测试 ---------------

class TestFetcherInterface(object):
    """html1 组 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.proxylistplus", "ProxyListPlusFetcher"),
        ("fetcher.sources.freeproxylistnet", "FreeProxyListNetFetcher"),
        ("fetcher.sources.proxylistorg", "ProxyListOrgFetcher"),
        ("fetcher.sources.freeproxylistcc", "FreeProxyListCcFetcher"),
        ("fetcher.sources.proxytools", "ProxyToolsFetcher"),
        ("fetcher.sources.qiyunip", "QiyunipFetcher"),
        ("fetcher.sources.qydaili", "QydailiFetcher"),
        ("fetcher.sources.proxy5", "Proxy5Fetcher"),
    ]

    def test_all_fetchers_have_name_url_enabled(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name, f"{class_name} missing name"
            assert cls.url, f"{class_name} missing url"
            assert hasattr(cls, 'enabled'), f"{class_name} missing enabled"

    def test_all_fetchers_subclass_base(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert issubclass(cls, BaseFetcher), f"{class_name} not subclass of BaseFetcher"

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), f"{class_name} missing fetch method"

    def test_enabled_flags_match_probe_result(self):
        """enabled 反映实测结论: 可解析为 True, 不可达/无数据为 False"""
        expected = {
            "proxylistplus": True,      # 每页 50 条
            "freeproxylistnet": False,  # 无 IPv4 A 记录, 连接失败
            "proxylistorg": False,      # 两次实测连接超时
            "freeproxylistcc": False,   # 200 但数据由 JS 渲染
            "proxytools": False,        # IP 有, 端口藏验证码后
            "qiyunip": True,            # 15 条可解析
            "qydaili": False,           # DNS 解析失败
            "proxy5": False,            # 403 反爬
        }
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.enabled == expected[cls.name], \
                f"{cls.name} enabled should be {expected[cls.name]}"


# --------------- ProxyListPlus ---------------

class TestProxyListPlusFetcher(object):

    @patch("fetcher.sources.proxylistplus.sleep", return_value=None)
    @patch("fetcher.sources.proxylistplus.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistplus import ProxyListPlusFetcher
        html = ('<tr><td>1.2.3.4</td><td>8080</td></tr>'
                '<tr><td>5.6.7.8</td><td>3128</td></tr>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(ProxyListPlusFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxylistplus.sleep", return_value=None)
    @patch("fetcher.sources.proxylistplus.WebRequest")
    def test_fetch_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistplus import ProxyListPlusFetcher
        html = '<tr><td>1.2.3.4</td><td>8080</td></tr>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(ProxyListPlusFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxylistplus.sleep", return_value=None)
    @patch("fetcher.sources.proxylistplus.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistplus import ProxyListPlusFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxyListPlusFetcher().fetch()) == []

    @patch("fetcher.sources.proxylistplus.sleep", return_value=None)
    @patch("fetcher.sources.proxylistplus.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistplus import ProxyListPlusFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyListPlusFetcher().fetch()) == []

    @patch("fetcher.sources.proxylistplus.sleep", return_value=None)
    @patch("fetcher.sources.proxylistplus.WebRequest")
    def test_two_pages_requests(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistplus import ProxyListPlusFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        list(ProxyListPlusFetcher().fetch())
        assert mock_wr.return_value.get.call_count == 2
        assert mock_sleep.call_count == 1


# --------------- FreeProxyListNet ---------------

class TestFreeProxyListNetFetcher(object):

    @patch("fetcher.sources.freeproxylistnet.WebRequest")
    def test_fetch_from_textarea(self, mock_wr):
        from fetcher.sources.freeproxylistnet import FreeProxyListNetFetcher
        html = ('<div id="raw"><div><div><div>x</div>'
                '<div><textarea>1.2.3.4:8080\n5.6.7.8:3128</textarea></div>'
                '</div></div></div>')
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(FreeProxyListNetFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.freeproxylistnet.WebRequest")
    def test_fetch_text_fallback(self, mock_wr):
        from fetcher.sources.freeproxylistnet import FreeProxyListNetFetcher
        mock_wr.return_value.get.return_value = _make_response(
            tree=None, text="<p>1.2.3.4:8080 5.6.7.8:3128</p>")
        result = list(FreeProxyListNetFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.freeproxylistnet.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.freeproxylistnet import FreeProxyListNetFetcher
        html = ('<div id="raw"><div><div><div>x</div>'
                '<div><textarea>1.2.3.4:8080\n1.2.3.4:8080</textarea></div>'
                '</div></div></div>')
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(FreeProxyListNetFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.freeproxylistnet.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.freeproxylistnet import FreeProxyListNetFetcher
        mock_wr.return_value.get.return_value = _make_response(tree=None, text="")
        assert list(FreeProxyListNetFetcher().fetch()) == []

    @patch("fetcher.sources.freeproxylistnet.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.freeproxylistnet import FreeProxyListNetFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(FreeProxyListNetFetcher().fetch()) == []


# --------------- ProxyListOrg ---------------

class TestProxyListOrgFetcher(object):

    @staticmethod
    def _enc(proxy):
        return base64.b64encode(proxy.encode("utf-8")).decode("utf-8")

    @patch("fetcher.sources.proxylistorg.sleep", return_value=None)
    @patch("fetcher.sources.proxylistorg.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistorg import ProxyListOrgFetcher
        text = "Proxy('%s') Proxy('%s')" % (
            self._enc("1.2.3.4:8080"), self._enc("5.6.7.8:3128"))
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyListOrgFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxylistorg.sleep", return_value=None)
    @patch("fetcher.sources.proxylistorg.WebRequest")
    def test_fetch_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistorg import ProxyListOrgFetcher
        item = self._enc("1.2.3.4:8080")
        text = "Proxy('%s') Proxy('%s')" % (item, item)
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyListOrgFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxylistorg.sleep", return_value=None)
    @patch("fetcher.sources.proxylistorg.WebRequest")
    def test_bad_base64_skipped(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistorg import ProxyListOrgFetcher
        # 非法 base64 与解码后非 ip:port 的内容都应跳过
        text = "Proxy('!!!') Proxy('%s')" % self._enc("not-a-proxy")
        mock_wr.return_value.get.return_value = _make_response(text=text)
        assert list(ProxyListOrgFetcher().fetch()) == []

    @patch("fetcher.sources.proxylistorg.sleep", return_value=None)
    @patch("fetcher.sources.proxylistorg.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistorg import ProxyListOrgFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxyListOrgFetcher().fetch()) == []

    @patch("fetcher.sources.proxylistorg.sleep", return_value=None)
    @patch("fetcher.sources.proxylistorg.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.proxylistorg import ProxyListOrgFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyListOrgFetcher().fetch()) == []


# --------------- FreeProxyListCc ---------------

class TestFreeProxyListCcFetcher(object):

    @patch("fetcher.sources.freeproxylistcc.sleep", return_value=None)
    @patch("fetcher.sources.freeproxylistcc.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.freeproxylistcc import FreeProxyListCcFetcher
        html = ('<tr><td>1.2.3.4</td><td>8080</td></tr>'
                '<tr><td>5.6.7.8</td><td>3128</td></tr>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(FreeProxyListCcFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.freeproxylistcc.sleep", return_value=None)
    @patch("fetcher.sources.freeproxylistcc.WebRequest")
    def test_fetch_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.freeproxylistcc import FreeProxyListCcFetcher
        html = '<tr><td>1.2.3.4</td><td>8080</td></tr>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(FreeProxyListCcFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.freeproxylistcc.sleep", return_value=None)
    @patch("fetcher.sources.freeproxylistcc.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.freeproxylistcc import FreeProxyListCcFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(FreeProxyListCcFetcher().fetch()) == []

    @patch("fetcher.sources.freeproxylistcc.sleep", return_value=None)
    @patch("fetcher.sources.freeproxylistcc.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.freeproxylistcc import FreeProxyListCcFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(FreeProxyListCcFetcher().fetch()) == []

    @patch("fetcher.sources.freeproxylistcc.sleep", return_value=None)
    @patch("fetcher.sources.freeproxylistcc.WebRequest")
    def test_three_pages_and_sleep(self, mock_wr, mock_sleep):
        from fetcher.sources.freeproxylistcc import FreeProxyListCcFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        list(FreeProxyListCcFetcher().fetch())
        assert mock_wr.return_value.get.call_count == 3
        assert mock_sleep.call_count == 2


# --------------- ProxyTools ---------------

class TestProxyToolsFetcher(object):

    @staticmethod
    def _table(rows):
        html = "<table><tr><th>IP</th><th>Port</th></tr>"
        for ip, port in rows:
            html += "<tr><td>%s</td><td>%s</td></tr>" % (ip, port)
        html += "</table>"
        return etree.HTML(html)

    @patch("fetcher.sources.proxytools.sleep", return_value=None)
    @patch("fetcher.sources.proxytools.WebRequest")
    def test_fetch_real_port(self, mock_wr, mock_sleep):
        from fetcher.sources.proxytools import ProxyToolsFetcher
        tree = self._table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(ProxyToolsFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxytools.sleep", return_value=None)
    @patch("fetcher.sources.proxytools.WebRequest")
    def test_missing_port_row_skipped(self, mock_wr, mock_sleep):
        """端口位置是“显示端口”时不应硬编码 80, 直接跳过"""
        from fetcher.sources.proxytools import ProxyToolsFetcher
        tree = self._table([("1.2.3.4", "显示端口"), ("5.6.7.8", "3128")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(ProxyToolsFetcher().fetch())
        assert "1.2.3.4:80" not in result
        assert "1.2.3.4:8080" not in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxytools.sleep", return_value=None)
    @patch("fetcher.sources.proxytools.WebRequest")
    def test_fetch_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.proxytools import ProxyToolsFetcher
        tree = self._table([("1.2.3.4", "8080")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(ProxyToolsFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxytools.sleep", return_value=None)
    @patch("fetcher.sources.proxytools.WebRequest")
    def test_none_tree_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.proxytools import ProxyToolsFetcher
        mock_wr.return_value.get.return_value = _make_response(tree=None)
        assert list(ProxyToolsFetcher().fetch()) == []

    @patch("fetcher.sources.proxytools.sleep", return_value=None)
    @patch("fetcher.sources.proxytools.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.proxytools import ProxyToolsFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyToolsFetcher().fetch()) == []

    @patch("fetcher.sources.proxytools.sleep", return_value=None)
    @patch("fetcher.sources.proxytools.WebRequest")
    def test_eight_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.proxytools import ProxyToolsFetcher
        mock_wr.return_value.get.return_value = _make_response(tree=None)
        list(ProxyToolsFetcher().fetch())
        assert mock_wr.return_value.get.call_count == 8
        assert mock_sleep.call_count == 7


# --------------- Qiyunip ---------------

class TestQiyunipFetcher(object):

    @staticmethod
    def _table(rows):
        html = "<table><tr><th>IP</th><th>PORT</th><th>匿名度</th></tr>"
        for ip, port in rows:
            html += "<tr><th>%s</th><th>%s</th><th>高匿</th></tr>" % (ip, port)
        html += "</table>"
        return etree.HTML(html)

    @patch("fetcher.sources.qiyunip.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.qiyunip import QiyunipFetcher
        tree = self._table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(QiyunipFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.qiyunip.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.qiyunip import QiyunipFetcher
        tree = self._table([("1.2.3.4", "8080"), ("1.2.3.4", "8080")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(QiyunipFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.qiyunip.WebRequest")
    def test_none_tree_returns_empty(self, mock_wr):
        from fetcher.sources.qiyunip import QiyunipFetcher
        mock_wr.return_value.get.return_value = _make_response(tree=None)
        assert list(QiyunipFetcher().fetch()) == []

    @patch("fetcher.sources.qiyunip.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.qiyunip import QiyunipFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(QiyunipFetcher().fetch()) == []


# --------------- Qydaili ---------------

class TestQydailiFetcher(object):

    @patch("fetcher.sources.qydaili.sleep", return_value=None)
    @patch("fetcher.sources.qydaili.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.qydaili import QydailiFetcher
        html = ('<tr><td class="x">1.2.3.4</td><td class="y">8080</td></tr>'
                '<tr><td class="x">5.6.7.8</td><td class="y">3128</td></tr>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(QydailiFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.qydaili.sleep", return_value=None)
    @patch("fetcher.sources.qydaili.WebRequest")
    def test_fetch_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.qydaili import QydailiFetcher
        html = '<tr><td>1.2.3.4</td><td>8080</td></tr>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(QydailiFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.qydaili.sleep", return_value=None)
    @patch("fetcher.sources.qydaili.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.qydaili import QydailiFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(QydailiFetcher().fetch()) == []

    @patch("fetcher.sources.qydaili.sleep", return_value=None)
    @patch("fetcher.sources.qydaili.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.qydaili import QydailiFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(QydailiFetcher().fetch()) == []


# --------------- Proxy5 ---------------

class TestProxy5Fetcher(object):

    @staticmethod
    def _table(rows):
        html = "<table><tr><th>IP</th><th>Port</th></tr>"
        for ip, port in rows:
            html += "<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (ip, port)
        html += "</table>"
        return etree.HTML(html)

    @patch("fetcher.sources.proxy5.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxy5 import Proxy5Fetcher
        tree = self._table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(Proxy5Fetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxy5.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.proxy5 import Proxy5Fetcher
        tree = self._table([("1.2.3.4", "8080"), ("1.2.3.4", "8080")])
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(Proxy5Fetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxy5.WebRequest")
    def test_none_tree_returns_empty(self, mock_wr):
        from fetcher.sources.proxy5 import Proxy5Fetcher
        mock_wr.return_value.get.return_value = _make_response(tree=None)
        assert list(Proxy5Fetcher().fetch()) == []

    @patch("fetcher.sources.proxy5.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.proxy5 import Proxy5Fetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(Proxy5Fetcher().fetch()) == []
