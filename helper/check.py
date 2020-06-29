# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06:
-------------------------------------------------
"""
__author__ = 'JHao'

from util.six import Empty
from threading import Thread
from datetime import datetime

from helper.proxy import Proxy
from util.validators import validators
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler


def proxyCheck(proxy_obj):
    """
    检测代理是否可用
    :param proxy_obj: Proxy object
    :return: Proxy object, status
    """

    def __proxyCheck(proxy):
        for func in validators:
            if not func(proxy):
                return False
        return True

    if __proxyCheck(proxy_obj.proxy):
        # 检测通过 更新proxy属性
        proxy_obj.check_count += 1
        proxy_obj.last_status = 1
        proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if proxy_obj.fail_count > 0:
            proxy_obj.fail_count -= 1
        return proxy_obj
    else:
        proxy_obj.check_count += 1
        proxy_obj.last_status = 0
        proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy_obj.fail_count += 1
        return proxy_obj


class Checker(Thread):
    """
    多线程检测代理是否可用
    """

    def __init__(self, check_type, queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.type = check_type
        self.log = LogHandler(self.name)
        self.proxy_handler = ProxyHandler()
        self.queue = queue

    def run(self):
        self.log.info("ProxyCheck - {}  : start".format(self.name))
        while True:
            try:
                proxy_json = self.queue.get(block=False)
            except Empty:
                self.log.info("ProxyCheck - {}  : complete".format(self.name))
                break

            proxy = Proxy.createFromJson(proxy_json)
            proxy = proxyCheck(proxy)
            if self.type == "raw":
                if proxy.last_status:
                    if self.proxy_handler.exists(proxy.proxy):
                        self.log.info('ProxyCheck - {}  : {} exists'.format(self.name, proxy.proxy.ljust(23)))
                    else:
                        self.log.info('ProxyCheck - {}  : {} success'.format(self.name, proxy.proxy.ljust(23)))
                        self.proxy_handler.put(proxy)
                else:
                    self.log.info('ProxyCheck - {}  : {} fail'.format(self.name, proxy.proxy.ljust(23)))
            else:
                pass
            self.queue.task_done()


def runChecker(tp, queue):
    """
    run Checker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(20):
        thread_list.append(Checker(tp, queue, "thread_%s" % str(index).zfill(2)))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
