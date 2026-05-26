.. how_to_manage

服务管理
--------

``proxy_pool.sh`` 是项目的服务管理脚本, 提供统一的命令行接口来启动、停止和管理服务。

基本用法
>>>>>>>>>

.. code-block:: console

    $ ./proxy_pool.sh <command> [options]

可用命令
>>>>>>>>>

start - 启动服务
^^^^^^^^^^^^^^^^

启动所有服务(调度程序和API服务)。

.. code-block:: console

    # 后台启动(默认)
    $ ./proxy_pool.sh start

    # 前台启动(适用于容器环境)
    $ ./proxy_pool.sh start --fg

后台模式下, 服务会在后台运行, 并生成 ``proxy_pool.pid`` 文件记录进程ID。

前台模式下, 服务在当前终端运行, 按 ``Ctrl+C`` 可停止服务。

stop - 停止服务
^^^^^^^^^^^^^^^^

停止所有正在运行的服务。

.. code-block:: console

    $ ./proxy_pool.sh stop

脚本会读取 ``proxy_pool.pid`` 文件, 向所有子进程发送终止信号。

restart - 重启服务
^^^^^^^^^^^^^^^^^^^

重启所有服务。

.. code-block:: console

    # 后台重启
    $ ./proxy_pool.sh restart

    # 前台重启
    $ ./proxy_pool.sh restart --fg

status - 查看状态
^^^^^^^^^^^^^^^^^^

查看当前服务运行状态。

.. code-block:: console

    $ ./proxy_pool.sh status

输出示例::

    [INFO] Services: 2 running, 0 dead
      PID 12345: running
      PID 12346: running

环境变量
>>>>>>>>>

PYTHON
^^^^^^

指定Python解释器路径, 默认为 ``python``。

.. code-block:: console

    $ PYTHON=python3 ./proxy_pool.sh start

PID 文件
>>>>>>>>

服务启动后会在项目根目录生成 ``proxy_pool.pid`` 文件, 记录所有子进程的PID。

该文件用于:

- ``stop`` 命令识别需要终止的进程
- ``status`` 命令检查进程状态
- 防止重复启动

``stop`` 命令执行后会自动删除该文件。

Docker 环境
>>>>>>>>>>>>

在Docker环境中, 建议使用前台模式:

.. code-block:: dockerfile

    ENTRYPOINT ["tini", "--", "bash", "proxy_pool.sh", "start", "--fg"]

``docker-compose.yml`` 示例:

.. code-block:: yaml

    version: '2'
    services:
      proxy_pool:
        build: .
        container_name: proxy_pool
        ports:
          - "5010:5010"
        links:
          - proxy_redis
        environment:
          DB_CONN: "redis://@proxy_redis:6379/0"
      proxy_redis:
        image: "redis"
        container_name: proxy_redis

故障排除
>>>>>>>>>

服务启动失败
^^^^^^^^^^^^^

检查日志输出, 确认配置是否正确:

.. code-block:: console

    # 前台启动查看详细日志
    $ ./proxy_pool.sh start --fg

端口被占用
^^^^^^^^^^^

如果API端口被占用, 修改 ``setting.py`` 中的 ``PORT`` 配置:

.. code-block:: python

    PORT = 5010  # 修改为其他端口

无法停止服务
^^^^^^^^^^^^^

如果 ``stop`` 命令无法停止服务, 可手动终止:

.. code-block:: console

    # 查看PID文件
    $ cat proxy_pool.pid

    # 手动终止进程
    $ kill <PID>

    # 删除PID文件
    $ rm proxy_pool.pid
