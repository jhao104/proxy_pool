# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
-------------------------------------------------
"""
__author__ = 'JHao'

import requests
import json

from util.six import Empty
from threading import Thread
from datetime import datetime
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


class DoValidator(object):
    """ 执行校验 """

    @classmethod
    def validator(cls, proxy):
        """
        校验入口
        Args:
            proxy: Proxy Object
        Returns:
            Proxy Object
        """
        http_r = cls.httpValidator(proxy)
        https_r = False if not http_r else cls.httpsValidator(proxy)

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = True if http_r else False
        proxy._region = cls.region_get(proxy.proxy)
        proxy._anonymous = cls.anonymousValidator(proxy.proxy, proxy.https)
        if http_r:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            proxy.https = True if https_r else False
        else:
            proxy.fail_count += 1
        return proxy

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def region_get(cls, proxy):
        try:
            r = requests.get(url='https://searchplugin.csdn.net/api/v1/ip/get', params={'ip': proxy.split(':')[0]})
            return json.loads(r.text)['data']['address']
        except:
            return '未知或请求失败'

    @classmethod
    def anonymousValidator(cls, proxy, https):
        if https:
            url = 'https://httpbin.org/get'
            proxy = {'https': proxy}
        else:
            url = 'http://httpbin.org/get'
            proxy = {'http': proxy}

        r = requests.get(url, proxies=proxy)
        r = json.loads(r.text)
        try:
            if ',' in r.get('origin'):
                return 0
            elif r.get('headers').get('Proxy-connecttion', False):
                return 1
            else:
                return 2
        except:
            return -1


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            proxy = DoValidator.validator(proxy)
            if self.work_type == "raw":
                self.__ifRaw(proxy)
            else:
                self.__ifUse(proxy)
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {} exist'.format(self.name, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            self.log.info('UseProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
        else:
            if proxy.fail_count > self.conf.maxFailCount:
                self.log.info('UseProxyCheck - {}: {} fail, count {} delete'.format(self.name,
                                                                                    proxy.proxy.ljust(23),
                                                                                    proxy.fail_count))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {} fail, count {} keep'.format(self.name,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                self.proxy_handler.put(proxy)


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(20):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.setDaemon(True)
        thread.start()

    for thread in thread_list:
        thread.join()
