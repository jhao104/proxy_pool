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
from helper.validators import validators
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


def _validator(proxy_obj):
    """ 检测代理是否可用 """

    def _do_validate(proxy):
        for func in validators:
            if not func(proxy):
                return False
        return True

    rs = _do_validate(proxy_obj.proxy)
    proxy_obj.check_count += 1
    proxy_obj.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if rs:
        proxy_obj.last_status = 1
        if proxy_obj.fail_count > 0:
            proxy_obj.fail_count -= 1
    else:
        proxy_obj.last_status = 0
        proxy_obj.fail_count += 1
    return proxy_obj


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
            proxy = _validator(proxy)
            if self.work_type == "raw":
                self._if_raw(proxy)
            else:
                self._if_use(proxy)
            self.target_queue.task_done()

    def _if_raw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {} exist'.format(self.name, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
        else:
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def _if_use(self, proxy):
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
        thread.start()

    for thread in thread_list:
        thread.join()
