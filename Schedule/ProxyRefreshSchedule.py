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
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from multiprocessing import Process
import requests
import time
import sys

sys.path.append('../')

from Manager.ProxyManager import ProxyManager


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)

    def validProxy(self):
        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy = self.db.pop()
        while raw_proxy:
            proxies = {"http": "http://{proxy}".format(proxy=raw_proxy),
                       "https": "https://{proxy}".format(proxy=raw_proxy)}
            try:
                r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=50, verify=False)
                if r.status_code == 200:
                    self.db.changeTable(self.useful_proxy_queue)
                    self.db.put(raw_proxy)
            except Exception as e:
                # print e
                pass
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy = self.db.pop()


def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def main(process_num=100):
    p = ProxyRefreshSchedule()
    p.refresh()

    for num in range(process_num):
        P = Process(target=refreshPool, args=())
        P.start()
    print '{time}: refresh complete!'.format(time=time.ctime())


if __name__ == '__main__':
    # pp = ProxyRefreshSchedule()
    # pp.main()
    main()
    sched = BlockingScheduler()
    sched.add_job(main, 'interval', minute=20)
    sched.start()
