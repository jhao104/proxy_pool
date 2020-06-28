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

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from helper.proxy import Proxy
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler


def doProxyFetch():
    proxy_queue = Queue()

    fetcher = Fetcher()
    for proxy in fetcher.fetch():
        proxy_queue.put(Proxy(proxy).to_json)

    thread_list = list()
    for index in range(20):
        thread_list.append(Checker("raw", proxy_queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


def doProxyCheck():
    proxy_queue = Queue()

    proxy_handler = ProxyHandler()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy.to_json)


# class DoFetchProxy(ProxyManager):
#     """ fetch proxy"""
#
#     def __init__(self):
#         ProxyManager.__init__(self)
#         self.log = LogHandler('fetch_proxy')
#
#     def main(self):
#         self.log.info("start fetch proxy")
#         self.fetch()
#         self.log.info("finish fetch proxy")
#
#
# def rawProxyScheduler():
#     DoFetchProxy().main()
#     doRawProxyCheck()
#
#
# def usefulProxyScheduler():
#     doUsefulProxyCheck()


def runScheduler():
    doProxyFetch()

    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log)

    scheduler.add_job(doProxyFetch, 'interval', minutes=5, id="proxy_fetch", name="proxy采集")
    # scheduler.add_job(usefulProxyScheduler, 'interval', minutes=1, id="useful_proxy_check", name="useful_proxy定时检查")

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
