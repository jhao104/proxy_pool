# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     utilClass.py  
   Description :  tool class
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3: Class LazyProperty
-------------------------------------------------
"""
__author__ = 'JHao'


class LazyProperty(object):
    """
    LazyProperty
    explain: http://www.spiderpy.cn/blog/5/
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value
