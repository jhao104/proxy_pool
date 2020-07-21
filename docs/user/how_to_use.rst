.. how_to_use

如何使用
----------

爬虫代码要对接代理池目前有两种方式: 一是通过调用API接口使用, 二是直接读取数据库.

调用API
>>>>>>>>>

启动ProxyPool的 ``server`` 后会提供如下几个http接口:

============     ========    ================       ==============
Api               Method      Description            Arg
============     ========    ================       ==============
/                GET         API介绍                 无
/get             GET         随机返回一个代理         无
/get_all         GET         返回所有代理             无
/get_status      GET         返回代理数量             无
/delete          GET         删除指定代理             proxy=host:ip
============     ========    ================       ==============

在代码中可以通过封装上面的API接口来使用代理, 例子:

.. code-block:: python

   import requests

   def get_proxy():
       return requests.get("http://127.0.0.1:5010/get/").json()

   def delete_proxy(proxy):
       requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

   # your spider code

   def getHtml():
       # ....
       retry_count = 5
       proxy = get_proxy().get("proxy")
       while retry_count > 0:
           try:
               # 使用代理访问
               html = requests.get('http://www.example.com', proxies={"http": "http://{}".format(proxy)})
               return html
           except Exception:
               retry_count -= 1
               # 删除代理池中代理
               delete_proxy(proxy)
       return None

本例中我们在本地 ``127.0.0.1`` 启动端口为 ``5010`` 的 ``server``, 使用 ``/get`` 接口获取代理, ``/delete`` 删除代理.

读数据库
>>>>>>>>>

目前支持配置两种数据库: ``REDIS`` 、 ``SSDB``.

* **REDIS** 储存结构为 ``hash``, hash name为配置项中的 **TABLE_NAME**

* **SSDB** 储存结构为 ``hash``, hash name为配置项中的 **TABLE_NAME**

可以在代码中自行读取.
