.. ProxyPool documentation master file, created by
   sphinx-quickstart on Wed Jul  8 16:13:42 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ProxyPool
=====================================

::

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

Python爬虫代理IP池

安装
-----

* 下载代码

.. code-block:: console

    $ git clone git@github.com:jhao104/proxy_pool.git

* 安装依赖

.. code-block:: console

    $ pip install -r requirements.txt

* 更新配置

.. code-block:: python

   HOST = "0.0.0.0"
   PORT = 5000

   DB_CONN = 'redis://@127.0.0.1:8888'

   PROXY_FETCHER = [
       "freeProxy01",
       "freeProxy02",
       # ....
   ]

* 启动项目

.. code-block:: console

    $ python proxyPool.py schedule
    $ python proxyPool.py server

使用
______

* API

============     ========    ================       ==============
Api               Method      Description            Params
============     ========    ================       ==============
/                GET         API介绍                 无
/get             GET         返回一个代理             可选参数: `?type=https` 过滤支持https的代理
/pop             GET         返回并删除一个代理        可选参数: `?type=https` 过滤支持https的代理
/all             GET         返回所有代理             可选参数: `?type=https` 过滤支持https的代理
/count           GET         返回代理数量             无
/delete          GET         删除指定代理             `?proxy=host:ip`
============     ========    ================       ==============


* 爬虫

.. code-block:: python

   import requests

   def get_proxy():
       return requests.get("http://127.0.0.1:5010/get?type=https").json()

   def delete_proxy(proxy):
       requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

   # your spider code

   def getHtml():
       # ....
       retry_count = 5
       proxy = get_proxy().get("proxy")
       while retry_count > 0:
           try:
               html = requests.get('https://www.example.com', proxies={"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)})
               # 使用代理访问
               return html
           except Exception:
               retry_count -= 1
               # 删除代理池中代理
               delete_proxy(proxy)
       return None

Contents
--------

.. toctree::
   :maxdepth: 2

   user/index
   dev/index
   changelog
