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
        # t = r.text.replace('\r','').replace('\n','').replace('\t','')
        if r.status_code == 200 and "<!--STATUS OK-->" in r.text:
            return True
    except Exception as e:
        pass
    return False


# @validator
# def customValidator(proxy):
#     """
#     自定义validator函数，校验代理是否可用
#     :param proxy:
#     :return: Boolean
#     """
#     return True

@validator
def tagValidatorExample(proxy):
    """
    带标签功能的代理检验
    :param proxy:
    :return: Boolean or List(tags)
    """
    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8'}
    try:
        r = requests.get('https://webvpn.cuit.edu.cn/por/login_auth.csp?apiversion=1', headers=headers, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        v1 = "login auth success" in r.text
        r = requests.get('http://jwc.cuit.edu.cn/', headers=headers, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        v2 = "datedifference" in r.text

        tags = []
        if v1:
            tags.append('cuit_https')
        if v2:
            tags.append('cuit_http')
        if len(tags):
            return tags
        else:
            return False
    except Exception as e:
        return False
        pass
    return False
