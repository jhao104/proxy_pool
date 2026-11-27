# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_api.py
   Description :   api 组代理源 fetcher 测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 api 组代理源测试
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
    """验证所有 proxy 符合 ip:port 格式且为 str"""
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')
    for p in proxies:
        assert isinstance(p, str), "proxy should be str: %r" % (p,)
        assert pattern.match(p), "Invalid proxy format: %s" % p


# --------------- 接口约定测试 ---------------

class TestFetcherInterface(object):
    """本组所有 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.parserpp", "ParserppFetcher"),
        ("fetcher.sources.charlespikachu", "CharlesPikachuFetcher"),
        ("fetcher.sources.proxyscrape", "ProxyScrapeFetcher"),
        ("fetcher.sources.proxylistdownload", "ProxyListDownloadFetcher"),
        ("fetcher.sources.fatezero", "FateZeroFetcher"),
        ("fetcher.sources.proxydb", "ProxydbFetcher"),
        ("fetcher.sources.geoxy", "GeoxyFetcher"),
        ("fetcher.sources.pzzqz", "PzzqzFetcher"),
    ]

    def test_all_fetchers_subclass_base(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert issubclass(cls, BaseFetcher), "%s not subclass of BaseFetcher" % class_name

    def test_all_fetchers_have_name_url_enabled(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name, "%s missing name" % class_name
            assert cls.url, "%s missing url" % class_name
            assert hasattr(cls, 'enabled'), "%s missing enabled" % class_name

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), "%s missing fetch method" % class_name
            assert callable(cls.fetch)

    def test_names_are_unique_and_lowercase(self):
        names = []
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name == cls.name.lower(), "%s name not lowercase" % class_name
            names.append(cls.name)
        assert len(names) == len(set(names))


# --------------- parserpp ---------------

class TestParserppFetcher(object):

    @patch("fetcher.sources.parserpp.WebRequest")
    def test_fetch_dict_format(self, mock_wr):
        """{分类名: [{host, port, protocol}, ...]} 格式"""
        from fetcher.sources.parserpp import ParserppFetcher
        json_data = {
            "http": [
                {"host": "1.2.3.4", "port": 8080, "protocol": "http"},
                {"host": "5.6.7.8", "port": 3128},
            ],
            "socks5": [
                {"host": "9.9.9.9", "port": 1080, "protocol": "socks5"},
            ],
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ParserppFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "9.9.9.9:1080" not in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.parserpp.WebRequest")
    def test_fetch_jsonl_format(self, mock_wr):
        """实测格式为 JSONL(每行一个 JSON), json 解析失败时回退解析 text"""
        from fetcher.sources.parserpp import ParserppFetcher
        text = ('{"type": "http", "host": "1.2.3.4", "port": 8080}\n'
                '{"type": "https", "host": "5.6.7.8", "port": 3128}\n'
                '{"type": "socks4", "host": "9.9.9.9", "port": 1080}\n'
                '\n'
                'not-json-line\n')
        mock_wr.return_value.get.return_value = _make_response(
            text=text, json_data={})
        result = list(ParserppFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "9.9.9.9:1080" not in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.parserpp.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.parserpp import ParserppFetcher
        json_data = {"http": [
            {"host": "1.2.3.4", "port": 8080},
            {"host": "1.2.3.4", "port": 8080},
        ]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ParserppFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.parserpp.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.parserpp import ParserppFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="", json_data={})
        assert list(ParserppFetcher().fetch()) == []

    @patch("fetcher.sources.parserpp.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr):
        from fetcher.sources.parserpp import ParserppFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ParserppFetcher().fetch()) == []

    @patch("fetcher.sources.parserpp.WebRequest")
    def test_request_contract(self, mock_wr):
        """使用 timeout=10, retry_time=1"""
        from fetcher.sources.parserpp import ParserppFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        list(ParserppFetcher().fetch())
        kwargs = mock_wr.return_value.get.call_args[1]
        assert kwargs.get("timeout") == 10
        assert kwargs.get("retry_time") == 1


# --------------- charlespikachu ---------------

class TestCharlesPikachuFetcher(object):

    @patch("fetcher.sources.charlespikachu.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.charlespikachu import CharlesPikachuFetcher
        json_data = {"data": [
            {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
            {"ip": "5.6.7.8", "port": 3128, "protocol": "Https"},
            {"ip": "6.6.6.6", "port": 8000, "protocol": "Http, Https"},
        ]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(CharlesPikachuFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "6.6.6.6:8000" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.charlespikachu.WebRequest")
    def test_fetch_filters_socks(self, mock_wr):
        from fetcher.sources.charlespikachu import CharlesPikachuFetcher
        json_data = {"data": [
            {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
            {"ip": "9.9.9.9", "port": 1080, "protocol": "Socks5"},
            {"ip": "8.8.8.8", "port": 1081, "protocol": "Socks4, Socks5"},
        ]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(CharlesPikachuFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:1080" not in result
        assert "8.8.8.8:1081" not in result

    @patch("fetcher.sources.charlespikachu.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.charlespikachu import CharlesPikachuFetcher
        json_data = {"data": [
            {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
            {"ip": "1.2.3.4", "port": 8080, "protocol": "Http, Https"},
        ]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(CharlesPikachuFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.charlespikachu.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.charlespikachu import CharlesPikachuFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        assert list(CharlesPikachuFetcher().fetch()) == []

    @patch("fetcher.sources.charlespikachu.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr):
        from fetcher.sources.charlespikachu import CharlesPikachuFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(CharlesPikachuFetcher().fetch()) == []


# --------------- proxyscrape ---------------

class TestProxyScrapeFetcher(object):

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        text = "1.2.3.4:8080\n5.6.7.8:3128\n\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyScrapeFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        text = "1.2.3.4:8080\n1.2.3.4:8080\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyScrapeFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxyScrapeFetcher().fetch()) == []

    @patch("fetcher.sources.proxyscrape.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr):
        from fetcher.sources.proxyscrape import ProxyScrapeFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyScrapeFetcher().fetch()) == []


# --------------- proxylistdownload ---------------

class TestProxyListDownloadFetcher(object):

    @patch("fetcher.sources.proxylistdownload.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxylistdownload import ProxyListDownloadFetcher
        text = "1.2.3.4:8080\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyListDownloadFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.proxylistdownload.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.proxylistdownload import ProxyListDownloadFetcher
        text = "1.2.3.4:8080\n1.2.3.4:8080\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(ProxyListDownloadFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxylistdownload.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxylistdownload import ProxyListDownloadFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(ProxyListDownloadFetcher().fetch()) == []

    @patch("fetcher.sources.proxylistdownload.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr):
        from fetcher.sources.proxylistdownload import ProxyListDownloadFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(ProxyListDownloadFetcher().fetch()) == []


# --------------- fatezero ---------------

class TestFateZeroFetcher(object):

    @patch("fetcher.sources.fatezero.WebRequest")
    def test_fetch_filters_cn(self, mock_wr):
        from fetcher.sources.fatezero import FateZeroFetcher
        text = (
            '{"host": "1.2.3.4", "port": 8080, "country": "CN"}\n'
            '{"host": "5.6.7.8", "port": 3128, "country": "US"}\n'
            '{"host": "9.9.9.9", "port": 1080, "country": "CN"}\n'
        )
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(FateZeroFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:1080" in result
        assert "5.6.7.8:3128" not in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.fatezero.WebRequest")
    def test_fetch_skips_bad_lines(self, mock_wr):
        from fetcher.sources.fatezero import FateZeroFetcher
        text = (
            '\n'
            'not-json\n'
            '{"host": "1.2.3.4", "port": 8080, "country": "CN"}\n'
            'null\n'
            '\n'
        )
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(FateZeroFetcher().fetch())
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.fatezero.WebRequest")
    def test_fetch_dedup(self, mock_wr):
        from fetcher.sources.fatezero import FateZeroFetcher
        text = ('{"host": "1.2.3.4", "port": 8080, "country": "CN"}\n'
                '{"host": "1.2.3.4", "port": 8080, "country": "CN"}\n')
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(FateZeroFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.fatezero.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.fatezero import FateZeroFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(FateZeroFetcher().fetch()) == []

    @patch("fetcher.sources.fatezero.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr):
        from fetcher.sources.fatezero import FateZeroFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(FateZeroFetcher().fetch()) == []


# --------------- proxydb ---------------

class TestProxydbFetcher(object):

    @patch("fetcher.sources.proxydb.WebRequest")
    def test_fetch_json(self, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        json_data = {"proxies": [
            {"ip": "1.2.3.4", "port": 8080, "protocol": "http"},
            {"ip": "5.6.7.8", "port": 3128, "protocol": "https"},
            {"ip": "9.9.9.9", "port": 1080, "protocol": "socks5"},
        ]}
        mock_wr.return_value.post.return_value = _make_response(json_data=json_data)
        result = list(ProxydbFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "9.9.9.9:1080" not in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.proxydb.WebRequest")
    def test_fetch_two_pages_and_dedup(self, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        json_data = {"proxies": [
            {"ip": "1.2.3.4", "port": 8080, "protocol": "http"},
        ]}
        mock_wr.return_value.post.return_value = _make_response(json_data=json_data)
        result = list(ProxydbFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1
        offsets = [c[1]["json"]["offset"]
                   for c in mock_wr.return_value.post.call_args_list]
        assert offsets == [0, 30]

    @patch("fetcher.sources.proxydb.WebRequest")
    def test_fetch_html_fallback(self, mock_wr):
        """/list 接口 404 时回退解析首页 HTML 表格"""
        from fetcher.sources.proxydb import ProxydbFetcher
        html = ('<table><tr><th>IP</th><th>Port</th><th>Protocol</th></tr>'
                '<tr><td>1.2.3.4</td><td><a href="/1.2.3.4/8080">8080</a></td>'
                '<td>HTTP</td></tr>'
                '<tr><td>5.6.7.8</td><td><a>1080</a></td><td>SOCKS5</td></tr>'
                '</table>')
        tree = etree.HTML(html)
        mock_wr.return_value.post.return_value = _make_response(json_data={})
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(ProxydbFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:1080" not in result
        assert mock_wr.return_value.get.call_count == 2

    @patch("fetcher.sources.proxydb.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        mock_wr.return_value.post.return_value = _make_response(json_data={})
        mock_wr.return_value.get.return_value = _make_response(tree=None)
        assert list(ProxydbFetcher().fetch()) == []

    @patch("fetcher.sources.proxydb.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        mock_wr.return_value.post.side_effect = RuntimeError("boom")
        assert list(ProxydbFetcher().fetch()) == []

    @patch("fetcher.sources.proxydb.WebRequest")
    def test_post_contract(self, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        mock_wr.return_value.post.return_value = _make_response(
            json_data={"proxies": []})
        list(ProxydbFetcher().fetch())
        kwargs = mock_wr.return_value.post.call_args_list[0][1]
        assert kwargs.get("json") == {
            "protocols": [], "anonlvls": [], "offset": 0}
        assert kwargs.get("timeout") == 10
        assert kwargs.get("retry_time") == 1


# --------------- geoxy ---------------

class TestGeoxyFetcher(object):

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.geoxy import GeoxyFetcher
        json_data = [
            {"address": "1.2.3.4:8080", "protocols": ["http"]},
            {"address": "5.6.7.8:3128", "protocols": ["https"]},
            {"address": "9.9.9.9:1080", "protocols": ["socks5"]},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GeoxyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "9.9.9.9:1080" not in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_fetch_stops_on_empty_page(self, mock_wr, mock_sleep):
        """空数据(疑似 token 过期)时停止翻页"""
        from fetcher.sources.geoxy import GeoxyFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data=[])
        result = list(GeoxyFetcher().fetch())
        assert result == []
        assert mock_wr.return_value.get.call_count == 1

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_fetch_stops_on_unauthorized(self, mock_wr, mock_sleep):
        """401/403 时 json 不是列表, 不抛异常且停止翻页"""
        from fetcher.sources.geoxy import GeoxyFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(GeoxyFetcher().fetch())
        assert result == []
        assert mock_wr.return_value.get.call_count == 1

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_fetch_pages_and_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.geoxy import GeoxyFetcher
        page = [{"address": "1.2.3.4:8080", "protocols": ["http"]}]

        def side_effect(url, **kwargs):
            if "page=3" in url:
                return _make_response(json_data=[])
            return _make_response(json_data=page)

        mock_wr.return_value.get.side_effect = side_effect
        result = list(GeoxyFetcher().fetch())
        assert result == ["1.2.3.4:8080"]
        assert mock_wr.return_value.get.call_count == 3

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_fetch_exception_no_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.geoxy import GeoxyFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(GeoxyFetcher().fetch()) == []

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_request_contract(self, mock_wr, mock_sleep):
        """带上 authorization 请求头, timeout=10, retry_time=1"""
        from fetcher.sources.geoxy import GeoxyFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data=[])
        list(GeoxyFetcher().fetch())
        kwargs = mock_wr.return_value.get.call_args[1]
        assert kwargs["header"]["authorization"]
        assert kwargs.get("timeout") == 10
        assert kwargs.get("retry_time") == 1
        assert kwargs.get("verify") is False

    @patch("fetcher.sources.geoxy.sleep", return_value=None)
    @patch("fetcher.sources.geoxy.WebRequest")
    def test_max_pages(self, mock_wr, mock_sleep):
        """最多请求 16 页"""
        from fetcher.sources.geoxy import GeoxyFetcher
        page = [{"address": "1.2.3.4:8080", "protocols": ["http"]}]
        mock_wr.return_value.get.return_value = _make_response(json_data=page)
        result = list(GeoxyFetcher().fetch())
        assert mock_wr.return_value.get.call_count == 16
        assert result == ["1.2.3.4:8080"]


# --------------- pzzqz ---------------

class TestPzzqzFetcher(object):

    @staticmethod
    def _make_session(token='X-CSRFToken": "abc123"', proxy_html=None):
        session = MagicMock()
        index_resp = MagicMock()
        index_resp.text = '<script>var x = {%s};</script>' % token
        proxy_resp = MagicMock()
        proxy_resp.json.return_value = {"proxy_html": proxy_html or ""}
        session.get.return_value = index_resp
        session.post.return_value = proxy_resp
        return session

    @patch("fetcher.sources.pzzqz.requests")
    def test_fetch(self, mock_requests):
        from fetcher.sources.pzzqz import PzzqzFetcher
        proxy_html = ('<table><tr><td>1.2.3.4</td><td>8080</td></tr>'
                      '<tr><td>5.6.7.8</td><td>3128</td></tr></table>')
        mock_requests.Session.return_value = self._make_session(proxy_html=proxy_html)
        result = list(PzzqzFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.pzzqz.requests")
    def test_fetch_dedup(self, mock_requests):
        from fetcher.sources.pzzqz import PzzqzFetcher
        proxy_html = ('<table><tr><td>1.2.3.4</td><td>8080</td></tr>'
                      '<tr><td>1.2.3.4</td><td>8080</td></tr></table>')
        mock_requests.Session.return_value = self._make_session(proxy_html=proxy_html)
        result = list(PzzqzFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.pzzqz.requests")
    def test_fetch_no_token_returns_empty(self, mock_requests):
        from fetcher.sources.pzzqz import PzzqzFetcher
        session = self._make_session(token='__no_token__')
        index_resp = MagicMock()
        index_resp.text = "<html>no token</html>"
        session.get.return_value = index_resp
        mock_requests.Session.return_value = session
        result = list(PzzqzFetcher().fetch())
        assert result == []
        assert not session.post.called

    @patch("fetcher.sources.pzzqz.requests")
    def test_fetch_empty_html_returns_empty(self, mock_requests):
        from fetcher.sources.pzzqz import PzzqzFetcher
        mock_requests.Session.return_value = self._make_session(proxy_html="")
        assert list(PzzqzFetcher().fetch()) == []

    @patch("fetcher.sources.pzzqz.requests")
    def test_fetch_exception_no_raise(self, mock_requests):
        from fetcher.sources.pzzqz import PzzqzFetcher
        mock_requests.Session.side_effect = RuntimeError("boom")
        assert list(PzzqzFetcher().fetch()) == []

    @patch("fetcher.sources.pzzqz.requests")
    def test_post_payload_and_token_header(self, mock_requests):
        from fetcher.sources.pzzqz import PzzqzFetcher
        session = self._make_session(proxy_html="")
        mock_requests.Session.return_value = session
        list(PzzqzFetcher().fetch())
        args, kwargs = session.post.call_args
        assert kwargs["headers"]["X-CSRFToken"] == "abc123"
        assert kwargs["json"] == {
            "http": "on", "ping": "3000", "country": "cn", "ports": ""}
        assert kwargs.get("timeout") == 10

    def test_enabled_is_false(self):
        """实测域名无法解析, 应禁用"""
        from fetcher.sources.pzzqz import PzzqzFetcher
        assert PzzqzFetcher.enabled is False
