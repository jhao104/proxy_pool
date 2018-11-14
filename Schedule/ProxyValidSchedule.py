# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyValidSchedule.py
   Description :  验证useful_proxy_queue中的代理,将不可用的移出
   Author :       JHao
   date：          2017/3/31
-------------------------------------------------
   Change Activity:
                   2017/3/31: 验证useful_proxy_queue中的代理
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import time

try:
    from Queue import Queue  # py3
except:
    from queue import Queue  # py2

sys.path.append('../')

from Schedule.ProxyCheck import ProxyCheck
from Manager.ProxyManager import ProxyManager


class ProxyValidSchedule(ProxyManager, object):
    def __init__(self):
        ProxyManager.__init__(self)
        self.queue = Queue()
        self.proxy_item = dict()

    def __validProxy(self, threads=20):
        """
        验证useful_proxy代理
        :param threads: 线程数
        :return:
        """
        thread_list = list()
        for index in range(threads):
            thread_list.append(ProxyCheck(self.queue, self.proxy_item))

        for thread in thread_list:
            thread.daemon = True
            thread.start()

        for thread in thread_list:
            thread.join()

    def main(self):
        self.putQueue()
        while True:
            if not self.queue.empty():
                self.log.info("Start valid useful proxy")
                self.__validProxy()
            else:
                self.log.info('Valid Complete! sleep 5 minutes.')
                time.sleep(60 * 5)
                self.putQueue()

    def putQueue(self):
        self.db.changeTable(self.useful_proxy_queue)
        self.proxy_item = self.db.getAll()
        for item in self.proxy_item:
            self.queue.put(item)


def run():
    p = ProxyValidSchedule()
    p.main()


if __name__ == '__main__':
    p = ProxyValidSchedule()
    p.main()
