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
import threading
# 使用后台调度，不使用阻塞式~
from apscheduler.schedulers.background import BackgroundScheduler as Sch

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Log.LogManager import log

__author__ = 'JHao'

logging.basicConfig()


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)

    def validProxy(self):
        """
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy_item = self.db.pop()

        thread_id = threading.currentThread().ident
        log.info("thread_id:{thread_id}, Start ValidProxy `raw_proxy_queue`".format(thread_id=thread_id))

        total = 0
        succ = 0
        fail = 0
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
                log.debug('ProxyRefreshSchedule: %s validation pass' % raw_proxy)
                succ = succ + 1
            else:
                log.debug('ProxyRefreshSchedule: %s validation fail' % raw_proxy)
                fail = fail + 1
            total = total + 1
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy_item = self.db.pop()
            remaining_proxies = self.getAll()

        log.info('thread_id:{thread_id}, ValidProxy Complete `raw_proxy_queue`, total:{total}, succ:{succ}, fail:{fail}'.format(thread_id=thread_id, total=total, succ=succ, fail=fail))

def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def batch_refresh(process_num=30):
    # 检验新代理
    pl = []
    for num in range(process_num):
        proc = threading.Thread(target=refreshPool, args=())
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

    while True:
        time.sleep(1)


if __name__ == '__main__':
    run()
