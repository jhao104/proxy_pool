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
from helper.proxy import Proxy


def testProxyClass():
    proxy = Proxy("127.0.0.1:8080")

    print(proxy.to_json)

    proxy.source = "test"

    proxy_str = json.dumps(proxy.to_dict, ensure_ascii=False)

    print(proxy_str)

    print(Proxy.createFromJson(proxy_str).to_dict)


if __name__ == '__main__':
    testProxyClass()
