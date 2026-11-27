# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources_extra.py
   Description :   补充代理源测试
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 ip66 代理源测试
-------------------------------------------------
"""
__author__ = 'JHao'

from unittest.mock import patch, MagicMock

from fetcher.baseFetcher import BaseFetcher


def _response(text=""):
    resp = MagicMock()
    resp.text = text
    return resp


class TestIp66Fetcher(object):

    @patch("fetcher.sources.ip66.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.ip66 import Ip66Fetcher
        mock_wr.return_value.get.return_value = _response(
            "1.2.3.4:8080\n5.6.7.8:3128\n1.2.3.4:8080")
        result = list(Ip66Fetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert result.count("1.2.3.4:8080") == 1

    @patch("fetcher.sources.ip66.WebRequest")
    def test_empty_response(self, mock_wr):
        from fetcher.sources.ip66 import Ip66Fetcher
        mock_wr.return_value.get.return_value = _response("")
        assert list(Ip66Fetcher().fetch()) == []

    @patch("fetcher.sources.ip66.WebRequest")
    def test_exception_does_not_raise(self, mock_wr):
        from fetcher.sources.ip66 import Ip66Fetcher
        mock_wr.return_value.get.side_effect = RuntimeError("boom")
        assert list(Ip66Fetcher().fetch()) == []

    def test_interface(self):
        from fetcher.sources.ip66 import Ip66Fetcher
        assert Ip66Fetcher.name
        assert Ip66Fetcher.url
        assert isinstance(Ip66Fetcher.enabled, bool)
        assert issubclass(Ip66Fetcher, BaseFetcher)
        assert hasattr(Ip66Fetcher, "fetch")
