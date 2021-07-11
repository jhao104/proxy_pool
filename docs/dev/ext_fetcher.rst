.. ext_fetcher

扩展代理源
-----------

项目默认包含几个免费的代理获取源，但是免费的毕竟质量有限，如果直接运行可能拿到的代理质量不理想。因此提供了用户自定义扩展代理获取的方法。

如果要添加一个新的代理获取方法, 过程如下:

1. 首先在 `ProxyFetcher`_ 类中添加自定义的获取代理的静态方法，该方法需要以生成器(yield)形式返回 ``host:ip`` 格式的代理字符串， 例如：

.. code-block:: python

    class ProxyFetcher(object):
    # ....
    # 自定义代理源获取方法
    @staticmethod
    def freeProxyCustom01():  # 命名不和已有重复即可
        # 通过某网站或者某接口或某数据库获取代理
        # 假设你已经拿到了一个代理列表
        proxies = ["x.x.x.x:3128", "x.x.x.x:80"]
        for proxy in proxies:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回

2. 添加好方法后，修改配置文件 `setting.py`_ 中的 ``PROXY_FETCHER`` 项， 加入刚才添加的自定义方法的名字:

.. code-block:: python

    PROXY_FETCHER = [
        # ....
        "freeProxyCustom01"  #  # 确保名字和你添加方法名字一致
    ]

.. _ProxyFetcher: https://github.com/jhao104/proxy_pool/blob/1a3666283806a22ef287fba1a8efab7b94e94bac/fetcher/proxyFetcher.py#L20
.. _setting.py: https://github.com/jhao104/proxy_pool/blob/1a3666283806a22ef287fba1a8efab7b94e94bac/setting.py#L47