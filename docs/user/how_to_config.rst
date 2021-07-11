.. how_to_config

配置参考
---------

配置文件 ``setting.py`` 位于项目的主目录下, 配置主要分为四类: **服务配置** 、 **数据库配置** 、 **采集配置** 、 **校验配置**.

服务配置
>>>>>>>>>

* ``HOST``

    API服务监听的IP, 本机访问设置为 ``127.0.0.1``, 开启远程访问设置为: ``0.0.0.0``.

* ``PORT``

    API服务监听的端口.

数据库配置
>>>>>>>>>>>

* ``DB_CONN``

    用户存放代理IP的数据库URI, 配置格式为: ``db_type://[[user]:[pwd]]@ip:port/[db]``.

    目前支持的db_type有: ``ssdb`` 、 ``redis``.

    配置示例:

.. code-block:: python

    # SSDB IP: 127.0.0.1  Port: 8888
    DB_CONN = 'ssdb://@127.0.0.1:8888'
    # SSDB IP: 127.0.0.1  Port: 8899  Password:  123456
    DB_CONN = 'ssdb://:123456@127.0.0.1:8888'

    # Redis IP: 127.0.0.1  Port: 6379
    DB_CONN = 'redis://@127.0.0.1:6379'
    # Redis IP: 127.0.0.1  Port: 6379  Password:  123456
    DB_CONN = 'redis://:123456@127.0.0.1:6379'
    # Redis IP: 127.0.0.1  Port: 6379  Password:  123456  DB: 15
    DB_CONN = 'redis://:123456@127.0.0.1:6379/15'


* ``TABLE_NAME``

    存放代理的数据载体名称, ssdb和redis的存放结构为hash.

采集配置
>>>>>>>>>

* ``PROXY_FETCHER``

    启用的代理采集方法名, 代理采集方法位于 ``fetcher/proxyFetcher.py`` 类中.

    由于各个代理源的稳定性不容易掌握, 当某个代理采集方法失效时, 可以该配置中注释掉其名称.

    如果有增加某些代理采集方法, 也请在该配置中添加其方法名, 具体请参考 :doc:`/dev/extend_fetcher`.

    调度程序每次执行采集任务时都会再次加载该配置, 保证每次运行的采集方法都是有效的.

校验配置
>>>>>>>>>

* ``HTTP_URL``

    用于检验代理是否可用的地址, 默认为 ``http://httpbin.org``, 可根据使用场景修改为其他地址.

* ``HTTPS_URL``

    用于检验代理是否支持HTTPS的地址, 默认为 ``https://www.qq.com``, 可根据使用场景修改为其他地址.

* ``VERIFY_TIMEOUT``

    检验代理的超时时间, 默认为 ``10`` , 单位秒. 使用代理访问 ``HTTP(S)_URL`` 耗时超过 ``VERIFY_TIMEOUT`` 时, 视为代理不可用.

* ``MAX_FAIL_COUNT``

    检验代理允许最大失败次数, 默认为 ``0``, 即出错一次即删除.

* ``POOL_SIZE_MIN``

    代理检测定时任务运行前若代理数量小于 `POOL_SIZE_MIN`, 则先运行抓取程序.