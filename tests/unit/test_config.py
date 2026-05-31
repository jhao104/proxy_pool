# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testConfig.py
   Description :   ConfigHandler环境变量测试
   Author :        JHao
   date：          2026/5/28
-------------------------------------------------
   Change Activity:
                   2026/05/28:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import pytest
import setting
from handler.configHandler import ConfigHandler


@pytest.fixture(autouse=True)
def clean_env():
    """测试前后清理可能设置的环境变量"""
    env_keys = ["DB_CONN", "PORT", "HOST", "TABLE_NAME", "HTTP_URL",
                "HTTPS_URL", "VERIFY_TIMEOUT", "MAX_FAIL_COUNT",
                "POOL_SIZE_MIN", "PROXY_REGION", "TIMEZONE"]
    saved = {k: os.environ.get(k) for k in env_keys}
    for k in env_keys:
        os.environ.pop(k, None)
    yield
    for k, v in saved.items():
        if v is not None:
            os.environ[k] = v
        else:
            os.environ.pop(k, None)


@pytest.fixture
def conf():
    return ConfigHandler()


class TestConfigHandlerDefaults:

    def test_db_conn_default(self, conf):
        assert conf.dbConn == setting.DB_CONN

    def test_server_host_default(self, conf):
        assert conf.serverHost == setting.HOST

    def test_server_port_default(self, conf):
        assert str(conf.serverPort) == str(setting.PORT)

    def test_table_name_default(self, conf):
        assert conf.tableName == setting.TABLE_NAME

    def test_http_url_default(self, conf):
        assert conf.httpUrl == setting.HTTP_URL

    def test_https_url_default(self, conf):
        assert conf.httpsUrl == setting.HTTPS_URL

    def test_verify_timeout_default(self, conf):
        assert conf.verifyTimeout == setting.VERIFY_TIMEOUT

    def test_max_fail_count_default(self, conf):
        assert conf.maxFailCount == setting.MAX_FAIL_COUNT

    def test_pool_size_min_default(self, conf):
        assert conf.poolSizeMin == setting.POOL_SIZE_MIN

    def test_timezone_default(self, conf):
        assert conf.timezone == setting.TIMEZONE

    def test_fetcher_exclude_is_list(self, conf):
        assert isinstance(conf.fetcherExclude, list)


class TestConfigHandlerEnvOverride:

    def test_db_conn_override(self):
        os.environ["DB_CONN"] = "redis://:newpwd@10.0.0.1:6380/3"
        conf = ConfigHandler()
        assert conf.dbConn == "redis://:newpwd@10.0.0.1:6380/3"

    def test_port_override(self):
        os.environ["PORT"] = "8080"
        conf = ConfigHandler()
        assert str(conf.serverPort) == "8080"

    def test_verify_timeout_override(self):
        os.environ["VERIFY_TIMEOUT"] = "30"
        conf = ConfigHandler()
        assert conf.verifyTimeout == 30

    def test_max_fail_count_override(self):
        os.environ["MAX_FAIL_COUNT"] = "5"
        conf = ConfigHandler()
        assert conf.maxFailCount == 5