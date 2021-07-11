.. ext_validator

代理校验
-----------

内置校验
>>>>>>>>>

项目中使用的代理校验方法全部定义在 `validator.py`_ 中， 通过 `ProxyValidator`_ 类中提供的装饰器来区分。校验方法返回 ``True`` 表示
校验通过， 返回 ``False`` 表示校验不通过。

* 代理校验方法分为三类: ``preValidator`` 、 ``httpValidator`` 、 ``httpsValidator``：

    * **preValidator**: 预校验，在代理抓取后验证前调用，目前实现了 `formatValidator`_ 校验代理IP格式是否合法；
    * **httpValidator**: 代理可用性校验，通过则认为代理可用， 目前实现了 `httpTimeOutValidator`_ 校验；
    * **httpsValidator**: 校验代理是否支持https，目前实现了 `httpsTimeOutValidator`_ 校验。


.. _validator.py: https://github.com/jhao104/proxy_pool/blob/release-2.3.0/helper/validator.py
.. _ProxyValidator: https://github.com/jhao104/proxy_pool/blob/release-2.3.0/helper/validator.py#L29
.. _formatValidator: https://github.com/jhao104/proxy_pool/blob/release-2.3.0/helper/validator.py#L51
.. _httpTimeOutValidator: https://github.com/jhao104/proxy_pool/blob/release-2.3.0/helper/validator.py#L58
.. _httpsTimeOutValidator: https://github.com/jhao104/proxy_pool/blob/release-2.3.0/helper/validator.py#L71

每种校验可以定义多个方法，只有 **所有** 方法都返回 ``True`` 的情况下才视为该校验通过，校验方法执行顺序为: 先执行 **httpValidator** ， 前者通过后再执行 **httpsValidator** 。
只有 `preValidator` 校验通过的代理才会进入可用性校验， `httpValidator` 校验通过后认为代理可用准备更新入代理池, `httpValidator` 校验通过后视为代理支持https更新代理的 `https` 属性为 `True` 。

扩展校验
>>>>>>>>>

在 `validator.py`_ 已有自定义校验的示例，自定义函数需返回True或者False，使用 `ProxyValidator`_ 中提供的装饰器来区分校验类型。 下面是两个例子:

* 1. 自定义一个代理可用性的校验(``addHttpValidator``):

.. code-block:: python

    @ProxyValidator.addHttpValidator
    def customValidatorExample01(proxy):
        """自定义代理可用性校验函数"""
        proxies = {"http": "http://{proxy}".format(proxy=proxy)}
        try:
            r = requests.get("http://www.baidu.com/", headers=HEADER, proxies=proxies, timeout=5)
            return True if r.status_code == 200 and len(r.content) > 200 else False
        except Exception as e:
            return False

* 2. 自定义一个代理是否支持https的校验(``addHttpsValidator``):

.. code-block:: python

    @ProxyValidator.addHttpsValidator
    def customValidatorExample02(proxy):
        """自定义代理是否支持https校验函数"""
        proxies = {"https": "https://{proxy}".format(proxy=proxy)}
        try:
            r = requests.get("https://www.baidu.com/", headers=HEADER, proxies=proxies, timeout=5, verify=False)
            return True if r.status_code == 200 and len(r.content) > 200 else False
        except Exception as e:
            return False

注意，比如在运行代理可用性校验时，所有被 ``ProxyValidator.addHttpValidator`` 装饰的函数会被依次按定义顺序执行，只有当所有函数都返回True时才会判断代理可用。 ``HttpsValidator`` 运行机制也是如此。
