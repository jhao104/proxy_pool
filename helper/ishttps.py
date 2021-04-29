# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     isHttps
   Description :
   Author :        nansirc（https://github.com/jiannanya）
   date：          2021/4/26
-------------------------------------------------
   Change Activity:
                   2021/4/2:
-------------------------------------------------
"""
__author__ = 'jiannanya'

from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from helper.proxy import Proxy
import requests
from requests.exceptions import RequestException
import threading

class HttpsCheckerThread(threading.Thread):
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.result = 0

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

class HttpsChecker(object):

    __headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'cache-control': 'max-age=0',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
            }

    __proxy_handler = ProxyHandler()
    __log = LogHandler("ishttps-checker")

    @staticmethod
    def __put_proxy(proxy):
        HttpsChecker.__proxy_handler.put(proxy)

    @staticmethod
    def __delete_proxy(proxy):
        HttpsChecker.__proxy_handler.delete(proxy)

    @staticmethod
    def __proxy_check(proxy):
        try:
            response = requests.get("https://www.qq.com/", headers=HttpsChecker.__headers, proxies={"https": "https://{}".format(proxy.proxy)},timeout=3)
            if response.status_code == 200:
                proxy.type = "https"
                HttpsChecker.__delete_proxy(proxy)
                HttpsChecker.__put_proxy(proxy)#(Proxy.createFromJson(json.dumps(proxy)))
                HttpsChecker.__log.info("Https Check - {} is https".format(proxy.proxy))
        except RequestException:
            proxy.type = "http"
            HttpsChecker.__delete_proxy(proxy)
            HttpsChecker.__put_proxy(proxy)#(Proxy.createFromJson(json.dumps(proxy)))
            HttpsChecker.__log.info("Https Check - {} is http".format(proxy.proxy))

    @staticmethod
    def __proxy_get_all():
        return HttpsChecker.__proxy_handler.getAll()


    @staticmethod
    def https_check():
        proxyList = HttpsChecker.__proxy_get_all()
        HttpsChecker.__log.info("Https Check Start!")
        threadList = []
        for proxy in proxyList:
            t=HttpsCheckerThread(HttpsChecker.__proxy_check,proxy)
            threadList.append(t)
            t.start()
        for t in threadList:
            t.join()
        HttpsChecker.__log.info("Https Check Done!")

def _runHttpsChecker():
    HttpsChecker.https_check()

if __name__ == "__main__":
    #test below
    HttpsChecker.https_check()
    # for _ in range(30):
    #     __proxy_check(__get_proxy())
    #all = __proxy_get_all()
    #print(type(__proxy_get_all()[0]['proxy']))
