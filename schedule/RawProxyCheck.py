# # -*- coding: utf-8 -*-
# """
# -------------------------------------------------
#    File Name：     RawProxyCheck
#    Description :   check raw_proxy to useful
#    Author :        JHao
#    date：          2019/8/6
# -------------------------------------------------
#    Change Activity:
#                    2019/8/6: check raw_proxy to useful
# -------------------------------------------------
# """
# __author__ = 'JHao'
#
# from threading import Thread
#
# try:
#     from Queue import Empty, Queue  # py2
# except:
#     from queue import Empty, Queue  # py3
#
# from util import LogHandler
# from handler import ProxyManager
# from helper import Proxy, checkProxyUseful
#
#
# class RawProxyCheck(ProxyManager, Thread):
#     def __init__(self, queue, thread_name):
#         ProxyManager.__init__(self)
#         Thread.__init__(self, name=thread_name)
#         self.log = LogHandler('raw_proxy_check')
#         self.queue = queue
#
#     def run(self):
#         self.log.info("RawProxyCheck - {}  : start".format(self.name))
#         self.db.changeTable(self.useful_proxy_queue)
#         while True:
#             try:
#                 proxy_json = self.queue.get(block=False)
#             except Empty:
#                 self.log.info("RawProxyCheck - {}  : exit".format(self.name))
#                 break
#
#             proxy_obj = Proxy.newProxyFromJson(proxy_json)
#
#             proxy_obj, status = checkProxyUseful(proxy_obj)
#             if status:
#                 if self.db.exists(proxy_obj.proxy):
#                     self.log.info('RawProxyCheck - {}  : {} validation exists'.format(self.name,
#                                                                                       proxy_obj.proxy.ljust(20)))
#                 else:
#                     self.db.put(proxy_obj)
#                     self.log.info(
#                         'RawProxyCheck - {}  : {} validation pass'.format(self.name, proxy_obj.proxy.ljust(20)))
#             else:
#                 self.log.info('RawProxyCheck - {}  : {} validation fail'.format(self.name, proxy_obj.proxy.ljust(20)))
#             self.queue.task_done()
#
#
# def doRawProxyCheck():
#     proxy_queue = Queue()
#
#     pm = ProxyManager()
#     pm.db.changeTable(pm.raw_proxy_queue)
#     for _proxy in pm.db.getAll():
#         proxy_queue.put(_proxy)
#     pm.db.clear()
#
#     thread_list = list()
#     for index in range(20):
#         thread_list.append(RawProxyCheck(proxy_queue, "thread_%s" % index))
#
#     for thread in thread_list:
#         thread.start()
#
#     for thread in thread_list:
#         thread.join()
#
#
# if __name__ == '__main__':
#     doRawProxyCheck()
