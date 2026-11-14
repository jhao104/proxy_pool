# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_check.py
   Description :   helper/check.py 单元测试
   Author :        JHao
   date：          2026/6/15
-------------------------------------------------
     Change Activity:
                     2026/06/15:
                     2026/09/05: 黑名单机制测试(伪造即拉黑, 网络型失败连续满5分钟才作废)
-------------------------------------------------
"""
__author__ = 'JHao'

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime

from helper.proxy import Proxy
from helper.check import DoValidator, _ThreadChecker
from helper.blacklist import FAIL_EXPIRE_TIME
from util.six import Empty


class TestDoValidator:
    """DoValidator.validator 测试"""

    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_pass_https_pass(self, mock_pv_cls, mock_conf_cls):
        """HTTP 通过 + HTTPS 通过 -> https=True, fail_count 不变"""
        mock_pv = MagicMock()
        mock_pv.http_validator = [MagicMock(return_value=True)]
        mock_pv.https_validator = [MagicMock(return_value=True)]
        mock_pv_cls.http_validator = mock_pv.http_validator
        mock_pv_cls.https_validator = mock_pv.https_validator

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False
        mock_conf_cls.return_value = mock_conf

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 0

        # Patch DoValidator.conf at class level
        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.https is True
        assert result.last_status is True
        assert result.check_count == 1
        assert result.fail_count == 0

    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_fake(self, mock_pv_cls, mock_conf_cls):
        """HTTP 校验返回 "FAKE"(内容不符) -> last_status=False, fail_count+1, fake_flag=True"""
        mock_pv_cls.http_validator = [MagicMock(return_value="FAKE")]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 0

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.last_status is False
        assert result.fail_count == 1
        assert result.fake_flag is True
        # 伪造不算通过, 不应触发 https 检测后的 https=True
        assert result.https is False

    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_pass_https_fail(self, mock_pv_cls, mock_conf_cls):
        """HTTP 通过 + HTTPS 失败 -> https=False"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=False)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.https is False
        assert result.last_status is True

    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_http_fail(self, mock_pv_cls, mock_conf_cls):
        """HTTP 失败 -> fail_count += 1, last_status=False"""
        mock_pv_cls.http_validator = [MagicMock(return_value=False)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 0

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.last_status is False
        assert result.fail_count == 1

    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_fail_count_decrement(self, mock_pv_cls, mock_conf_cls):
        """HTTP 通过 + fail_count > 0 -> fail_count -= 1"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.fail_count = 3

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "use")

        assert result.fail_count == 2

    @patch("helper.check.DoValidator.regionGetter", return_value="US")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_raw_sets_region(self, mock_pv_cls, mock_conf_cls, mock_region):
        """work_type='raw' + proxyRegion=True -> regionGetter 被调用"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = True

        proxy = Proxy("1.2.3.4:8080", source="test")

        with patch.object(DoValidator, "conf", mock_conf):
            result = DoValidator.validator(proxy, "raw")

        assert result.region == "US"
        mock_region.assert_called_once_with(proxy)

    @patch("helper.check.DoValidator.regionGetter")
    @patch("helper.check.ConfigHandler")
    @patch("helper.check.ProxyValidator")
    def test_validator_use_skips_region(self, mock_pv_cls, mock_conf_cls, mock_region):
        """work_type='use' -> 不调用 regionGetter"""
        mock_pv_cls.http_validator = [MagicMock(return_value=True)]
        mock_pv_cls.https_validator = [MagicMock(return_value=True)]

        mock_conf = MagicMock()
        mock_conf.proxyRegion = True

        proxy = Proxy("1.2.3.4:8080", source="test")

        with patch.object(DoValidator, "conf", mock_conf):
            DoValidator.validator(proxy, "use")

        mock_region.assert_not_called()


class TestThreadCheckerSpeedStat:
    """校验速度统计埋点"""

    def _run_once(self, work_type):
        mock_ph = MagicMock()
        proxy = Proxy("1.2.3.4:8080", source="ip89")
        proxy.last_status = True

        checker = _make_checker(work_type, mock_ph)
        checker.target_queue = MagicMock()
        checker.target_queue.get.side_effect = [proxy, Empty()]

        with patch("helper.check.DoValidator.validator", return_value=proxy), \
             patch("helper.check.speed_stat") as mock_speed, \
             patch("helper.check.source_stat"), \
             patch("helper.check.fail_blacklist"):
            checker.run()
        return mock_speed

    def test_raw_records_speed(self):
        """raw 校验后记录一次时间戳"""
        mock_speed = self._run_once("raw")
        mock_speed.record.assert_called_once()

    def test_use_records_speed(self):
        """use 校验后记录一次时间戳"""
        mock_speed = self._run_once("use")
        mock_speed.record.assert_called_once()

    def test_records_even_when_check_fails(self):
        """校验失败也要计入速度统计"""
        mock_ph = MagicMock()
        proxy = Proxy("1.2.3.4:8080", source="ip89")
        proxy.last_status = False
        proxy.fake_flag = False

        checker = _make_checker("use", mock_ph)
        checker.target_queue = MagicMock()
        checker.target_queue.get.side_effect = [proxy, Empty()]

        with patch("helper.check.DoValidator.validator", return_value=proxy), \
             patch("helper.check.speed_stat") as mock_speed, \
             patch("helper.check.fail_blacklist") as mock_bl:
            mock_bl.markFail.return_value = 0
            checker.run()
        mock_speed.record.assert_called_once()


class TestRegionGetter:
    """DoValidator.regionGetter 测试"""

    @patch("helper.check.WebRequest")
    def test_success_returns_country_code(self, mock_wr_cls):
        """正常返回 -> country_code"""
        mock_wr = MagicMock()
        mock_wr.get.return_value.json = {"country_code": "CN"}
        mock_wr_cls.return_value = mock_wr

        proxy = Proxy("1.2.3.4:8080")
        result = DoValidator.regionGetter(proxy)
        assert result == "CN"

    @patch("helper.check.WebRequest")
    def test_exception_returns_error(self, mock_wr_cls):
        """异常 -> 'error'"""
        mock_wr = MagicMock()
        mock_wr.get.side_effect = Exception("timeout")
        mock_wr_cls.return_value = mock_wr

        proxy = Proxy("1.2.3.4:8080")
        result = DoValidator.regionGetter(proxy)
        assert result == "error"


def _make_checker(work_type, proxy_handler, conf=None):
    """构造手动注入依赖的 _ThreadChecker（绕过 Thread.__init__）"""
    checker = _ThreadChecker.__new__(_ThreadChecker)
    # 手动初始化 Thread 所需的状态
    checker._initialized = True
    checker._name = "test_thread"
    checker._target = None
    checker._args = ()
    checker._kwargs = {}
    checker._daemonic = False
    checker._ident = None
    checker._tstate_lock = None
    checker._started = MagicMock()
    checker._is_stopped = False
    checker._block = MagicMock()
    checker._waiters = []
    checker._stderr = None
    # 注入依赖
    checker.proxy_handler = proxy_handler
    checker.log = MagicMock()
    checker.work_type = work_type
    checker.conf = conf or MagicMock()
    return checker


class TestThreadCheckerIfRaw:
    """_ThreadChecker.__ifRaw 测试"""

    def test_ifraw_new_proxy_gets_put(self):
        """last_status=True, exists=False -> put"""
        mock_ph = MagicMock()
        mock_ph.exists.return_value = False

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = True

        checker = _make_checker("raw", mock_ph)
        checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_called_once_with(proxy)

    def test_ifraw_pass_records_valid_count(self):
        """验证通过的代理计入来源可用数"""
        mock_ph = MagicMock()
        mock_ph.exists.return_value = False

        proxy = Proxy("1.2.3.4:8080", source="ip89")
        proxy.last_status = True

        checker = _make_checker("raw", mock_ph)
        with patch("helper.check.source_stat") as mock_stat:
            checker._ThreadChecker__ifRaw(proxy)
        mock_stat.recordValid.assert_called_once_with(proxy)

    def test_ifraw_existing_also_records_valid(self):
        """已在池中的代理本轮验证通过, 也算该源可用"""
        mock_ph = MagicMock()
        mock_ph.exists.return_value = True

        proxy = Proxy("1.2.3.4:8080", source="ip89")
        proxy.last_status = True

        checker = _make_checker("raw", mock_ph)
        with patch("helper.check.source_stat") as mock_stat:
            checker._ThreadChecker__ifRaw(proxy)
        mock_stat.recordValid.assert_called_once_with(proxy)

    def test_ifraw_failed_not_recorded_valid(self):
        """验证失败不计入可用数"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="ip89")
        proxy.last_status = False

        checker = _make_checker("raw", mock_ph)
        with patch("helper.check.source_stat") as mock_stat, \
             patch("helper.check.fail_blacklist"):
            checker._ThreadChecker__ifRaw(proxy)
        mock_stat.recordValid.assert_not_called()

    def test_ifraw_existing_proxy_skipped(self):
        """last_status=True, exists=True -> 不 put"""
        mock_ph = MagicMock()
        mock_ph.exists.return_value = True

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = True

        checker = _make_checker("raw", mock_ph)
        checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_not_called()

    def test_ifraw_failed_proxy_not_put(self):
        """last_status=False -> 不 put, 且按网络型失败拉黑"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False

        checker = _make_checker("raw", mock_ph)
        with patch("helper.check.fail_blacklist") as mock_bl:
            checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_not_called()
        mock_bl.add.assert_called_once_with("1.2.3.4:8080", fake=False)

    def test_ifraw_failed_fake_blacklist_120(self):
        """伪造代理失败 -> add(fake=True) 拉黑120分钟"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False
        proxy.fake_flag = True

        checker = _make_checker("raw", mock_ph)
        with patch("helper.check.fail_blacklist") as mock_bl:
            checker._ThreadChecker__ifRaw(proxy)
        mock_ph.put.assert_not_called()
        mock_bl.add.assert_called_once_with("1.2.3.4:8080", fake=True)


class TestThreadCheckerIfUse:
    """_ThreadChecker.__ifUse 测试"""

    def test_ifuse_pass_gets_put(self):
        """last_status=True -> put, 并清零连续失败计时"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = True

        checker = _make_checker("use", mock_ph)
        with patch("helper.check.fail_blacklist") as mock_bl:
            checker._ThreadChecker__ifUse(proxy)
        mock_bl.clearFail.assert_called_once_with("1.2.3.4:8080")
        mock_ph.put.assert_called_once_with(proxy)

    def test_ifuse_fake_deleted_blacklist_120(self):
        """伪造代理: 一次即 delete 并拉黑120分钟"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False
        proxy.fake_flag = True

        checker = _make_checker("use", mock_ph)
        with patch("helper.check.fail_blacklist") as mock_bl:
            checker._ThreadChecker__ifUse(proxy)
        mock_bl.add.assert_called_once_with("1.2.3.4:8080", fake=True)
        mock_ph.delete.assert_called_once_with(proxy)
        mock_ph.put.assert_not_called()

    def test_ifuse_fail_over_5min_deleted(self):
        """网络型失败连续满5分钟 -> delete 并拉黑60分钟"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False
        proxy.fake_flag = False

        checker = _make_checker("use", mock_ph)
        with patch("helper.check.fail_blacklist") as mock_bl:
            mock_bl.markFail.return_value = FAIL_EXPIRE_TIME + 1
            checker._ThreadChecker__ifUse(proxy)
        mock_bl.add.assert_called_once_with("1.2.3.4:8080")
        mock_ph.delete.assert_called_once_with(proxy)
        mock_ph.put.assert_not_called()

    def test_ifuse_fail_below_5min_kept(self):
        """网络型失败未满5分钟 -> keep(不计入连续时长即保留)"""
        mock_ph = MagicMock()

        proxy = Proxy("1.2.3.4:8080", source="test")
        proxy.last_status = False
        proxy.fake_flag = False

        checker = _make_checker("use", mock_ph)
        with patch("helper.check.fail_blacklist") as mock_bl:
            mock_bl.markFail.return_value = FAIL_EXPIRE_TIME - 60
            checker._ThreadChecker__ifUse(proxy)
        mock_bl.add.assert_not_called()
        mock_ph.put.assert_called_once_with(proxy)
        mock_ph.delete.assert_not_called()
