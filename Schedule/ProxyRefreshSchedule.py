# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyRefreshSchedule.py
   Description :  代理定时刷新
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4: 代理定时刷新
                   2017/03/06: 使用LogHandler添加日志
                   2017/04/26: raw_proxy_queue验证通过但useful_proxy_queue中已经存在的代理不在放入
-------------------------------------------------
"""

import sys
import time
import logging
from threading import Thread
# 使用后台调度，不使用阻塞式~
from apscheduler.schedulers.background import BackgroundScheduler as Sch

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

__author__ = 'JHao'

logging.basicConfig()


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('refresh_schedule')

    def validProxy(self):
        """
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy_item = self.db.pop()
        self.log.info('ProxyRefreshSchedule: %s start validProxy' % time.ctime())
        # 计算剩余代理，用来减少重复计算
        remaining_proxies = self.getAll()
        while raw_proxy_item:
            raw_proxy = raw_proxy_item.get('proxy')
            if isinstance(raw_proxy, bytes):
                # 兼容Py3
                raw_proxy = raw_proxy.decode('utf8')

            if (raw_proxy not in remaining_proxies) and validUsefulProxy(raw_proxy):
                self.db.changeTable(self.useful_proxy_queue)
                self.db.put(raw_proxy)
                self.log.info('ProxyRefreshSchedule: %s validation pass' % raw_proxy)
            else:
                self.log.info('ProxyRefreshSchedule: %s validation fail' % raw_proxy)
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy_item = self.db.pop()
            remaining_proxies = self.getAll()
        self.log.info('ProxyRefreshSchedule: %s validProxy complete' % time.ctime())


def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def batch_refresh(process_num=30):
    # 检验新代理
    pl = []
    for num in range(process_num):
        proc = Thread(target=refreshPool, args=())
        pl.append(proc)

    for num in range(process_num):
        pl[num].daemon = True
        pl[num].start()

    for num in range(process_num):
        pl[num].join()


def fetch_all():
    p = ProxyRefreshSchedule()
    # 获取新代理
    p.refresh()


def run():
    sch = Sch()
    sch.add_job(fetch_all, 'interval', minutes=5)  # 每5分钟抓取一次
    sch.add_job(batch_refresh, "interval", minutes=1)  # 每分钟检查一次
    sch.start()
    fetch_all()


if __name__ == '__main__':
    run()
