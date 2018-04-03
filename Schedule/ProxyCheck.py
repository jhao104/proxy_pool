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
from time import sleep
from threading import Thread

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

FAIL_COUNT = 2  # 校验失败次数， 超过次数删除代理


class ProxyCheck(ProxyManager, Thread):
    def __init__(self):
        ProxyManager.__init__(self)
        Thread.__init__(self)
        self.log = LogHandler('proxy_check')

    def run(self):
        self.db.changeTable(self.useful_proxy_queue)
        while True:
            for proxy, count in self.db.getAll().items():
                if validUsefulProxy(proxy):
                    # 验证通过计数器减1
                    if count and int(count) > 0:
                        self.db.put(proxy, num=int(count) - 1)
                    else:
                        pass
                    self.log.info('ProxyCheck: {} validation pass'.format(proxy))
                else:
                    self.log.info('ProxyCheck: {} validation fail'.format(proxy))
                    if count and int(count) > FAIL_COUNT:
                        self.log.info('ProxyCheck: {} fail too many, delete!'.format(proxy))
                        self.db.delete(proxy)
                    else:
                        self.db.put(proxy, num=int(count) + 1)
            sleep(60 * 5)


if __name__ == '__main__':
    p = ProxyCheck()
    p.run()
