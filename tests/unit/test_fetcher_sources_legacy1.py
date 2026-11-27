# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_legacy1.py
   Description :   legacy1 组各代理源 fetcher 测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 legacy1 组代理源测试
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


def _html_table(rows, has_header=False):
    """快速生成 HTML table 字符串"""
    html = "<table>"
    if has_header:
        html += "<tr><th>IP</th><th>Port</th></tr>"
    for ip, port in rows:
        html += "<tr><td>%s</td><td>%s</td></tr>" % (ip, port)
    html += "</table>"
    return html


def _assert_valid_proxies(proxies):
    """验证所有 proxy 为字符串且符合 ip:port 格式"""
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')
    for p in proxies:
        assert isinstance(p, str), "proxy is not str: %r" % (p,)
        assert pattern.match(p), "Invalid proxy format: %s" % p


FETCHER_CLASSES = [
    ("fetcher.sources.coderbusy", "CoderBusyFetcher"),
    ("fetcher.sources.iphai", "IphaiFetcher"),
    ("fetcher.sources.xicidaili", "XicidailiFetcher"),
    ("fetcher.sources.data5u", "Data5uFetcher"),
    ("fetcher.sources.goubanjia", "GoubanjiaFetcher"),
    ("fetcher.sources.spysone", "SpysOneFetcher"),
    ("fetcher.sources.webanetlabs", "WebanetlabsFetcher"),
    ("fetcher.sources.aliveproxy", "AliveProxyFetcher"),
]


# --------------- 接口约定测试 ---------------

class TestFetcherInterface(object):
    """所有 fetcher 的接口约定"""

    def test_all_fetchers_have_name_url_enabled(self):
        for module_path, class_name in FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name, "%s missing name" % class_name
            assert cls.url, "%s missing url" % class_name
            assert hasattr(cls, 'enabled'), "%s missing enabled" % class_name

    def test_all_fetchers_subclass_base(self):
        for module_path, class_name in FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert issubclass(cls, BaseFetcher), "%s not subclass of BaseFetcher" % class_name

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), "%s missing fetch method" % class_name

    def test_names_are_unique_and_enabled_flags(self):
        expected = {
            "coderbusy": False,
            "iphai": False,
            "xicidaili": False,
            "data5u": False,
            "goubanjia": False,
            "spysone": False,
            "webanetlabs": True,
            "aliveproxy": False,
        }
        names = []
        for module_path, class_name in FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            names.append(cls.name)
            assert expected[cls.name] is bool(cls.enabled)
        assert len(names) == len(set(names))


# --------------- 各 fetcher 逻辑测试 ---------------

class TestCoderBusyFetcher(object):

    @patch("fetcher.sources.coderbusy.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.coderbusy import CoderBusyFetcher
        html = _html_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")],
                           has_header=True)
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        result = list(CoderBusyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.coderbusy.WebRequest")
    def test_fetch_text_fallback_and_dedup(self, mock_wr):
        from fetcher.sources.coderbusy import CoderBusyFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080\n1.2.3.4:8080\n5.6.7.8:3128", tree=None)
        result = list(CoderBusyFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.coderbusy.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.coderbusy import CoderBusyFetcher
        mock_wr.return_value.get.return_value = _make_response(text="", tree=None)
        assert list(CoderBusyFetcher().fetch()) == []

    @patch("fetcher.sources.coderbusy.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.coderbusy import CoderBusyFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(CoderBusyFetcher().fetch()) == []


class TestIphaiFetcher(object):

    @patch("fetcher.sources.iphai.sleep", return_value=None)
    @patch("fetcher.sources.iphai.WebRequest")
    def test_fetch_all_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.iphai import IphaiFetcher
        html = ('<tr><td>1.2.3.4</td><td>8080</td></tr>'
                '<tr><td>5.6.7.8</td><td>3128</td></tr>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(IphaiFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)
        # 四个页面, 页面之间 sleep 3 次
        assert mock_wr.return_value.get.call_count == 4
        assert mock_sleep.call_count == 3
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 2

    @patch("fetcher.sources.iphai.sleep", return_value=None)
    @patch("fetcher.sources.iphai.WebRequest")
    def test_dedup_across_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.iphai import IphaiFetcher
        html = '<tr><td>1.2.3.4</td><td>8080</td></tr>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(IphaiFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.iphai.sleep", return_value=None)
    @patch("fetcher.sources.iphai.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.iphai import IphaiFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(IphaiFetcher().fetch()) == []

    @patch("fetcher.sources.iphai.sleep", return_value=None)
    @patch("fetcher.sources.iphai.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.iphai import IphaiFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(IphaiFetcher().fetch()) == []


class TestXicidailiFetcher(object):

    @patch("fetcher.sources.xicidaili.sleep", return_value=None)
    @patch("fetcher.sources.xicidaili.WebRequest")
    def test_fetch_skips_country_column(self, mock_wr, mock_sleep):
        from fetcher.sources.xicidaili import XicidailiFetcher
        html = ('<table id="ip_list">'
                '<tr><th>国家</th><th>IP</th><th>端口</th></tr>'
                '<tr><td>中国</td><td>1.2.3.4</td><td>8080</td><td>北京</td></tr>'
                '<tr><td>美国</td><td>5.6.7.8</td><td>3128</td><td>洛杉矶</td></tr>'
                '</table>')
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        result = list(XicidailiFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert not any("中国" in p for p in result)
        _assert_valid_proxies(result)

    @patch("fetcher.sources.xicidaili.sleep", return_value=None)
    @patch("fetcher.sources.xicidaili.WebRequest")
    def test_dedup_across_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.xicidaili import XicidailiFetcher
        html = ('<table id="ip_list">'
                '<tr><th>IP</th><th>端口</th></tr>'
                '<tr><td>1.2.3.4</td><td>8080</td></tr>'
                '</table>')
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        result = list(XicidailiFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1
        assert mock_sleep.call_count == 1

    @patch("fetcher.sources.xicidaili.sleep", return_value=None)
    @patch("fetcher.sources.xicidaili.WebRequest")
    def test_text_fallback(self, mock_wr, mock_sleep):
        from fetcher.sources.xicidaili import XicidailiFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="1.2.3.4:8080 5.6.7.8:3128", tree=None)
        result = list(XicidailiFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.xicidaili.sleep", return_value=None)
    @patch("fetcher.sources.xicidaili.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.xicidaili import XicidailiFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(XicidailiFetcher().fetch()) == []


class TestData5uFetcher(object):

    @staticmethod
    def _encoded_ul(ip, port):
        """按 key='ABCDEFGHIZ' 生成 class 编码的 ul"""
        key = 'ABCDEFGHIZ'
        code = "".join(key[int(d)] for d in str(port * 8))
        return ('<ul class="l2"><span><li>%s</li></span>'
                '<span><li class="port %s">0000</li></span></ul>' % (ip, code))

    @patch("fetcher.sources.data5u.sleep", return_value=None)
    @patch("fetcher.sources.data5u.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.data5u import Data5uFetcher
        html = self._encoded_ul("1.2.3.4", 8080) + self._encoded_ul("5.6.7.8", 3128)
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        result = list(Data5uFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.data5u.sleep", return_value=None)
    @patch("fetcher.sources.data5u.WebRequest")
    def test_dedup_across_pages(self, mock_wr, mock_sleep):
        from fetcher.sources.data5u import Data5uFetcher
        html = self._encoded_ul("1.2.3.4", 8080)
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        result = list(Data5uFetcher().fetch())
        assert result.count("1.2.3.4:8080") == 1
        assert mock_sleep.call_count == 1

    @patch("fetcher.sources.data5u.sleep", return_value=None)
    @patch("fetcher.sources.data5u.WebRequest")
    def test_bad_class_ignored(self, mock_wr, mock_sleep):
        from fetcher.sources.data5u import Data5uFetcher
        html = ('<ul class="l2"><span><li>1.2.3.4</li></span>'
                '<span><li class="port !!!">0000</li></span></ul>')
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        assert list(Data5uFetcher().fetch()) == []

    @patch("fetcher.sources.data5u.sleep", return_value=None)
    @patch("fetcher.sources.data5u.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.data5u import Data5uFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(Data5uFetcher().fetch()) == []


class TestGoubanjiaFetcher(object):

    @patch("fetcher.sources.goubanjia.WebRequest")
    def test_fetch_obfuscated_ip(self, mock_wr):
        from fetcher.sources.goubanjia import GoubanjiaFetcher
        html = ('<table><tr><td class="ip">'
                '<span>1.</span><span>2.</span><span>3.</span><span>4</span>'
                '<span style="display:none">9</span><span>:</span>'
                '<span class="port CFACE">9054</span>'
                '</td></tr></table>')
        mock_wr.return_value.get.return_value = _make_response(
            text="", tree=etree.HTML(html))
        result = list(GoubanjiaFetcher().fetch())
        assert "1.2.3.4:3128" in result
        _assert_valid_proxies(result)

    @patch("fetcher.sources.goubanjia.WebRequest")
    def test_text_fallback(self, mock_wr):
        from fetcher.sources.goubanjia import GoubanjiaFetcher
        mock_wr.return_value.get.return_value = _make_response(
            text="<p>5.6.7.8:8080</p>", tree=None)
        result = list(GoubanjiaFetcher().fetch())
        assert "5.6.7.8:8080" in result

    @patch("fetcher.sources.goubanjia.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.goubanjia import GoubanjiaFetcher
        mock_wr.return_value.get.return_value = _make_response(text="", tree=None)
        assert list(GoubanjiaFetcher().fetch()) == []

    @patch("fetcher.sources.goubanjia.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.goubanjia import GoubanjiaFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(GoubanjiaFetcher().fetch()) == []


class TestSpysOneFetcher(object):

    @patch("fetcher.sources.spysone.sleep", return_value=None)
    @patch("fetcher.sources.spysone.WebRequest")
    def test_fetch(self, mock_wr, mock_sleep):
        from fetcher.sources.spysone import SpysOneFetcher
        html = ('<tr><td>1.2.3.4</td><td>CN</td><td>8080</td></tr>'
                '<tr><td>5.6.7.8</td><td>US</td><td>3128</td></tr>')
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(SpysOneFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        _assert_valid_proxies(result)
        assert mock_wr.return_value.get.call_count == 2
        assert mock_sleep.call_count == 1

    @patch("fetcher.sources.spysone.sleep", return_value=None)
    @patch("fetcher.sources.spysone.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.spysone import SpysOneFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(SpysOneFetcher().fetch()) == []

    @patch("fetcher.sources.spysone.sleep", return_value=None)
    @patch("fetcher.sources.spysone.WebRequest")
    def test_exception_does_not_raise(self, mock_wr, mock_sleep):
        from fetcher.sources.spysone import SpysOneFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(SpysOneFetcher().fetch()) == []


class TestWebanetlabsFetcher(object):

    @patch("fetcher.sources.webanetlabs.WebRequest")
    def test_fetch_plain_text(self, mock_wr):
        from fetcher.sources.webanetlabs import WebanetlabsFetcher
        text = ("<p>1.2.3.4:8080<br />5.6.7.8:3128<br />"
                "1.2.3.4:8080</p>")
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(WebanetlabsFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert result.count("1.2.3.4:8080") == 1
        _assert_valid_proxies(result)

    @patch("fetcher.sources.webanetlabs.WebRequest")
    def test_table_fallback(self, mock_wr):
        from fetcher.sources.webanetlabs import WebanetlabsFetcher
        text = '<table><tr><td>1.2.3.4</td><td>8080</td></tr></table>'
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(WebanetlabsFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.webanetlabs.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr):
        from fetcher.sources.webanetlabs import WebanetlabsFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(WebanetlabsFetcher().fetch()) == []

    @patch("fetcher.sources.webanetlabs.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.webanetlabs import WebanetlabsFetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(WebanetlabsFetcher().fetch()) == []


class TestAliveProxyFetcher(object):

    @patch("fetcher.sources.aliveproxy.sleep", return_value=None)
    @patch("fetcher.sources.aliveproxy.WebRequest")
    def test_fetch_and_dedup(self, mock_wr, mock_sleep):
        from fetcher.sources.aliveproxy import AliveProxyFetcher
        html = _html_table([("1.2.3.4", "8080"), ("5.6.7.8", "3128")])
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(AliveProxyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert result.count("1.2.3.4:8080") == 1
        _assert_valid_proxies(result)
        # 逐个请求全部 URL, 页面之间 sleep
        assert mock_wr.return_value.get.call_count == len(AliveProxyFetcher.urls)
        assert mock_sleep.call_count == len(AliveProxyFetcher.urls) - 1

    @patch("fetcher.sources.aliveproxy.sleep", return_value=None)
    @patch("fetcher.sources.aliveproxy.WebRequest")
    def test_one_url_failure_does_not_abort_others(self, mock_wr, mock_sleep):
        from fetcher.sources.aliveproxy import AliveProxyFetcher
        ok = _make_response(text=_html_table([("5.6.7.8", "3128")]))

        def side_effect(url, **kwargs):
            if "high-anonymity" in url:
                raise RuntimeError("boom")
            return ok

        mock_wr.return_value.get.side_effect = side_effect
        result = list(AliveProxyFetcher().fetch())
        assert "5.6.7.8:3128" in result
        assert mock_wr.return_value.get.call_count == len(AliveProxyFetcher.urls)

    @patch("fetcher.sources.aliveproxy.sleep", return_value=None)
    @patch("fetcher.sources.aliveproxy.WebRequest")
    def test_empty_response_returns_empty(self, mock_wr, mock_sleep):
        from fetcher.sources.aliveproxy import AliveProxyFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        assert list(AliveProxyFetcher().fetch()) == []
