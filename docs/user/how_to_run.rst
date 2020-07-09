.. how_to_run


如何运行
---------

下载代码
>>>>>>>>>

本项目需要下载代码到本地运行, 通过 ``git`` 下载:

.. code-block:: console

    $ git clone git@github.com:jhao104/proxy_pool.git

或者下载特定的 ``release`` 版本:

.. code-block:: console

    https://github.com/jhao104/proxy_pool/releases

安装依赖
>>>>>>>>>

到项目目录下使用 ``pip`` 安装依赖库:

.. code-block:: console

    $ pip install -r requirements.txt


更新配置
>>>>>>>>>

配置文件 ``setting.py`` 位于项目的主目录下:

.. code-block:: python

    # 配置API服务

    HOST = "0.0.0.0"               # IP
    PORT = 5000                    # 监听端口

    # 配置数据库

    DB_CONN = 'redis://@127.0.0.1:8888/0'

    # 配置 ProxyFetcher

    PROXY_FETCHER = [
        "freeProxy01",      # 这里是启用的代理抓取方法，所有fetch方法位于fetcher/proxyFetcher.py
        "freeProxy02",
        # ....
    ]

更多配置请参考 :doc:`/user/how_to_config`

启动项目
>>>>>>>>>

如果已配置好运行环境, 具备运行条件, 可以通过 ``proxyPool.py`` 启动.  ``proxyPool.py`` 是项目的CLI入口.
完整程序包含两部份: ``schedule`` 调度程序和 ``server`` API服务, 调度程序负责采集和验证代理, API服务提供代理服务HTTP接口.

通过命令行程序分别启动调度程序和API服务:

.. code-block:: console

    # 启动调度程序
    $ python proxyPool.py schedule

    # 启动webApi服务
    $ python proxyPool.py server

