# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_base_fetcher.py
   Description :   BaseFetcher 基类测试
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

from lxml import etree
from fetcher.baseFetcher import BaseFetcher


class TestParseProxiesFromText(object):
    """parseProxiesFromText 测试"""

    def test_basic_ip_port(self):
        text = "1.2.3.4:8080"
        result = BaseFetcher.parseProxiesFromText(text)
        assert result == ["1.2.3.4:8080"]

    def test_multiple_proxies(self):
        text = "1.2.3.4:8080\n5.6.7.8:3128\n9.10.11.12:80"
        result = BaseFetcher.parseProxiesFromText(text)
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128", "9.10.11.12:80"]

    def test_ip_port_with_spaces(self):
        text = "1.2.3.4  8080"
        result = BaseFetcher.parseProxiesFromText(text)
        assert result == ["1.2.3.4:8080"]

    def test_ip_port_in_html_text(self):
        """HTML标签中的ip:port需要跨标签匹配，parseProxiesFromText只处理纯文本"""
        text = '<td>1.2.3.4</td><td>8080</td>'
        result = BaseFetcher.parseProxiesFromText(text)
        assert result == []

    def test_empty_text(self):
        assert BaseFetcher.parseProxiesFromText("") == []
        assert BaseFetcher.parseProxiesFromText(None) == []

    def test_no_proxies(self):
        text = "no proxies here"
        assert BaseFetcher.parseProxiesFromText(text) == []

    def test_ip_with_colon_port(self):
        text = "192.168.1.1:3128"
        result = BaseFetcher.parseProxiesFromText(text)
        assert result == ["192.168.1.1:3128"]

    def test_port_range(self):
        text = "1.2.3.4:80 1.2.3.4:65535"
        result = BaseFetcher.parseProxiesFromText(text)
        assert "1.2.3.4:80" in result
        assert "1.2.3.4:65535" in result


class TestParseProxiesFromJson(object):
    """parseProxiesFromJson 测试"""

    def test_dict_with_proxy_key(self):
        data = {"proxy": "1.2.3.4:8080"}
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_dict_with_addr_key(self):
        data = {"addr": "1.2.3.4:8080"}
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_dict_with_ip_port_keys(self):
        data = {"ip": "1.2.3.4", "port": "8080"}
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_dict_with_host_port_keys(self):
        data = {"host": "1.2.3.4", "port": "8080"}
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_dict_with_server_port_keys(self):
        data = {"server": "1.2.3.4", "port": "8080"}
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_list_of_dicts(self):
        data = [
            {"ip": "1.2.3.4", "port": "8080"},
            {"ip": "5.6.7.8", "port": "3128"},
        ]
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    def test_nested_dict(self):
        data = {
            "data": {
                "items": [
                    {"ip": "1.2.3.4", "port": "8080"}
                ]
            }
        }
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_string_value(self):
        data = "1.2.3.4:8080"
        result = BaseFetcher.parseProxiesFromJson(data)
        assert "1.2.3.4:8080" in result

    def test_empty_dict(self):
        assert BaseFetcher.parseProxiesFromJson({}) == []

    def test_empty_list(self):
        assert BaseFetcher.parseProxiesFromJson([]) == []


class TestParseProxiesFromTree(object):
    """parseProxiesFromTree 测试"""

    def test_basic_table(self):
        html = "<table><tr><td>1.2.3.4</td><td>8080</td></tr></table>"
        tree = etree.HTML(html)
        result = BaseFetcher.parseProxiesFromTree(tree)
        assert "1.2.3.4:8080" in result

    def test_multiple_rows(self):
        html = """<table>
            <tr><td>1.2.3.4</td><td>8080</td></tr>
            <tr><td>5.6.7.8</td><td>3128</td></tr>
        </table>"""
        tree = etree.HTML(html)
        result = BaseFetcher.parseProxiesFromTree(tree)
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    def test_none_tree(self):
        assert BaseFetcher.parseProxiesFromTree(None) == []

    def test_empty_table(self):
        html = "<table></table>"
        tree = etree.HTML(html)
        assert BaseFetcher.parseProxiesFromTree(tree) == []

    def test_header_row_skipped(self):
        html = """<table>
            <tr><th>IP</th><th>Port</th></tr>
            <tr><td>1.2.3.4</td><td>8080</td></tr>
        </table>"""
        tree = etree.HTML(html)
        result = BaseFetcher.parseProxiesFromTree(tree)
        assert "1.2.3.4:8080" in result

    def test_row_with_too_few_cells(self):
        html = "<table><tr><td>1.2.3.4</td></tr></table>"
        tree = etree.HTML(html)
        assert BaseFetcher.parseProxiesFromTree(tree) == []


class TestYieldUniqueProxies(object):
    """yieldUniqueProxies 测试"""

    def test_unique_proxies(self):
        proxies = ["1.2.3.4:8080", "5.6.7.8:3128"]
        result = list(BaseFetcher.yieldUniqueProxies(proxies))
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    def test_duplicates_removed(self):
        proxies = ["1.2.3.4:8080", "5.6.7.8:3128", "1.2.3.4:8080"]
        result = list(BaseFetcher.yieldUniqueProxies(proxies))
        assert result == ["1.2.3.4:8080", "5.6.7.8:3128"]

    def test_empty_list(self):
        assert list(BaseFetcher.yieldUniqueProxies([])) == []

    def test_preserves_order(self):
        proxies = ["3.3.3.3:80", "1.1.1.1:80", "2.2.2.2:80", "3.3.3.3:80"]
        result = list(BaseFetcher.yieldUniqueProxies(proxies))
        assert result == ["3.3.3.3:80", "1.1.1.1:80", "2.2.2.2:80"]

    def test_is_generator(self):
        import types
        gen = BaseFetcher.yieldUniqueProxies([])
        assert isinstance(gen, types.GeneratorType)


class TestBaseFetcherInterface(object):
    """BaseFetcher 接口约定测试"""

    def test_name_attribute(self):
        assert hasattr(BaseFetcher, 'name')
        assert BaseFetcher.name == ""

    def test_url_attribute(self):
        assert hasattr(BaseFetcher, 'url')
        assert BaseFetcher.url == ""

    def test_fetch_raises_not_implemented(self):
        fetcher = BaseFetcher()
        try:
            fetcher.fetch()
            assert False, "Should have raised NotImplementedError"
        except NotImplementedError:
            pass
