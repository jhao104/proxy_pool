# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyClass
   Description :
   Author :        JHao
   date：          2019/8/8
-------------------------------------------------
   Change Activity:
                   2019/8/8:
-------------------------------------------------
"""
__author__ = 'JHao'

import json
from helper import Proxy


def testProxyClass():
    proxy = Proxy("127.0.0.1:8080")

    print(proxy.info_dict)

    proxy.source = "test"

    proxy_str = json.dumps(proxy.info_dict, ensure_ascii=False)

    print(proxy_str)

    print(Proxy.newProxyFromJson(proxy_str).info_dict)


testProxyClass()
