# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyCheck
   Description :   多线程验证useful_proxy
   Author :        J_hao
   date：          2017/9/26
-------------------------------------------------
   Change Activity:
                   2017/9/26: 多线程验证useful_proxy
-------------------------------------------------
"""
__author__ = 'J_hao'

import sys
import threading
from threading import Thread

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

FAIL_COUNT = 2  # 校验失败次数， 超过次数删除代理


class ProxyCheck(ProxyManager, Thread):
    def __init__(self, queue, item_dict):
        ProxyManager.__init__(self)
        Thread.__init__(self)
        self.log = LogHandler('proxy_check')
        self.queue = queue
        self.item_dict = item_dict

    def run(self):
        while self.queue.qsize():
            print('%s active threads, %s queue size' % (threading.active_count(), self.queue.qsize()))
            proxy = self.queue.get()
            count = self.item_dict[proxy]
            if validUsefulProxy(proxy):
                # 验证通过计数器减1
                if count and int(count) > 0:
                    self.db.put(proxy, num=int(count) - 1)
                else:
                    pass
                print('ProxyCheck: {} validation pass'.format(proxy))
            else:
                print('ProxyCheck: {} validation fail'.format(proxy))
                if count and int(count) > FAIL_COUNT:
                    print('ProxyCheck: {} fail too many, delete!'.format(proxy))
                    self.db.delete(proxy)
                else:
                    self.db.put(proxy, num=int(count) + 1)
            self.queue.task_done()


if __name__ == '__main__':
    # p = ProxyCheck()
    # p.run()
    pass