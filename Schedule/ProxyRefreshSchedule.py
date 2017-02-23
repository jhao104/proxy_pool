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
import os
import random
import sys
import time
from multiprocessing import Process

import requests
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append('../')
from DB.DbClient import DbClient
from Manager.ProxyManager import ProxyManager

__author__ = 'JHao'

log = logging.getLogger('apscheduler')


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)

    def valid_proxy(self):
        logger_raw = logging.getLogger('apscheduler.raw_check-{}'.format(os.getpid()))

        fmt = logging.Formatter('%(asctime)s - %(levelname)s : %(name)s : %(message)s')
        fh = logging.FileHandler(filename='../log/raw_proxy_log.txt')
        fh.setFormatter(fmt=fmt)
        logger_raw.addHandler(fh)

        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy = self.db.pop()
        while raw_proxy:
            logger_raw.debug('[*] check raw proxy {} ...'.format(raw_proxy))
            # print '[*] check raw proxy {} ...'.format(raw_proxy)
            proxies = {"http": "http://{proxy}".format(proxy=raw_proxy),
                       "https": "https://{proxy}".format(proxy=raw_proxy)}
            try:
                # 超过30秒的代理就不要了
                r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=30, verify=False)
                if r.status_code == 200:
                    self.db.changeTable(self.useful_proxy_queue)
                    self.db.put(raw_proxy)
                    logger_raw.debug('[+] raw proxy {} succeed validating...'.format(raw_proxy))
                    # print '[+] raw proxy {} succeed validating...'.format(raw_proxy)
            except Exception, e:
                print e
                pass
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy = self.db.pop()
            logger_raw.debug('[-] raw proxy {} invalid'.format(raw_proxy))
            # print '[-] raw proxy {} invalid'.format(raw_proxy)

    def validate_useful_proxy(self, proxy_list):
        logger_avail = logging.getLogger('apscheduler.avail_check-{}'.format(os.getpid()))

        fmt = logging.Formatter('%(asctime)s - %(levelname)s : %(name)s : %(message)s')
        fh = logging.FileHandler(filename='../log/available_proxy_log.txt')
        fh.setFormatter(fmt=fmt)
        logger_avail.addHandler(fh)

        len_proxy = len(proxy_list)

        self.db.changeTable(self.useful_proxy_queue)
        while proxy_list:
            proxy = proxy_list.pop()
            logger_avail.debug('[*] check available proxy : {} ...({} remained)'.format(proxy, len(proxy_list)))
            # print '[*] check available proxy : {} ...({} remained)'.format(proxy, len(proxy_list))
            proxies = {"http": "http://{proxy}".format(proxy=proxy),
                       "https": "https://{proxy}".format(proxy=proxy)}
            try:
                r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=30, verify=False)
                if r.status_code == 200:
                    logger_avail.debug('[+] proxy {} is still available'.format(proxy))
                    continue
            except Exception, e:
                self.db.delete(proxy)
                logger_avail.debug('[-] A checked proxy {} has been removed from useful_proxy_queue'.format(proxy))
                # print '[-] A checked proxy {} has been removed from useful_proxy_queue'.format(proxy)
        logger_avail.debug('Process {} finished checking {} proxies.'.format(os.getpid(), len_proxy))


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
        # proc.daemon = True
        pl.append(proc)

    for num in range(process_num):
        pl[num].start()

    for num in range(process_num):
        pl[num].join()

    log.debug('Process main completed.')


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
        # proc.daemon = True
        pl.append(proc)

    for num in range(process_num):
        pl[num].start()

    for num in range(process_num):
        pl[num].join()

    log.debug('Process main_check completed.')


to_time = time.time()


def test():
    print 'start test', time.time() - to_time
    time.sleep(20)
    print 'end test', time.time() - to_time


def test2():
    print 'start test2', time.time() - to_time
    time.sleep(40)
    print 'end test2', time.time() - to_time


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)  # DEBUG

    fmt = logging.Formatter('%(asctime)s - %(levelname)s : %(name)s : %(message)s')
    h = logging.StreamHandler()
    h.setFormatter(fmt)
    log.addHandler(h)

    fh = logging.FileHandler(filename='../log/log.txt')
    fh.setFormatter(fmt=fmt)
    log.addHandler(fh)

    # main()
    sched = BlockingScheduler()
    sched.add_job(main, 'interval', minutes=10)
    sched.add_job(main_check, 'interval', minutes=15)
    sched.start()
