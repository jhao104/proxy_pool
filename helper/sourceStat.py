# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     sourceStat.py
   Description :   按代理源采集统计收集器(单轮采集内)
   Author :        JHao
   date：          2026/11/14
-------------------------------------------------
   Change Activity:
                   2026/11/14: 统计各源抓取数/可用数/存活率/上次抓取时间
-------------------------------------------------
"""
__author__ = 'JHao'

import time
from threading import Lock


class SourceStatCollector(object):
    """收集一轮采集内各源的抓取与验证结果, 由调度器在采集结束后落库"""

    def __init__(self):
        self._lock = Lock()
        self._start_time = {}  # source -> 抓取开始时间戳
        self._fetched = {}     # source -> set(proxy)
        self._valid = {}       # source -> set(proxy)

    def reset(self):
        """开始新一轮采集前清空"""
        with self._lock:
            self._start_time = {}
            self._fetched = {}
            self._valid = {}

    def start(self, source):
        """记录某源本轮开始抓取(即使一个都没抓到也算一次抓取)"""
        with self._lock:
            self._start_time[source] = time.time()

    def recordFetched(self, source, proxy):
        """记录某源抓取到的代理(按源去重)"""
        with self._lock:
            self._fetched.setdefault(source, set()).add(proxy)

    def recordValid(self, proxy):
        """记录一个代理验证通过, 按该代理的采集来源分别计数"""
        sources = [s for s in proxy.source.split('/') if s]
        with self._lock:
            for source in sources:
                self._valid.setdefault(source, set()).add(proxy.proxy)

    def snapshot(self):
        """
        返回 {source: {fetched, valid, last_fetch_time}}
        存活率由使用方按 fetched/valid 计算, 避免存储派生值
        """
        with self._lock:
            result = {}
            for source in self._start_time:
                fetched = len(self._fetched.get(source, set()))
                valid = len(self._valid.get(source, set()))
                result[source] = {
                    "fetched": fetched,
                    "valid": valid,
                    "last_fetch_time": time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(self._start_time[source])),
                }
            return result


source_stat = SourceStatCollector()
