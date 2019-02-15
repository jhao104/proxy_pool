# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testGetFreeProxy
   Description :   test model ProxyGetter/getFreeProxy
   Author :        J_hao
   date：          2017/7/31
-------------------------------------------------
   Change Activity:
                   2017/7/31:function testGetFreeProxy
-------------------------------------------------
"""
__author__ = 'J_hao'

import re
import sys
import requests

try:
    from importlib import reload  # py3 实际不会实用，只是为了不显示语法错误
except:
    reload(sys)
    sys.setdefaultencoding('utf-8')

sys.path.append('..')
from ProxyGetter.getFreeProxy import GetFreeProxy
from Config.ConfigGetter import config


# noinspection PyPep8Naming
def testGetFreeProxy():
    """
    test class GetFreeProxy in ProxyGetter/GetFreeProxy
    :return:
    """
    proxy_getter_functions = config.proxy_getter_functions
    for proxyGetter in proxy_getter_functions:
        proxy_count = 0
        for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
            if proxy:
                print('{func}: fetch proxy {proxy},proxy_count:{proxy_count}'.format(func=proxyGetter, proxy=proxy,
                                                                                     proxy_count=proxy_count))
                proxy_count += 1
        # assert proxy_count >= 20, '{} fetch proxy fail'.format(proxyGetter)


if __name__ == '__main__':
    testGetFreeProxy()
