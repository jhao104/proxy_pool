# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testWebRequest
   Description :   test class WebRequest
   Author :        J_hao
   date：          2017/7/31
-------------------------------------------------
   Change Activity:
                   2017/7/31: function testWebRequest
-------------------------------------------------
"""
__author__ = 'J_hao'

from Util.WebRequest import WebRequest


# noinspection PyPep8Naming
def testWebRequest():
    """
    test class WebRequest in Util/WebRequest.py
    :return:
    """
    wr = WebRequest()
    request_object = wr.get('https://www.baidu.com/')
    assert request_object.status_code == 200


if __name__ == '__main__':
    testWebRequest()
