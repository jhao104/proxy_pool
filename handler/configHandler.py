# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import setting
from util.six import reload_six
from util.singleton import Singleton
from util.lazyProperty import LazyProperty


class ConfigHandler(object):
    __metaclass__ = Singleton

    def __init__(self):
        pass

    @LazyProperty
    def serverHost(self):
        return os.environ.get("HOST", setting.HOST)

    @LazyProperty
    def serverPort(self):
        return os.environ.get("PORT", setting.PORT)

    @LazyProperty
    def dbConn(self):
        return os.getenv("DB_CONN", setting.DB_CONN)

    @LazyProperty
    def rawProxy(self):
        return setting.RAW_PROXY

    @LazyProperty
    def useProxy(self):
        return setting.USE_PROXY

    @property
    def fetchers(self):
        reload_six(setting)
        return setting.PROXY_FETCHER

    @LazyProperty
    def verifyUrl(self):
        return os.getenv("VERIFY_URL", setting.VERIFY_RUL)

    @LazyProperty
    def verifyTimeout(self):
        return os.getenv("VERIFY_TIMEOUT", setting.VERIFY_TIMEOUT)
