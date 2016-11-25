# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     getFreeProxy.py  
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: 
-------------------------------------------------
"""
import re
import requests
from lxml import etree


def robust(func):
    def decorate(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print u"sorry, 抓取出错。错误原因:"
            print e

    return decorate


def verifyProxy(proxy):
    """
    检查代理格式
    :param proxy:
    :return:
    """
    verify_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}"
    return True if re.findall(verify_regex, proxy) else False


# 快代理
# noinspection PyPep8Naming
@robust
def freeProxyFirst(page=10):
    """
    抓取快代理IP http://www.kuaidaili.com/
    :param page: 翻页数
    :return:
    """
    url_list = ('http://www.kuaidaili.com/proxylist/{page}/'.format(page=page) for page in range(1, page + 1))
    # 页数不用太多， 后面的全是历史IP， 可用性不高
    for url in url_list:
        html = requests.get(url).content
        tree = etree.HTML(html)
        proxy_list = tree.xpath('.//div[@id="index_free_list"]//tbody/tr')
        for proxy in proxy_list:
            yield ':'.join(proxy.xpath('./td/text()')[0:2])


# 代理66
@robust
def freeProxySecond(proxy_number):
    """
    抓取代理66 http://www.66ip.cn/
    :param proxy_number: 代理数量
    :return:
    """
    pass


if __name__ == '__main__':
    # for e in freeProxyFirst():
    #     print e
    pass