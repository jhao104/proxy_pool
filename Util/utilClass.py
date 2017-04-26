# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     utilClass.py  
   Description :  tool class
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3: Class LazyProperty
                   2016/12/4: rewrite ConfigParser
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


try:
    from configparser import ConfigParser  # py3
except:
    from ConfigParser import ConfigParser  # py2


class ConfigParse(ConfigParser):
    """
    rewrite ConfigParser, for support upper option
    """

    def __init__(self):
        ConfigParser.__init__(self)

    def optionxform(self, optionstr):
        return optionstr


class Singleton(type):
    """
    Singleton Metaclass
    """

    _inst = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._inst:
            cls._inst[cls] = super(Singleton, cls).__call__(*args)
        return cls._inst[cls]
