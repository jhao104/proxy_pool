# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     UsefulProxyCheck
   Description :   check useful proxy
   Author :        JHao
   date：          2019/8/7
-------------------------------------------------
   Change Activity:
                   2019/8/7: check useful proxy
-------------------------------------------------
"""
__author__ = 'JHao'

from threading import Thread

try:
    from Queue import Queue, Empty  # py2
except:
    from queue import Queue, Empty  # py3

from Util import LogHandler
from Manager import ProxyManager
from ProxyHelper import checkProxyUseful, Proxy

FAIL_COUNT = 0


class UsefulProxyCheck(ProxyManager, Thread):
    def __init__(self, queue, thread_name):
        ProxyManager.__init__(self)
        Thread.__init__(self, name=thread_name)

        self.queue = queue
        self.log = LogHandler('useful_proxy_check')

    def run(self):
        self.log.info("UsefulProxyCheck - {}  : start".format(self.name))
        self.db.changeTable(self.useful_proxy_queue)
        while True:
            try:
                proxy_str = self.queue.get(block=False)
            except Empty:
                self.log.info("UsefulProxyCheck - {}  : exit".format(self.name))
                break

            proxy_obj = Proxy.newProxyFromJson(proxy_str)
            proxy_obj, status = checkProxyUseful(proxy_obj)
            if status or proxy_obj.fail_count < FAIL_COUNT:
                self.db.put(proxy_obj)
                self.log.info('UsefulProxyCheck - {}  : {} validation pass'.format(self.name,
                                                                                   proxy_obj.proxy.ljust(20)))
            else:
                self.log.info('UsefulProxyCheck - {}  : {} validation fail'.format(self.name,
                                                                                   proxy_obj.proxy.ljust(20)))
                self.db.delete(proxy_obj.proxy)
            self.queue.task_done()


def doUsefulProxyCheck():
    proxy_queue = Queue()

    pm = ProxyManager()
    pm.db.changeTable(pm.useful_proxy_queue)
    for _proxy in pm.db.getAll():
        proxy_queue.put(_proxy)

    thread_list = list()
    for index in range(10):
        thread_list.append(UsefulProxyCheck(proxy_queue, "thread_%s" % index))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()


if __name__ == '__main__':
    doUsefulProxyCheck()
