# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main.py  
   Description :  运行主函数
   Author :       JHao
   date：          2017/4/1
-------------------------------------------------
   Change Activity:
                   2017/4/1: 
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from multiprocessing import Process

sys.path.append('../')

from Api.ProxyApi import run as ProxyApiRun
from Schedule.ProxyValidSchedule import run as ValidRun


def run():
    p1 = Process(target=ProxyApiRun)
    p1.start()
    p2 = Process(target=ValidRun())
    p2.start()


if __name__ == '__main__':
    run()
