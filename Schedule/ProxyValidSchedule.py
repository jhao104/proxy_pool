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

sys.path.append('../')

from Schedule.ProxyCheck import ProxyCheck
from Manager.ProxyManager import ProxyManager
from queue import Queue
import time


class ProxyValidSchedule(ProxyManager, object):
    def __init__(self):
        ProxyManager.__init__(self)
        self.queue = Queue()

    def __validProxy(self, threads=5):
        """
        验证useful_proxy代理
        :param threads: 线程数
        :return:
        """
        thread_list = list()
        for index in range(threads):
            thread_list.append(ProxyCheck(self.queue, self.item_dict))

        for thread in thread_list:
            thread.daemon = True
            thread.start()

        for thread in thread_list:
            thread.join()

    def main(self):
        self.put_queue()
        while True:
            if self.queue.qsize():
                self.__validProxy()
            else:
                print('Time sleep 5 minutes.')
                time.sleep(60 * 5)
                self.put_queue()

    def put_queue(self):
        self.db.changeTable(self.useful_proxy_queue)
        self.item_dict = self.db.getAll()
        for item in self.item_dict:
            self.queue.put(item)


def run():
    p = ProxyValidSchedule()
    p.main()


if __name__ == '__main__':
    p = ProxyValidSchedule()
    p.main()
