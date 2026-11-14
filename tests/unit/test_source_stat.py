# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_source_stat.py
   Description :   helper/sourceStat.py 单元测试
   Author :        JHao
   date：          2026/11/14
-------------------------------------------------
   Change Activity:
                   2026/11/14:
-------------------------------------------------
"""
__author__ = 'JHao'

import time

from helper.proxy import Proxy
from helper.sourceStat import SourceStatCollector


def _collector():
    return SourceStatCollector()


class TestSourceStatCollector:

    def test_empty_snapshot(self):
        assert _collector().snapshot() == {}

    def test_start_records_source_even_without_proxies(self):
        """开始了抓取但一个都没抓到, 也要有该源的记录"""
        c = _collector()
        c.start("empty_src")
        snap = c.snapshot()
        assert "empty_src" in snap
        assert snap["empty_src"]["fetched"] == 0
        assert snap["empty_src"]["valid"] == 0

    def test_fetched_dedup_per_source(self):
        """同一源重复抓到同一代理只计一次"""
        c = _collector()
        c.start("ip89")
        c.recordFetched("ip89", "1.2.3.4:8080")
        c.recordFetched("ip89", "1.2.3.4:8080")
        c.recordFetched("ip89", "5.6.7.8:3128")
        assert c.snapshot()["ip89"]["fetched"] == 2

    def test_fetched_per_source_isolated(self):
        """不同源各自计数"""
        c = _collector()
        c.start("a")
        c.start("b")
        c.recordFetched("a", "1.2.3.4:8080")
        c.recordFetched("b", "1.2.3.4:8080")
        snap = c.snapshot()
        assert snap["a"]["fetched"] == 1
        assert snap["b"]["fetched"] == 1

    def test_record_valid_counts_each_source(self):
        """多来源代理在每个来源下都算一次可用"""
        c = _collector()
        c.start("ip89")
        c.start("kuaidaili")
        proxy = Proxy("1.2.3.4:8080", source="ip89/kuaidaili")
        c.recordValid(proxy)
        snap = c.snapshot()
        assert snap["ip89"]["valid"] == 1
        assert snap["kuaidaili"]["valid"] == 1

    def test_record_valid_ignores_empty_source(self):
        """空来源不产生空 key"""
        c = _collector()
        c.start("ip89")
        c.recordValid(Proxy("1.2.3.4:8080", source=""))
        assert "" not in c.snapshot()

    def test_unknown_source_not_in_snapshot(self):
        """未 start 的来源不会凭空出现在快照里"""
        c = _collector()
        c.start("a")
        c.recordValid(Proxy("1.2.3.4:8080", source="ghost"))
        snap = c.snapshot()
        assert "ghost" not in snap

    def test_last_fetch_time_format(self):
        c = _collector()
        c.start("ip89")
        last = c.snapshot()["ip89"]["last_fetch_time"]
        # 形如 2026-11-14 10:00:00
        assert len(last) == 19
        assert last[4] == "-" and last[13] == ":"

    def test_start_time_updates_on_restart(self):
        """再次 start 覆盖上次抓取时间"""
        c = _collector()
        c.start("ip89")
        first = c._start_time["ip89"]
        time.sleep(0.01)
        c.start("ip89")
        assert c._start_time["ip89"] > first

    def test_reset_clears_all(self):
        """reset 后回到空状态, 保证每轮统计互相独立"""
        c = _collector()
        c.start("ip89")
        c.recordFetched("ip89", "1.2.3.4:8080")
        c.recordValid(Proxy("1.2.3.4:8080", source="ip89"))
        c.reset()
        assert c.snapshot() == {}
