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

BANNER = r"""
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

VERSION = "2.4.0"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:autosurf@127.0.0.1:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'


# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "freeProxy23",
    "freeProxy01",
<<<<<<< HEAD
#     "freeProxy02", # Not working.
#     "freeProxy03",
    # "freeProxy04",
#     "freeProxy05",
#     "freeProxy06", # Not working.
=======
    "freeProxy02",
    "freeProxy03",
    "freeProxy04",
    "freeProxy05",
    "freeProxy06",
>>>>>>> dd0156b05fc41bed7c2cd4189493effada6c98b9
    "freeProxy07",
#     "freeProxy08", # Not working.
    "freeProxy09",
<<<<<<< HEAD
    "freeProxy10",
    "freeProxy11",
    "freeProxy12",
    "freeProxy13",
    "freeProxy14",
    "freeProxy15",
    "freeProxy16",
    "freeProxy17",
    "freeProxy18",
    "freeProxy19",
    "freeProxy20",
    "freeProxy21",
    "freeProxy22",
=======
    "freeProxy10"
>>>>>>> dd0156b05fc41bed7c2cd4189493effada6c98b9
]

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://web.archive.org/web/20201028232110/https://shop.k9sforwarriors.org/products/bumper-sticker-5-x-5"

# 代理验证时超时时间
VERIFY_TIMEOUT = 3

# 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 3

# 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
# MAX_FAIL_RATE = 0.1

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 10000

# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"
