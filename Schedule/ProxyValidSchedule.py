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

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler


class ProxyValidSchedule(ProxyManager):
    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('valid_schedule')

    def __validProxy(self):
        """
        验证代理
        :return:
        """
        while True:
            self.db.changeTable(self.useful_proxy_queue)
            for each_proxy in self.db.getAll():
                if isinstance(each_proxy, bytes):
                    each_proxy = each_proxy.decode('utf-8')

                if validUsefulProxy(each_proxy):
                    self.log.debug('validProxy_b: {} validation pass'.format(each_proxy))
                else:
                    self.db.delete(each_proxy)
                    self.log.info('validProxy_b: {} validation fail'.format(each_proxy))
        self.log.info('validProxy_a running normal')

    def main(self):
        self.__validProxy()


def run():
    p = ProxyValidSchedule()
    p.main()


if __name__ == '__main__':
    p = ProxyValidSchedule()
    p.main()
