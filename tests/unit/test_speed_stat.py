# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_speed_stat.py
   Description :   helper/speedStat.py 单元测试
   Author :        JHao
   date：          2026/11/14
-------------------------------------------------
   Change Activity:
                   2026/11/14:
-------------------------------------------------
"""
__author__ = 'JHao'

import time

from helper.speedStat import SpeedStat


class TestSpeedStatRecord:

    def test_empty_snapshot(self):
        """没有校验记录时各窗口均为 0"""
        snap = SpeedStat().snapshot()
        assert snap["1min"] == {"count": 0, "speed": 0.0}
        assert snap["5min"] == {"count": 0, "speed": 0.0}
        assert snap["10min"] == {"count": 0, "speed": 0.0}

    def test_record_counts_in_all_windows(self):
        """刚记录的事件同时落在 1/5/10 分钟窗口内"""
        s = SpeedStat()
        s.record()
        snap = s.snapshot()
        assert snap["1min"]["count"] == 1
        assert snap["5min"]["count"] == 1
        assert snap["10min"]["count"] == 1

    def test_old_events_fall_out_of_short_window(self):
        """2 分钟前的事件不在 1 分钟窗口内, 但在 5/10 分钟内"""
        s = SpeedStat()
        now = time.time()
        s._events.append(now - 120)
        snap = s.snapshot()
        assert snap["1min"]["count"] == 0
        assert snap["5min"]["count"] == 1
        assert snap["10min"]["count"] == 1

    def test_events_older_than_10min_excluded(self):
        """超过 10 分钟的旧事件不计入任何窗口"""
        s = SpeedStat()
        s._events.append(time.time() - 700)
        snap = s.snapshot()
        assert snap["10min"]["count"] == 0

    def test_record_prunes_expired(self):
        """record 时顺带清掉超出保留期的旧数据, 防止 deque 无限增长"""
        s = SpeedStat()
        s._events.append(time.time() - 700)
        s.record()
        # 只保留最近一条
        assert len(s._events) == 1

    def test_dump_returns_recent_only(self):
        """dump 只导出保留期内的时间戳"""
        s = SpeedStat()
        now = time.time()
        s._events.extend([now - 700, now - 60, now])
        assert len(s.dump()) == 2


class TestSpeedStatSummarize:

    def test_speed_is_count_over_window(self):
        """速度为 count/窗口秒数"""
        now = time.time()
        events = [now] * 60  # 1分钟内 60 次
        result = SpeedStat.summarize(events)
        assert result["1min"]["count"] == 60
        assert result["1min"]["speed"] == 1.0  # 60/60
        assert result["5min"]["speed"] == 0.2  # 60/300
        assert result["10min"]["speed"] == 0.1  # 60/600

    def test_speed_rounded_4(self):
        """速度保留 4 位小数"""
        events = [time.time()] * 3
        assert SpeedStat.summarize(events)["1min"]["speed"] == 0.05

    def test_empty_events(self):
        result = SpeedStat.summarize([])
        assert result["1min"]["count"] == 0
        assert result["1min"]["speed"] == 0.0

    def test_window_boundary(self):
        """刚好在窗口内的事件计入 1min, 明显超出则不计"""
        now = time.time()
        assert SpeedStat.summarize([now - 59])["1min"]["count"] == 1
        assert SpeedStat.summarize([now - 61])["1min"]["count"] == 0
