# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_html2.py
   Description :   html2 组各代理源 fetcher 测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 html2 组代理源测试
-------------------------------------------------
"""
__author__ = 'JHao'

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
    for proxy in proxies:
        assert pattern.match(proxy), "Invalid proxy format: %s" % proxy


# --------------- 接口约定测试 ---------------

class TestHtml2FetcherInterface(object):
    """html2 组 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.proxynova", "ProxyNovaFetcher"),
        ("fetcher.sources.freeproxyworld", "FreeProxyWorldFetcher"),
        ("fetcher.sources.cnproxy", "CnProxyFetcher"),
        ("fetcher.sources.freeproxylistsnet", "FreeProxyListsNetFetcher"),
        ("fetcher.sources.binglx", "BinglxFetcher"),
        ("fetcher.sources.jiangxianli", "JiangxianliFetcher"),
        ("fetcher.sources.proxyelite", "ProxyEliteFetcher"),
        ("fetcher.sources.usproxy", "UsProxyFetcher"),
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
            assert callable(getattr(cls, 'fetch', None)), \
                "%s missing fetch method" % class_name

    def test_enabled_matches_probe_result(self):
        """实测可用为 True, 不可达/404/结构失效为 False"""
        from fetcher.sources.proxynova import ProxyNovaFetcher
        from fetcher.sources.freeproxyworld import FreeProxyWorldFetcher
        from fetcher.sources.cnproxy import CnProxyFetcher
        from fetcher.sources.freeproxylistsnet import FreeProxyListsNetFetcher
        from fetcher.sources.binglx import BinglxFetcher
        from fetcher.sources.jiangxianli import JiangxianliFetcher
        from fetcher.sources.proxyelite import ProxyEliteFetcher
        from fetcher.sources.usproxy import UsProxyFetcher

        assert FreeProxyWorldFetcher.enabled is True
        assert ProxyEliteFetcher.enabled is True
        assert ProxyNovaFetcher.enabled is False
        assert CnProxyFetcher.enabled is False
        assert FreeProxyListsNetFetcher.enabled is False
        assert BinglxFetcher.enabled is False
        assert JiangxianliFetcher.enabled is False
        assert UsProxyFetcher.enabled is False


# --------------- proxynova ---------------

class TestProxyNovaFetcher(object):

    HTML = (
        '<html><body><table id="tbl_proxy_list"><tbody>'
        # atob 拼接
        '<tr><td><script>document.write(atob("MTg1LjE4Ni4=")+atob("MTYyLjIxNw=="));'
        '</script></td><td>8080</td><td>HTTP</td></tr>'
        # 重复行
        '<tr><td><script>document.write(atob("MTg1LjE4Ni4=")+atob("MTYyLjIxNw=="));'
        '</script></td><td>8080</td><td>HTTP</td></tr>'
        # socks 应被过滤
        '<tr><td><script>document.write(atob("MS4yLjMuNA=="));</script></td>'
        '<td>1080</td><td>SOCKS5</td></tr>'
        # 表头(无 script)
        '<tr><th>Proxy IP</th><th>Port</th><th>Type</th></tr>'
        '</tbody></table></body></html>'
    )

    def test_extract_ip_with_literal_dot(self):
        from fetcher.sources.proxynova import _extractIpFromScript
        script = 'document.write(atob("MTg1LjE4Ng==")+"."+atob("MTYyLjIxNw=="))'
        assert _extractIpFromScript(script) == "185.186.162.217"

    def test_extract_ip_empty_script(self):
        from fetcher.sources.proxynova import _extractIpFromScript
        assert _extractIpFromScript("") is None
        assert _extractIpFromScript("document.write('x')") is None

    @patch("fetcher.sources.proxynova.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxynova import ProxyNovaFetcher
        tree = etree.HTML(self.HTML)
        mock_wr.return_value.get.return_value = _make_response(
            text=self.HTML, tree=tree)
        result = list(ProxyNovaFetcher().fetch())
        _assert_valid_proxies(result)
        assert "185.186.162.217:8080" in result
        assert result.count("185.186.162.217:8080") == 1  # 去重
        assert "1.2.3.4:1080" not in result               # socks 被过滤

    @patch("fetcher.sources.proxynova.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxynova import ProxyNovaFetcher
        mock_wr.return_value.get.return_value = _make_response(
            tree=etree.HTML("<html></html>"))
        assert list(ProxyNovaFetcher().fetch()) == []

    @patch("fetcher.sources.proxynova.WebRequest")
    def test_fetch_tree_none_returns_empty(self, mock_wr):
        from fetcher.sources.proxynova import ProxyNovaFetcher
        mock_wr.return_value.get.return_value = _make_response(tree=None)
        assert list(ProxyNovaFetcher().fetch()) == []

    @patch("fetcher.sources.proxynova.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.proxynova import ProxyNovaFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyNovaFetcher().fetch()) == []


# --------------- freeproxyworld ---------------

class TestFreeProxyWorldFetcher(object):

    @staticmethod
    def _row(ip, port, proxy_type):
        return (
            '<tr><td>%s</td><td><a href="/?port=%s">%s</a></td>'
            '<td>US</td><td>City</td><td>100 ms</td>'
            '<td><a href="/?type=%s">%s</a></td><td>No</td>'
            '<td>2 minutes</td></tr>'
            % (ip, port, port, proxy_type, proxy_type))

    def _tree(self):
        html = (
            '<table><thead><tr><th>IP Address</th><th>Port</th>'
            '<th>Country</th><th>City</th><th>Speed</th><th>Type</th>'
            '<th>Anonymity</th><th>Last Check</th></tr></thead><tbody>'
            + self._row("1.2.3.4", "8080", "http")
            + self._row("1.2.3.4", "8080", "http")       # 跨页重复
            + self._row("5.6.7.8", "1080", "socks4")    # 过滤
            + '</tbody></table>')
        return etree.HTML(html)

    @patch("fetcher.sources.freeproxyworld.WebRequest")
    @patch("fetcher.sources.freeproxyworld.sleep", return_value=None)
    def test_fetch(self, mock_sleep, mock_wr):
        from fetcher.sources.freeproxyworld import FreeProxyWorldFetcher
        tree = self._tree()
        mock_wr.return_value.get.return_value = _make_response(
            text=str(tree), tree=tree)
        result = list(FreeProxyWorldFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert result.count("1.2.3.4:8080") == 1  # 去重
        assert "5.6.7.8:1080" not in result       # socks 被过滤
        assert mock_wr.return_value.get.call_count == 5
        assert mock_sleep.call_count == 5

    @patch("fetcher.sources.freeproxyworld.WebRequest")
    @patch("fetcher.sources.freeproxyworld.sleep", return_value=None)
    def test_fetch_empty_returns_empty(self, mock_sleep, mock_wr):
        from fetcher.sources.freeproxyworld import FreeProxyWorldFetcher
        mock_wr.return_value.get.return_value = _make_response(
            tree=etree.HTML("<html></html>"))
        assert list(FreeProxyWorldFetcher().fetch()) == []

    @patch("fetcher.sources.freeproxyworld.WebRequest")
    @patch("fetcher.sources.freeproxyworld.sleep", return_value=None)
    def test_fetch_exception_returns_empty(self, mock_sleep, mock_wr):
        from fetcher.sources.freeproxyworld import FreeProxyWorldFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(FreeProxyWorldFetcher().fetch()) == []


# --------------- cnproxy ---------------

class TestCnProxyFetcher(object):

    HTML = (
        '<table><tr><td>1.2.3.4</td><td>8080</td><td>CN</td></tr>'
        '<tr><td>5.6.7.8</td><td>3128</td><td>CN</td></tr></table>')

    @patch("fetcher.sources.cnproxy.WebRequest")
    @patch("fetcher.sources.cnproxy.sleep", return_value=None)
    def test_fetch(self, mock_sleep, mock_wr):
        from fetcher.sources.cnproxy import CnProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(text=self.HTML)
        result = list(CnProxyFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        # 两个页面返回相同数据, 应去重
        assert result.count("1.2.3.4:8080") == 1
        assert mock_wr.return_value.get.call_count == 2

    @patch("fetcher.sources.cnproxy.WebRequest")
    @patch("fetcher.sources.cnproxy.sleep", return_value=None)
    def test_fetch_empty_returns_empty(self, mock_sleep, mock_wr):
        from fetcher.sources.cnproxy import CnProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(CnProxyFetcher().fetch()) == []

    @patch("fetcher.sources.cnproxy.WebRequest")
    @patch("fetcher.sources.cnproxy.sleep", return_value=None)
    def test_fetch_exception_returns_empty(self, mock_sleep, mock_wr):
        from fetcher.sources.cnproxy import CnProxyFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(CnProxyFetcher().fetch()) == []


# --------------- freeproxylistsnet ---------------

class TestFreeProxyListsNetFetcher(object):

    HTML = (
        '<table><tbody>'
        '<tr class="Odd"><td><script>document.write(unescape('
        "'%31%2E%32%2E%33%2E%34'))</script></td>"
        '<td>8080</td><td>HTTP</td></tr>'
        '<tr class="Even"><td>5.6.7.8</td><td>3128</td><td>HTTPS</td></tr>'
        '<tr class="Odd"><td>1.2.3.4</td><td>1080</td><td>SOCKS5</td></tr>'
        '</tbody></table>')

    @patch("fetcher.sources.freeproxylistsnet.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.freeproxylistsnet import FreeProxyListsNetFetcher
        tree = etree.HTML(self.HTML)
        mock_wr.return_value.get.return_value = _make_response(
            text=self.HTML, tree=tree)
        result = list(FreeProxyListsNetFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "1.2.3.4:1080" not in result  # socks 被过滤

    @patch("fetcher.sources.freeproxylistsnet.WebRequest")
    def test_fetch_text_fallback(self, mock_wr):
        from fetcher.sources.freeproxylistsnet import FreeProxyListsNetFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="9.9.9.9:3128", tree=etree.HTML("<html></html>"))
        result = list(FreeProxyListsNetFetcher().fetch())
        assert "9.9.9.9:3128" in result

    @patch("fetcher.sources.freeproxylistsnet.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.freeproxylistsnet import FreeProxyListsNetFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML("<html></html>"))
        assert list(FreeProxyListsNetFetcher().fetch()) == []

    @patch("fetcher.sources.freeproxylistsnet.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.freeproxylistsnet import FreeProxyListsNetFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(FreeProxyListsNetFetcher().fetch()) == []


# --------------- binglx ---------------

class TestBinglxFetcher(object):

    HTML = (
        '<table><tbody>'
        '<tr><th>IP</th><th>Port</th><th>Country</th></tr>'
        '<tr><td>1.2.3.4</td><td>8080</td><td>CN</td></tr>'
        '<tr><td>1.2.3.4</td><td>8080</td><td>CN</td></tr>'
        '</tbody></table>')

    @patch("fetcher.sources.binglx.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.binglx import BinglxFetcher
        tree = etree.HTML(self.HTML)
        mock_wr.return_value.get.return_value = _make_response(
            text=self.HTML, tree=tree)
        result = list(BinglxFetcher().fetch())
        _assert_valid_proxies(result)
        assert result == ["1.2.3.4:8080"]  # 解析且去重

    @patch("fetcher.sources.binglx.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.binglx import BinglxFetcher
        mock_wr.return_value.get.return_value = _make_response(
            tree=etree.HTML("<html></html>"))
        assert list(BinglxFetcher().fetch()) == []

    @patch("fetcher.sources.binglx.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.binglx import BinglxFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(BinglxFetcher().fetch()) == []


# --------------- jiangxianli ---------------

class TestJiangxianliFetcher(object):

    HTML = (
        '<table><tbody>'
        '<tr><th>IP</th><th>Port</th><th>Country</th></tr>'
        '<tr><td>1.2.3.4</td><td>8080</td><td>中国</td></tr>'
        '<tr><td>5.6.7.8</td><td>3128</td><td>中国</td></tr>'
        '</tbody></table>')

    @patch("fetcher.sources.jiangxianli.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.jiangxianli import JiangxianliFetcher
        tree = etree.HTML(self.HTML)
        mock_wr.return_value.get.return_value = _make_response(
            text=self.HTML, tree=tree)
        result = list(JiangxianliFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.jiangxianli.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.jiangxianli import JiangxianliFetcher
        mock_wr.return_value.get.return_value = _make_response(
            tree=etree.HTML("<html></html>"))
        assert list(JiangxianliFetcher().fetch()) == []

    @patch("fetcher.sources.jiangxianli.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.jiangxianli import JiangxianliFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(JiangxianliFetcher().fetch()) == []


# --------------- proxyelite ---------------

class TestProxyEliteFetcher(object):

    HTML = (
        '<html><head><script>var proxylister_ajax = '
        '{"ajax_url":"https://proxyelite.info/wp-admin/admin-ajax.php",'
        '"nonce":"abc123"};</script></head><body><table><tbody>'
        '<tr class="fpb-row" data-ix="0" data-protos="HTTP|SOCKS4|SOCKS5">'
        '<td><button data-ip="1.2.3.4" data-port="8080">Copy</button></td></tr>'
        '<tr class="fpb-row" data-ix="1" data-protos="HTTPS">'
        '<td><button data-ip="5.6.7.8" data-port="3128">Copy</button></td></tr>'
        '<tr class="fpb-row" data-ix="2" data-protos="SOCKS4|SOCKS5">'
        '<td><button data-ip="9.9.9.9" data-port="1080">Copy</button></td></tr>'
        '</tbody></table></body></html>')

    @patch("fetcher.sources.proxyelite.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxyelite import ProxyEliteFetcher
        tree = etree.HTML(self.HTML)
        mock_wr.return_value.get.return_value = _make_response(
            text=self.HTML, tree=tree)
        mock_wr.return_value.post.return_value = _make_response(json_data={})
        result = list(ProxyEliteFetcher().fetch())
        _assert_valid_proxies(result)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "9.9.9.9:1080" not in result  # socks-only 被过滤

    @patch("fetcher.sources.proxyelite.WebRequest")
    def test_fetch_posts_nonce(self, mock_wr):
        from fetcher.sources.proxyelite import ProxyEliteFetcher
        tree = etree.HTML(self.HTML)
        mock_wr.return_value.get.return_value = _make_response(
            text=self.HTML, tree=tree)
        mock_wr.return_value.post.return_value = _make_response(json_data={})
        list(ProxyEliteFetcher().fetch())
        _, kwargs = mock_wr.return_value.post.call_args
        assert kwargs["data"]["nonce"] == "abc123"
        assert kwargs["data"]["action"] == "proxylister_load_more"

    @patch("fetcher.sources.proxyelite.WebRequest")
    def test_fetch_uses_post_rows_and_dedup(self, mock_wr):
        from fetcher.sources.proxyelite import ProxyEliteFetcher
        # 首页无行, 仅 nonce; 数据来自 POST rows
        tree = etree.HTML("<html></html>")
        mock_wr.return_value.get.return_value = _make_response(
            text='{"nonce":"abc123"}', tree=tree)
        rows = ('<table><tr data-ix="0" data-protos="HTTP">'
                '<td><button data-ip="8.8.8.8" data-port="8888"></button></td>'
                '</tr><tr data-ix="1" data-protos="HTTP">'
                '<td><button data-ip="8.8.8.8" data-port="8888"></button></td>'
                '</tr></table>')
        mock_wr.return_value.post.return_value = _make_response(
            json_data={"success": True,
                       "data": {"rows": rows, "count": 1}})
        result = list(ProxyEliteFetcher().fetch())
        assert result == ["8.8.8.8:8888"]  # 去重

    @patch("fetcher.sources.proxyelite.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxyelite import ProxyEliteFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML("<html></html>"))
        assert list(ProxyEliteFetcher().fetch()) == []

    @patch("fetcher.sources.proxyelite.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.proxyelite import ProxyEliteFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyEliteFetcher().fetch()) == []


# --------------- usproxy ---------------

class TestUsProxyFetcher(object):

    HTML = (
        '<html><body><table><tbody>'
        '<tr><td>1.2.3.4</td><td>8080</td><td>US</td></tr>'
        '<tr><td>1.2.3.4</td><td>8080</td><td>US</td></tr>'
        '<tr><td>5.6.7.8</td><td>3128</td><td>US</td></tr>'
        '</tbody></table></body></html>')

    @patch("fetcher.sources.usproxy.WebRequest")
    def test_fetch_tbody(self, mock_wr):
        from fetcher.sources.usproxy import UsProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(text=self.HTML)
        result = list(UsProxyFetcher().fetch())
        _assert_valid_proxies(result)
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]  # 去重

    @patch("fetcher.sources.usproxy.WebRequest")
    def test_fetch_regex_fallback(self, mock_wr):
        from fetcher.sources.usproxy import UsProxyFetcher
        text = '<td>1.2.3.4</td><td>8080</td>'
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(UsProxyFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.usproxy.WebRequest")
    def test_fetch_plain_text_fallback(self, mock_wr):
        from fetcher.sources.usproxy import UsProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="9.9.9.9:3128")
        result = list(UsProxyFetcher().fetch())
        assert "9.9.9.9:3128" in result

    @patch("fetcher.sources.usproxy.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.usproxy import UsProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(UsProxyFetcher().fetch()) == []

    @patch("fetcher.sources.usproxy.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.usproxy import UsProxyFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(UsProxyFetcher().fetch()) == []
