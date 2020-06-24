# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHelper
   Description :
   Author :        JHao
   date：          2019/8/8
-------------------------------------------------
   Change Activity:
                   2019/8/8:
-------------------------------------------------
"""
__author__ = 'JHao'

from util import validUsefulProxy

from datetime import datetime


def checkProxyUseful(proxy_obj):
    """
    检测代理是否可用
    :param proxy_obj: Proxy object
    :return: Proxy object, status
    """

    if validUsefulProxy(proxy_obj.proxy):
        # 检测通过 更新proxy属性
        proxy_obj.check_count += 1
        proxy_obj.last_status = 1
        proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if proxy_obj.fail_count > 0:
            proxy_obj.fail_count -= 1
        return proxy_obj, True
    else:
        proxy_obj.check_count += 1
        proxy_obj.last_status = 0
        proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy_obj.fail_count += 1
        return proxy_obj, False
