# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testValidator.py
   Description :   formatValidator正则测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import pytest

# 直接导入 IP_REGEX 和 formatValidator，不导入整个 validator 模块（避免模块级副作用）
from helper.validator import IP_REGEX, formatValidator


class TestIPRegex:

    @pytest.mark.parametrize("proxy", [
        "1.2.3.4:8080",
        "192.168.1.1:3128",
        "10.0.0.1:80",
        "255.255.255.255:65535",
        "0.0.0.0:1",
        "1.2.3.4:99999",   # regex 不校验端口范围
        "999.1.1.1:80",    # regex 不校验 IP 范围
        "user:pass@1.2.3.4:8080",
        "admin:secret@192.168.1.1:443",
    ])
    def test_valid_proxy_format(self, proxy):
        assert IP_REGEX.fullmatch(proxy) is not None, f"应匹配: {proxy}"

    @pytest.mark.parametrize("proxy", [
        "",
        "abc",
        "1.2.3.4",
        "1.2.3.4:",
        ":8080",
        "1.2.3.4:abc",
        "1.2.3.4:8080:extra",
        "host:8080",
    ])
    def test_invalid_proxy_format(self, proxy):
        assert IP_REGEX.fullmatch(proxy) is None, f"不应匹配: {proxy}"


class TestFormatValidator:

    @pytest.mark.parametrize("proxy", [
        "1.2.3.4:8080",
        "192.168.1.1:3128",
        "user:pass@10.0.0.1:80",
    ])
    def test_valid_returns_true(self, proxy):
        assert formatValidator(proxy) is True

    @pytest.mark.parametrize("proxy", [
        "",
        "abc",
        "1.2.3.4",
    ])
    def test_invalid_returns_false(self, proxy):
        assert formatValidator(proxy) is False