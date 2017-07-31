# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testGetConfig
   Description :   test all function in GetConfig.py
   Author :        J_hao
   date：          2017/7/31
-------------------------------------------------
   Change Activity:
                   2017/7/31:
-------------------------------------------------
"""
__author__ = 'J_hao'

from Util.GetConfig import GetConfig


# noinspection PyPep8Naming
def testGetConfig():
    """
    test class GetConfig in Util/GetConfig
    :return:
    """
    gg = GetConfig()
    print(gg.db_type)
    print(gg.db_name)
    print(gg.db_host)
    print(gg.db_port)
    assert isinstance(gg.proxy_getter_functions, list)
    print(gg.proxy_getter_functions)

if __name__ == '__main__':
    testGetConfig()
