# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testLogHandler
   Description :
   Author :        J_hao
   date：          2017/8/2
-------------------------------------------------
   Change Activity:
                   2017/8/2:
-------------------------------------------------
"""
__author__ = 'J_hao'

from handler.logHandler import LogHandler


def testLogHandler():
    log = LogHandler('test')
    log.info('this is info')
    log.error('this is error')


if __name__ == '__main__':
    testLogHandler()
