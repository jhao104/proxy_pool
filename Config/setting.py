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

import sys
from os import getenv
from logging import getLogger

log = getLogger(__name__)

HEADER = """
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

PY3 = sys.version_info >= (3,)

DB_TYPE = getenv('db_type', 'SSDB').upper()
DB_HOST = getenv('db_host', '127.0.0.1')
DB_PORT = getenv('db_port', 8888)
DB_PASSWORD = getenv('db_password', '')


""" 数据库配置 """
DATABASES = {
    "default": {
        "TYPE": DB_TYPE,
        "HOST": DB_HOST,
        "PORT": DB_PORT,
        "NAME": "proxy",
        "PASSWORD": DB_PASSWORD
    }
}

# register the proxy getter function

PROXY_GETTER = [
    "freeProxy01",
    # "freeProxy02",
    "freeProxy03",
    "freeProxy04",
    "freeProxy05",
    # "freeProxy06",
    "freeProxy07",
    # "freeProxy08",
    "freeProxy09",
    "freeProxy13",
    "freeProxy14",
    "freeProxy14",
]

""" API config http://127.0.0.1:5010 """
SERVER_API = {
    "HOST": "0.0.0.0",  # The ip specified which starting the web API
    "PORT": 5010  # port number to which the server listens to
}


class ConfigError(BaseException):
    pass


def checkConfig():
    if DB_TYPE not in ["SSDB", "REDIS"]:
        raise ConfigError('db_type Do not support: %s, must SSDB/REDIS .' % DB_TYPE)

    if type(DB_PORT) == str and not DB_PORT.isdigit():
        raise ConfigError('if db_port is string, it must be digit, not %s' % DB_PORT)

    from ProxyGetter import getFreeProxy
    illegal_getter = list(filter(lambda key: not hasattr(getFreeProxy.GetFreeProxy, key), PROXY_GETTER))
    if len(illegal_getter) > 0:
        raise ConfigError("ProxyGetter: %s does not exists" % "/".join(illegal_getter))


checkConfig()
