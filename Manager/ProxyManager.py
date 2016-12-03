# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyManager.py  
   Description :  
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3: 
-------------------------------------------------
"""
__author__ = 'JHao'

from DB.DbClient import DbClient


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient