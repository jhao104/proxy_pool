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

from Config.ConfigGetter import config


# noinspection PyPep8Naming
def testConfig():
    """
    :return:
    """
    print(config.db_type)
    print(config.db_name)
    print(config.db_host)
    print(config.db_port)
    print(config.db_password)
    assert isinstance(config.proxy_getter_functions, list)
    print(config.proxy_getter_functions)


if __name__ == '__main__':
    testConfig()
