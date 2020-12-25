# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/8/5: proxyScheduler
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.proxy import Proxy
from helper.fetch import runFetcher
from helper.check import runChecker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler
from qqwry import updateQQwry


def runProxyFetch():
    proxy_queue = Queue()

    for proxy in runFetcher():
        # ('1.1.1.1', 'fetch1')
        proxy_queue.put(Proxy(proxy=proxy[0], source=proxy[1], region=proxy[2]).to_json)

    runChecker("raw", proxy_queue)


def runProxyCheck():
    proxy_queue = Queue()

    print(ProxyHandler().getAll())
    for proxy in ProxyHandler().getAll():
        proxy_queue.put(proxy.to_json)

    runChecker("use", proxy_queue)

def runIpDBUpdate():
    """
    https://github.com/animalize/qqwry-python3
    """
    ret = updateQQwry("qqwry.dat")
    # print(ret)


def runScheduler():
    runProxyFetch()
    runIpDBUpdate()

    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    scheduler.add_job(runProxyFetch, 'interval', minutes=2, id="proxy_fetch", name="proxy采集")
    scheduler.add_job(runProxyCheck, 'interval', minutes=1, id="proxy_check", name="proxy检查")
    scheduler.add_job(runIpDBUpdate, 'interval', minutes=600, id="ipdb_update", name="IP数据库更新")

    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
