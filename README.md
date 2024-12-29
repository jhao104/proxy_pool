﻿
ProxyPool 爬虫代理IP池
=======
[![Build Status](https://travis-ci.org/jhao104/proxy_pool.svg?branch=master)](https://travis-ci.org/jhao104/proxy_pool)
[![](https://img.shields.io/badge/Powered%20by-@j_hao104-green.svg)](http://www.spiderpy.cn/blog/)
[![Requirements Status](https://requires.io/github/jhao104/proxy_pool/requirements.svg?branch=master)](https://requires.io/github/jhao104/proxy_pool/requirements/?branch=master)
[![Packagist](https://img.shields.io/packagist/l/doctrine/orm.svg)](https://github.com/jhao104/proxy_pool/blob/master/LICENSE)
[![GitHub contributors](https://img.shields.io/github/contributors/jhao104/proxy_pool.svg)](https://github.com/jhao104/proxy_pool/graphs/contributors)
[![](https://img.shields.io/badge/language-Python-green.svg)](https://github.com/jhao104/proxy_pool)

    ______                        ______             _
    | ___ \_                      | ___ \           | |
    | |_/ / \__ __   __  _ __   _ | |_/ /___   ___  | |
    |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | |
    | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___
    \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____\
                           __ / /
                          /___ /

### ProxyPool

爬虫代理IP池项目,主要功能为定时采集网上发布的免费代理验证入库，定时验证入库的代理保证代理的可用性，提供API和CLI两种使用方式。同时你也可以扩展代理源以增加代理池IP的质量和数量。

* 文档: [document](https://proxy-pool.readthedocs.io/zh/latest/) [![Documentation Status](https://readthedocs.org/projects/proxy-pool/badge/?version=latest)](https://proxy-pool.readthedocs.io/zh/latest/?badge=latest)

* 支持版本: ![](https://img.shields.io/badge/Python-2.x-green.svg) ![](https://img.shields.io/badge/Python-3.x-blue.svg)

* 测试地址: http://demo.spiderpy.cn (勿压谢谢)

* 付费代理推荐: [luminati-china](https://brightdata.grsm.io/proxyPool). 国外的亮数据BrightData（以前叫luminati）被认为是代理市场领导者，覆盖全球的7200万IP，大部分是真人住宅IP，成功率扛扛的。付费套餐多种，需要高质量代理IP的可以注册后联系中文客服，开通后有5美金赠送和教程指引(PS:用不明白的同学可以参考这个[使用教程](https://www.cnblogs.com/jhao/p/15611785.html))。


### 运行项目

##### 下载代码:

* git clone

```bash
git clone git@github.com:jhao104/proxy_pool.git
```

* releases

```bash
https://github.com/jhao104/proxy_pool/releases 下载对应zip文件
```

##### 安装依赖:

```bash
pip install -r requirements.txt
```

##### 更新配置:


```python
# setting.py 为项目配置文件

# 配置API服务

HOST = "0.0.0.0"               # IP
PORT = 5000                    # 监听端口


# 配置数据库

DB_CONN = 'redis://:pwd@127.0.0.1:8888/0'


# 配置 ProxyFetcher

PROXY_FETCHER = [
    "freeProxy01",      # 这里是启用的代理抓取方法名，所有fetch方法位于fetcher/proxyFetcher.py
    "freeProxy02",
    # ....
]
```

#### 启动项目:

```bash
# 如果已经具备运行条件, 可用通过proxyPool.py启动。
# 程序分为: schedule 调度程序 和 server Api服务

# 启动调度程序
python proxyPool.py schedule

# 启动webApi服务
python proxyPool.py server

```


# 关于 Py 312 报错的问题解决：
1. from imp import reload as reload_six
ModuleNotFoundError: No module named 'imp'
解决方法：if PY3:
import importlib
reload_six = importlib.reload
else:
reload_six = reload

2. from collections import MutableMapping
ImportError: cannot import name 'MutableMapping' from 'collections'
解决方法：from collections.abc import MutableMapping

3. from collections import Iterable, Mapping
ImportError: cannot import name 'Iterable' from 'collections'
解决方法：from collections.abc import Iterable, Mapping

4. from .packages.six.moves.http_client import (
ModuleNotFoundError: No module named 'urllib3.packages.six.moves'
解决方法：更新urllib3包到最新版本

处理完这些问题 python proxyPool.py schedule 就正常启动了。
-------------------------------------------------------------------------------

* 执行 python proxyPool.py server 也会报好多错：

1.from jinja2 import Markup, escape
ImportError: cannot import name 'Markup' from 'jinja2'
解决方法：改成 from jinja2 import pass_eval_context
from markupsafe import Markup, escape

2.from itsdangerous import json as _json
ImportError: cannot import name 'json' from 'itsdangerous'
解决方法：改成 import json as _json

3.from collections import MutableMapping
ImportError: cannot import name 'MutableMapping' from 'collections'
解决方法：改成 from collections.abc import MutableMapping

然后就可以 get 到 代理地址 了



### Docker Image

```bash
docker pull jhao104/proxy_pool

docker run --env DB_CONN=redis://:password@ip:port/0 -p 5010:5010 jhao104/proxy_pool:latest
```
### docker-compose

项目目录下运行: 
``` bash
docker-compose up -d
```

### 使用

* Api

启动web服务后, 默认配置下会开启 http://127.0.0.1:5010 的api接口服务:

| api | method | Description | params|
| ----| ---- | ---- | ----|
| / | GET | api介绍 | None |
| /get | GET | 随机获取一个代理| 可选参数: `?type=https` 过滤支持https的代理|
| /pop | GET | 获取并删除一个代理| 可选参数: `?type=https` 过滤支持https的代理|
| /all | GET | 获取所有代理 |可选参数: `?type=https` 过滤支持https的代理|
| /count | GET | 查看代理数量 |None|
| /delete | GET | 删除代理  |`?proxy=host:ip`|


* 爬虫使用

　　如果要在爬虫代码中使用的话， 可以将此api封装成函数直接使用，例如：

```python
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
            html = requests.get('http://www.example.com', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    return None
```

### 扩展代理

　　项目默认包含几个免费的代理获取源，但是免费的毕竟质量有限，所以如果直接运行可能拿到的代理质量不理想。所以，提供了代理获取的扩展方法。

　　添加一个新的代理源方法如下:

* 1、首先在[ProxyFetcher](https://github.com/jhao104/proxy_pool/blob/1a3666283806a22ef287fba1a8efab7b94e94bac/fetcher/proxyFetcher.py#L21)类中添加自定义的获取代理的静态方法，
该方法需要以生成器(yield)形式返回`host:ip`格式的代理，例如:

```python

class ProxyFetcher(object):
    # ....

    # 自定义代理源获取方法
    @staticmethod
    def freeProxyCustom1():  # 命名不和已有重复即可

        # 通过某网站或者某接口或某数据库获取代理
        # 假设你已经拿到了一个代理列表
        proxies = ["x.x.x.x:3128", "x.x.x.x:80"]
        for proxy in proxies:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
```

* 2、添加好方法后，修改[setting.py](https://github.com/jhao104/proxy_pool/blob/1a3666283806a22ef287fba1a8efab7b94e94bac/setting.py#L47)文件中的`PROXY_FETCHER`项：

　　在`PROXY_FETCHER`下添加自定义方法的名字:

```python
PROXY_FETCHER = [
    "freeProxy01",    
    "freeProxy02",
    # ....
    "freeProxyCustom1"  #  # 确保名字和你添加方法名字一致
]
```


　　`schedule` 进程会每隔一段时间抓取一次代理，下次抓取时会自动识别调用你定义的方法。

### 免费代理源

   目前实现的采集免费代理网站有(排名不分先后, 下面仅是对其发布的免费代理情况, 付费代理测评可以参考[这里](https://zhuanlan.zhihu.com/p/33576641)): 
   
  |   代理名称   |  状态  |  更新速度 |  可用率  |  地址 |    代码   |
  | ---------   |  ---- | --------  | ------  | ----- |   ------- |
  | 站大爷     |  ✔    |     ★     |   **     | [地址](https://www.zdaye.com/)    | [`freeProxy01`](/fetcher/proxyFetcher.py#L28) |
  | 66代理     |  ✔    |     ★     |   *     | [地址](http://www.66ip.cn/)         | [`freeProxy02`](/fetcher/proxyFetcher.py#L50) |
  | 开心代理     |   ✔   |     ★     |   *     | [地址](http://www.kxdaili.com/)     | [`freeProxy03`](/fetcher/proxyFetcher.py#L63)  |
  | FreeProxyList |   ✔  |    ★     |   *    | [地址](https://www.freeproxylists.net/zh/) | [`freeProxy04`](/fetcher/proxyFetcher.py#L74) |
  | 快代理       |  ✔    |     ★     |   *     | [地址](https://www.kuaidaili.com/)  | [`freeProxy05`](/fetcher/proxyFetcher.py#L92)  |
  | FateZero    |  ✔    |    ★★    |   *     | [地址](http://proxylist.fatezero.org) | [`freeProxy06`](/fetcher/proxyFetcher.py#L111) |
  | 云代理       |  ✔    |     ★     |   *     | [地址](http://www.ip3366.net/)      | [`freeProxy07`](/fetcher/proxyFetcher.py#L124) |
  | 小幻代理     |  ✔    |     ★★    |    *    | [地址](https://ip.ihuan.me/)        | [`freeProxy08`](/fetcher/proxyFetcher.py#L134) |
  | 免费代理库   |  ✔    |      ☆     |    *    | [地址](http://ip.jiangxianli.com/)   | [`freeProxy09`](/fetcher/proxyFetcher.py#L144) |
  | 89代理      |  ✔    |      ☆     |   *     | [地址](https://www.89ip.cn/)         | [`freeProxy10`](/fetcher/proxyFetcher.py#L155) |

  
  如果还有其他好的免费代理网站, 可以在提交在[issues](https://github.com/jhao104/proxy_pool/issues/71), 下次更新时会考虑在项目中支持。

### 问题反馈

　　任何问题欢迎在[Issues](https://github.com/jhao104/proxy_pool/issues) 中反馈，同时也可以到我的[博客](http://www.spiderpy.cn/blog/message)中留言。

　　你的反馈会让此项目变得更加完美。

### 贡献代码

　　本项目仅作为基本的通用的代理池架构，不接收特有功能(当然,不限于特别好的idea)。

　　本项目依然不够完善，如果发现bug或有新的功能添加，请在[Issues](https://github.com/jhao104/proxy_pool/issues)中提交bug(或新功能)描述，我会尽力改进，使她更加完美。

　　这里感谢以下contributor的无私奉献：

　　[@kangnwh](https://github.com/kangnwh) | [@bobobo80](https://github.com/bobobo80) | [@halleywj](https://github.com/halleywj) | [@newlyedward](https://github.com/newlyedward) | [@wang-ye](https://github.com/wang-ye) | [@gladmo](https://github.com/gladmo) | [@bernieyangmh](https://github.com/bernieyangmh) | [@PythonYXY](https://github.com/PythonYXY) | [@zuijiawoniu](https://github.com/zuijiawoniu) | [@netAir](https://github.com/netAir) | [@scil](https://github.com/scil) | [@tangrela](https://github.com/tangrela) | [@highroom](https://github.com/highroom) | [@luocaodan](https://github.com/luocaodan) | [@vc5](https://github.com/vc5) | [@1again](https://github.com/1again) | [@obaiyan](https://github.com/obaiyan) | [@zsbh](https://github.com/zsbh) | [@jiannanya](https://github.com/jiannanya) | [@Jerry12228](https://github.com/Jerry12228)


### Release Notes

   [changelog](https://github.com/jhao104/proxy_pool/blob/master/docs/changelog.rst)
