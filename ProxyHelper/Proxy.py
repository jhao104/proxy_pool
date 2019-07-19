# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Proxy
   Description :   代理对象类型封装
   Author :        JHao
   date：          2019/7/11
-------------------------------------------------
   Change Activity:
                   2019/7/11: 代理对象类型封装
-------------------------------------------------
"""
__author__ = 'JHao'


class Proxy(object):

    def __init__(self, proxy):
        if isinstance(proxy, str):
            self._proxy = proxy
            self._fail_count = 0
            self._region = ""
            self._type = ""
            self._last_status = ""
            self._last_time = ""

        elif isinstance(proxy, dict):
            self._proxy = proxy.get("proxy")
            self._fail_count = proxy.get("fail_count")
            self._region = proxy.get("region")
            self._type = proxy.get("type")
            self._last_status = proxy.get("last_status")
            self._last_time = proxy.get("last_time")

        else:
            raise TypeError("proxy arg invalid")

    @property
    def proxy(self):
        """ 代理 ip:port """
        return self._proxy

    @property
    def fail_count(self):
        """ 检测失败次数 """
        return self._fail_count

    @property
    def region(self):
        """ 地理位置(国家/城市) """
        return self._region

    @property
    def type(self):
        """ 透明/匿名/高匿 """
        return self._type

    @property
    def last_status(self):
        """ 最后一次检测结果 """
        return self._last_status

    @property
    def last_time(self):
        """ 最后一次检测时间 """
        return self._last_time

    # --- proxy method ---
    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value

    @region.setter
    def region(self, value):
        self._region = value

    @type.setter
    def type(self, value):
        self._type = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value):
        self._last_time = value


def proxy2Json(proxy):
    return {"proxy": proxy.proxy,
            "fail_count": proxy.fail_count,
            "region": proxy.region,
            "type": proxy.type,
            "last_status": proxy.last_status,
            "last_time": proxy.last_time}


if __name__ == '__main__':
    p = Proxy("127.0.0.1:8080")

    import json

    print(json.dumps(p, default=proxy2Json))
