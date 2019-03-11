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
from os import getenv


class ConfigError(BaseException):
    pass


DB_TYPE = getenv('db_type', 'SSDB')

if DB_TYPE == 'SSDB':
    DB_HOST = getenv('ssdb_host', '127.0.0.1')
    DB_PORT = getenv('ssdb_port', '6379')
elif DB_TYPE == 'MONGODB':
    DB_HOST = getenv('mongodb_host', '127.0.0.1')
    DB_PORT = getenv('mongodb_host', '27017')
else:
    raise ConfigError('Unknown database type, your environment variable `db_type` should be one of SSDB/MONGODB.')

DATABASES = {
    "default": {
        "TYPE": DB_TYPE,  # TYPE SSDB/MONGODB if use redis, only modify the host port, the type should be SSDB
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "NAME": "proxy",
        "PASSWORD": ""

    }
}

# register the proxy getter function

PROXY_GETTER = [
    "freeProxyFirst",
    "freeProxySecond",
    # "freeProxyThird",  # 网站已不能访问
    "freeProxyFourth",
    "freeProxyFifth",
    # "freeProxySixth"   # 不再提供免费代理
    "freeProxySeventh",
    # "freeProxyEight",
    # "freeProxyNinth",
    "freeProxyTen",
    "freeProxyEleven",
    "freeProxyTwelve",
    # foreign website, outside the wall
    # "freeProxyWallFirst",
    # "freeProxyWallSecond",
    # "freeProxyWallThird"
]

# # API config http://127.0.0.1:5010

SERVER_API = {
    "HOST": "0.0.0.0",  # The ip specified which starting the web API
    "PORT": 5010  # port number to which the server listens to
}
