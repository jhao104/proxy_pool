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


class ProxyCheck(ProxyManager, Thread):

    def __init__(self):
        ProxyManager.__init__(self)
        Thread.__init__(self)
        self.log = LogHandler('proxy_check')

    def run(self):
        self.db.changeTable(self.useful_proxy_queue)
        while True:
            proxy_item = self.db.pop()
            while proxy_item:
                proxy = proxy_item.get('proxy')
                counter = proxy_item.get('value')
                if validUsefulProxy(proxy):
                    # 验证通过计数器加1, 计数在-5到1之间
                    if counter and int(counter) < 1:
                        self.db.put(proxy, num=int(counter) + 1)
                    else:
                        self.db.put(proxy)
                    self.log.info('ProxyCheck: {} validation pass'.format(proxy))
                else:
                    self.log.info('ProxyCheck: {} validation fail'.format(proxy))
                    # 验证失败，计数器减1
                    if counter and int(counter) < -5:
                        self.log.info('ProxyCheck: {} fail too many, delete!'.format(proxy))
                        self.db.delete(proxy)
                    else:
                        self.db.put(proxy, num=int(counter) - 1)

                proxy_item = self.db.pop()
            sleep(60 * 5)


if __name__ == '__main__':
    p = ProxyCheck()
    p.run()