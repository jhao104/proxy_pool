# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_meta.py
   Description :   MetaPool/ProxyStatus/IhuanToday/Ip89Web 代理源测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增本组代理源测试
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
    for p in proxies:
        assert pattern.match(p), "Invalid proxy format: %s" % p


# --------------- 接口约定测试 ---------------

class TestMetaFetcherInterface(object):
    """本组 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.metapool", "MetaPoolFetcher"),
        ("fetcher.sources.proxystatus", "ProxyStatusFetcher"),
        ("fetcher.sources.ihuan_today", "IhuanTodayFetcher"),
        ("fetcher.sources.ip89_web", "Ip89WebFetcher"),
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
            assert issubclass(cls, BaseFetcher), "%s not subclass of BaseFetcher" % class_name

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), "%s missing fetch method" % class_name

    def test_aggregate_sources_disabled_by_default(self):
        """聚合类源默认关闭, 避免来源不可控/循环抓取"""
        from fetcher.sources.metapool import MetaPoolFetcher
        from fetcher.sources.proxystatus import ProxyStatusFetcher
        assert MetaPoolFetcher.enabled is False
        assert ProxyStatusFetcher.enabled is False


# --------------- MetaPool ---------------

class TestMetaPoolFetcher(object):

    @patch("fetcher.sources.metapool.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.metapool import MetaPoolFetcher

        def side_effect(url, **kwargs):
            if "152.69.217.58" in url:
                return _make_response(json_data=[
                    {"proxy": "1.2.3.4:8080"},
                    {"proxy": "5.6.7.8:3128"},
                ])
            if "117.72.44.211" in url:
                raise RuntimeError("boom")
            return _make_response(json_data={}, text="")

        mock_wr.return_value.get.side_effect = side_effect
        result = list(MetaPoolFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.metapool.WebRequest")
    def test_fetch_dedup_across_urls(self, mock_wr):
        from fetcher.sources.metapool import MetaPoolFetcher
        mock_wr.return_value.get.return_value = _make_response(
            json_data=[{"proxy": "1.2.3.4:8080"}])
        result = list(MetaPoolFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.metapool.WebRequest")
    def test_fetch_text_fallback(self, mock_wr):
        from fetcher.sources.metapool import MetaPoolFetcher
        mock_wr.return_value.get.return_value = _make_response(
            json_data={}, text="1.2.3.4:8080 5.6.7.8:3128")
        result = list(MetaPoolFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.metapool.WebRequest")
    def test_fetch_ignores_non_dict_items(self, mock_wr):
        from fetcher.sources.metapool import MetaPoolFetcher
        mock_wr.return_value.get.return_value = _make_response(
            json_data=[{"proxy": "1.2.3.4:8080"}, "bad", None])
        result = list(MetaPoolFetcher().fetch())
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.metapool.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.metapool import MetaPoolFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data=[], text="")
        result = list(MetaPoolFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.metapool.WebRequest")
    def test_fetch_all_fail_returns_empty(self, mock_wr):
        from fetcher.sources.metapool import MetaPoolFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        result = list(MetaPoolFetcher().fetch())
        assert result == []


# --------------- ProxyStatus ---------------

class TestProxyStatusFetcher(object):

    @patch("fetcher.sources.proxystatus.WebRequest")
    def test_fetch_filters_non_http(self, mock_wr):
        from fetcher.sources.proxystatus import ProxyStatusFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={
            "proxies": [
                {"ip": "1.2.3.4", "port": 8080, "protocol": "HTTP"},
                {"ip": "5.6.7.8", "port": 3128, "protocol": "HTTPS"},
                {"ip": "9.9.9.9", "port": 1080, "protocol": "SOCKS5"},
            ]
        })
        result = list(ProxyStatusFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert "9.9.9.9:1080" not in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.proxystatus.WebRequest")
    def test_fetch_protocol_case_insensitive(self, mock_wr):
        from fetcher.sources.proxystatus import ProxyStatusFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={
            "proxies": [{"ip": "1.2.3.4", "port": 8080, "protocol": "http"}]
        })
        result = list(ProxyStatusFetcher().fetch())
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.proxystatus.WebRequest")
    def test_fetch_dedup_across_urls(self, mock_wr):
        from fetcher.sources.proxystatus import ProxyStatusFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={
            "proxies": [{"ip": "1.2.3.4", "port": 8080, "protocol": "HTTP"}]
        })
        result = list(ProxyStatusFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.proxystatus.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.proxystatus import ProxyStatusFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(ProxyStatusFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.proxystatus.WebRequest")
    def test_fetch_all_fail_returns_empty(self, mock_wr):
        from fetcher.sources.proxystatus import ProxyStatusFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        result = list(ProxyStatusFetcher().fetch())
        assert result == []


# --------------- IhuanToday ---------------

class TestIhuanTodayFetcher(object):

    @patch("fetcher.sources.ihuan_today.requests")
    def test_fetch_table(self, mock_requests):
        from fetcher.sources.ihuan_today import IhuanTodayFetcher
        html = (
            '<table class="table table-hover table-bordered">'
            '<tr><td>1.2.3.4</td><td>8080</td></tr>'
            '<tr><td>5.6.7.8</td><td>3128</td></tr>'
            '</table>'
        )
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_session.get.return_value = mock_resp
        mock_requests.session.return_value = mock_session

        result = list(IhuanTodayFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        # 先取 cookie, 再取今日代理页
        assert mock_session.get.call_count == 2

    @patch("fetcher.sources.ihuan_today.requests")
    def test_fetch_dedup(self, mock_requests):
        from fetcher.sources.ihuan_today import IhuanTodayFetcher
        html = (
            '<table class="table table-hover table-bordered">'
            '<tr><td>1.2.3.4</td><td>8080</td></tr>'
            '<tr><td>1.2.3.4</td><td>8080</td></tr>'
            '</table>'
        )
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_requests.session.return_value.get.return_value = mock_resp

        result = list(IhuanTodayFetcher().fetch())
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.ihuan_today.requests")
    def test_fetch_hourly_page_fallback(self, mock_requests):
        from fetcher.sources.ihuan_today import IhuanTodayFetcher
        today_html = (
            '<div class="bs-callout bs-callout-info">'
            '<a href="/today/2026/11/21/23.html">2026年11月21日23时</a></div>'
        )

        def side_effect(url, **kwargs):
            resp = MagicMock()
            if url.endswith("today.html"):
                resp.text = today_html
            elif "/today/2026/11/21/23.html" in url:
                resp.text = "1.2.3.4:8080<br>5.6.7.8:3128"
            else:
                resp.text = ""
            return resp

        mock_session = MagicMock()
        mock_session.get.side_effect = side_effect
        mock_requests.session.return_value = mock_session

        result = list(IhuanTodayFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.ihuan_today.requests")
    def test_fetch_empty_returns_empty(self, mock_requests):
        from fetcher.sources.ihuan_today import IhuanTodayFetcher
        mock_resp = MagicMock()
        mock_resp.text = ""
        mock_requests.session.return_value.get.return_value = mock_resp
        result = list(IhuanTodayFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.ihuan_today.requests")
    def test_fetch_exception_returns_empty(self, mock_requests):
        from fetcher.sources.ihuan_today import IhuanTodayFetcher
        mock_requests.session.return_value.get.side_effect = RuntimeError("boom")
        result = list(IhuanTodayFetcher().fetch())
        assert result == []


# --------------- Ip89Web ---------------

class TestIp89WebFetcher(object):

    @patch("fetcher.sources.ip89_web.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.ip89_web import Ip89WebFetcher
        text = ('<a href="https://www.qiyunip.com/">ad</a><br>'
                '1.2.3.4:8080<br>5.6.7.8:3128<br>1.2.3.4:8080')
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(Ip89WebFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert result.count("1.2.3.4:8080") == 1  # 去重
        _assert_valid_proxies(result)

    @patch("fetcher.sources.ip89_web.WebRequest")
    def test_fetch_request_params(self, mock_wr):
        from fetcher.sources.ip89_web import Ip89WebFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        list(Ip89WebFetcher().fetch())
        kwargs = mock_wr.return_value.get.call_args[1]
        assert kwargs["params"]["num"] == "9999"
        assert kwargs["header"]["Referer"] == "https://www.89ip.cn/ti.html"
        assert kwargs["timeout"] == 10
        assert kwargs["retry_time"] == 1

    @patch("fetcher.sources.ip89_web.WebRequest")
    def test_fetch_empty_returns_empty(self, mock_wr):
        from fetcher.sources.ip89_web import Ip89WebFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        result = list(Ip89WebFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.ip89_web.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.ip89_web import Ip89WebFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        result = list(Ip89WebFetcher().fetch())
        assert result == []
