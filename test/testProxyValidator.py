# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testProxyValidator
   Description :
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2021/5/25:
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.validator import ProxyValidator


def testProxyValidator():
    for _ in ProxyValidator.pre_validator:
        print(_)
    for _ in ProxyValidator.http_validator:
        print(_)
    for _ in ProxyValidator.https_validator:
        print(_)


if __name__ == '__main__':
    testProxyValidator()
