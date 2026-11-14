# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     speedStat.py
   Description :   校验速度统计(最近10分钟滑动窗口)
   Author :        JHao
   date：          2026/11/14
-------------------------------------------------
   Change Activity:
                   2026/11/14: 记录1/5/10分钟内校验的ip数量与速度
-------------------------------------------------
"""
__author__ = 'JHao'

import time
from collections import deque
from threading import Lock

# 保留最近10分钟的时间戳, 覆盖最长统计窗口
KEEP_SECONDS = 10 * 60

# 展示窗口(秒)
WINDOWS = (60, 300, 600)


class SpeedStat(object):
    """记录每次校验的时间戳, 按滑动窗口统计数量与速度(个/秒)"""

    def __init__(self, keep_seconds=KEEP_SECONDS):
        self._keep_seconds = keep_seconds
        self._lock = Lock()
        self._events = deque()

    def record(self):
        """记录一次校验, 顺带丢弃窗口外的旧数据"""
        now = time.time()
        with self._lock:
            self._events.append(now)
            while self._events and now - self._events[0] > self._keep_seconds:
                self._events.popleft()

    def dump(self):
        """导出窗口内的时间戳, 供落库"""
        now = time.time()
        with self._lock:
            return [t for t in self._events if now - t <= self._keep_seconds]

    @staticmethod
    def summarize(events, windows=WINDOWS):
        """
        按滑动窗口统计
        Args:
            events: 时间戳列表
            windows: 窗口秒数
        Returns:
            {"1min": {"count": N, "speed": 个/秒}, ...}
        """
        now = time.time()
        result = {}
        for window in windows:
            count = sum(1 for t in events if now - t <= window)
            result["%dmin" % (window // 60)] = {
                "count": count,
                "speed": round(float(count) / window, 4),
            }
        return result

    def snapshot(self, windows=WINDOWS):
        """当前进程内的实时统计"""
        now = time.time()
        with self._lock:
            events = [t for t in self._events if now - t <= self._keep_seconds]
        return self.summarize(events, windows)


speed_stat = SpeedStat()
