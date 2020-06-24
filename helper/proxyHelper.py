# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyHelper
   Description :
   Author :        JHao
   date：          2020/6/24
-------------------------------------------------
   Change Activity:
                   2020/6/24:
-------------------------------------------------
"""
__author__ = 'JHao'

from util.validators import validators

from datetime import datetime


def proxyCheck(proxy_obj):
    """
    检测代理是否可用
    :param proxy_obj: Proxy object
    :return: Proxy object, status
    """

    def __proxyCheck(proxy):
        for func in validators:
            if not func(proxy):
                return False
        return True

    if __proxyCheck(proxy_obj.proxy):
        # 检测通过 更新proxy属性
        proxy_obj.check_count += 1
        proxy_obj.last_status = 1
        proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if proxy_obj.fail_count > 0:
            proxy_obj.fail_count -= 1
        return proxy_obj
    else:
        proxy_obj.check_count += 1
        proxy_obj.last_status = 0
        proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy_obj.fail_count += 1
        return proxy_obj
