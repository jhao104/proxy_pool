# -*- coding: utf-8 -*-

import requests
from re import findall
from handler.configHandler import ConfigHandler

conf = ConfigHandler()
validators = []


def validator(func):
    validators.append(func)
    return func


@validator
def formatValidator(proxy):
    """
    检查代理格式
    :param proxy:
    :return:
    """
    verify_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
    _proxy = findall(verify_regex, proxy)
    return True if len(_proxy) == 1 and _proxy[0] == proxy else False


@validator
def timeOutValidator(proxy):
    """
    检测超时
    :param proxy:
    :return:
    """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8'}
    try:
        r = requests.head(conf.verifyUrl, headers=headers, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        if r.status_code == 200:
            return True
    except Exception as e:
        pass
    return False


@validator
def customValidator(proxy):
    """
    自定义validator函数，校验代理是否可用
    :param proxy:
    :return:
    """

    return True
