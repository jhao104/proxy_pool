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

from Util.LogHandler import LogHandler


# noinspection PyPep8Naming
def testLogHandler():
    """
    test function LogHandler  in Util/LogHandler
    :return:
    """
    log = LogHandler('test')
    log.info('this is a log from test')

    log.resetName(name='test1')
    log.info('this is a log from test1')

    log.resetName(name='test2')
    log.info('this is a log from test2')


if __name__ == '__main__':
    testLogHandler()
