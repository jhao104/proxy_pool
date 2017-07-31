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

from ProxyGetter.getFreeProxy import GetFreeProxy
from Util.GetConfig import GetConfig


# noinspection PyPep8Naming
def testGetFreeProxy():
    """
    test class GetFreeProxy in ProxyGetter/GetFreeProxy
    :return:
    """
    gc = GetConfig()
    proxy_getter_functions = gc.proxy_getter_functions
    for proxyGetter in proxy_getter_functions:
        proxy_count = 0
        for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
            if proxy:
                print('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                proxy_count += 1
        assert proxy_count >= 20, '{} fetch proxy fail'.format(proxyGetter)


if __name__ == '__main__':
    testGetFreeProxy()
