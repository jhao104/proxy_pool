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
import logging
import random
from multiprocessing import Process

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
import sys
sys.path.append('../')
from DB.DbClient import DbClient
from Manager.ProxyManager import ProxyManager

__author__ = 'JHao'


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)

    def valid_proxy(self):
        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy = self.db.pop()
        print '[*]check raw proxy {} ...'.format(raw_proxy)
        while raw_proxy:
            proxies = {"http": "http://{proxy}".format(proxy=raw_proxy),
                       "https": "https://{proxy}".format(proxy=raw_proxy)}
            try:
                # 超过30秒的代理就不要了
                r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=30, verify=False)
                if r.status_code == 200:
                    self.db.changeTable(self.useful_proxy_queue)
                    self.db.put(raw_proxy)
            except Exception, e:
                print e
                pass
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy = self.db.pop()
            print 'validate a  proxy'

    def validate_useful_proxy(self, proxy_list):
        self.db.changeTable(self.useful_proxy_queue)
        for proxy in proxy_list:
            print '[*]validating proxy : {} ...({} remained)'.format(proxy, len(proxy_list))
            proxies = {"http": "http://{proxy}".format(proxy=proxy),
                       "https": "https://{proxy}".format(proxy=proxy)}
            try:
                r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=30, verify=False)
                if r.status_code == 200:
                    continue
            except Exception, e:
                self.db.delete(proxy)
                print '[-]delete proxy {}'.format(proxy)


def refresh_pool():
    pp = ProxyRefreshSchedule()
    pp.valid_proxy()


def validate_user_proxy(proxy_list):
    pp = ProxyRefreshSchedule()
    pp.validate_useful_proxy(proxy_list)


def main(process_num=10):
    p = ProxyRefreshSchedule()
    p.refresh()
    pl = []
    for num in range(process_num):
        proc = Process(target=refresh_pool, args=())
        proc.daemon = True
        pl.append(proc)

    for num in range(process_num):
        pl[num].start()

    print 'All raw_proxy_crawler sub-processes start.'

    for num in range(process_num):
        pl[num].join()


def main_check(process_num=10):
    db = DbClient()
    useful_proxy_queue = 'useful_proxy_queue'
    db.changeTable(useful_proxy_queue)
    proxy_list = db.getAll()

    uncheck_list = [list() for i in xrange(process_num)]
    for proxy in proxy_list:
        uncheck_list[random.randint(0, process_num - 1)].append(proxy)

    pl = []
    for num in range(process_num):
        proc = Process(target=validate_user_proxy, args=(uncheck_list[num],))
        proc.daemon = True
        pl.append(proc)

    for num in range(process_num):
        pl[num].start()

    print 'All proxy validator sub-processes start.'

    for num in range(process_num):
        pl[num].join()


# def main(process_num=100):
#     p = ProxyRefreshSchedule()
#     p.refresh()
#     for num in range(process_num):
#         P = Process(target=refreshPool, args=())
#         P.daemon = True
#         P.start()
#         P.join()
# print '{time}: refresh complete!'.format(time=time.ctime())

if __name__ == '__main__':
    log = logging.getLogger('apscheduler')
    log.setLevel(logging.INFO)  # DEBUG

    fmt = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)

    # main()
    sched = BlockingScheduler()
    # sched.add_job(main, 'interval', seconds=10)
    sched.add_job(main_check, 'interval', seconds=15)
    sched.start()
