# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
-------------------------------------------------
"""

# database config

DATABASES = {
    "default": {
        "TYPE": "SSDB",  # TYPE SSDB/MONGODB if use redis, only modify the host port, the type should be SSDB
        "HOST": "127.0.0.1",
        "PORT": 8888,
        "NAME": "proxy",
        "PASSWORD": ""

    }
}

# register the proxy getter function

PROXY_GETTER = [
    "freeProxyFirst",
    "freeProxySecond",
    # "freeProxyThird",
    "freeProxyFourth",
    "freeProxyFifth",
    # "freeProxySixth"
    "freeProxySeventh",
    # "freeProxyEight",
    # "freeProxyNinth",
    "freeProxyTen",
    "freeProxyEleven",
    "freeProxyTwelve",
    # foreign website, outside the wall
    "freeProxyWallFirst",
    "freeProxyWallSecond",
    "freeProxyWallThird"
]


# # API config http://127.0.0.1:5010

SERVER_API = {
    "HOST": "0.0.0.0",  # The ip specified which starting the web API
    "PORT": 5010  # port number to which the server listens to
}
