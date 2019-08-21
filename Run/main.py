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
import signal
from multiprocessing import Process

sys.path.append('.')
sys.path.append('..')

from Schedule.ProxyScheduler import runScheduler
from Api.ProxyApi import runFlaskWithGunicorn


def run():
    p_list = list()
    p1 = Process(target=runScheduler, name='scheduler')
    p_list.append(p1)
    p2 = Process(target=runFlaskWithGunicorn, name='api')
    p_list.append(p2)

    def kill_child_processes(signum, frame):
        for p in p_list:
            p.terminate()
        sys.exit(1)

    signal.signal(signal.SIGTERM, kill_child_processes)

    for p in p_list:
        p.daemon = True
        p.start()
    for p in p_list:
        p.join()


if __name__ == '__main__':
    run()
