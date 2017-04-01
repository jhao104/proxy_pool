# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyValidSchedule.py  
   Description :  代理验证
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

    def __validProxy__(self):
        """
        验证代理
        :return:
        """
        while 1:
            self.db.changeTable(self.useful_proxy_queue)
            for each_proxy in self.db.getAll():
                if validUsefulProxy(each_proxy):
                    self.log.debug('proxy: {} validation pass'.format(each_proxy))
                else:
                    self.db.delete(each_proxy)
                    self.log.info('proxy: {} validation fail'.format(each_proxy))
        self.log.info(u'代理验证程序运行正常')

    def main(self):
        self.__validProxy__()


def run():
    p = ProxyValidSchedule()
    p.main()

if __name__ == '__main__':
    p = ProxyValidSchedule()
    p.main()
