
爬虫IP代理池
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

##### [介绍文档](https://github.com/jhao104/proxy_pool/blob/master/doc/introduce.md)

* 支持版本: ![](https://img.shields.io/badge/Python-2.x-green.svg) ![](https://img.shields.io/badge/Python-3.x-blue.svg)

* 测试地址: http://118.24.52.95:5010 (单机勿压。感谢, 恶意访问者关小黑屋)

### 下载安装

* 下载源码:

```shell
git clone git@github.com:jhao104/proxy_pool.git

或者直接到https://github.com/jhao104/proxy_pool 下载zip文件
```

* 安装依赖:

```shell
pip install -r requirements.txt
```

* 配置Config/setting.py:

```shell
# Config/setting.py 为项目配置文件

# 配置DB     
DATABASES = {
    "default": {
        "TYPE": "SSDB",        # 目前支持SSDB或redis数据库
        "HOST": "127.0.0.1",   # db host
        "PORT": 8888,          # db port，例如SSDB通常使用8888，redis通常默认使用6379
        "NAME": "proxy",       # 默认配置
        "PASSWORD": ""         # db password

    }
}


# 配置 ProxyGetter

PROXY_GETTER = [
    "freeProxy01",      # 这里是启用的代理抓取函数名，可在ProxyGetter/getFreeProxy.py 扩展
    "freeProxy02",
    ....
]


# 配置 API服务

SERVER_API = {
    "HOST": "0.0.0.0",  # 监听ip, 0.0.0.0 监听所有IP
    "PORT": 5010        # 监听端口
}
       
# 上面配置启动后，代理池访问地址为 http://127.0.0.1:5010

```

* 启动:

```shell
# 如果你的依赖已经安全完成并且具备运行条件,可以在cli下运行通过ProxyPool.py启动
# 程序分为: schedule 调度程序 和 webserver Api服务

# 首先启动调度程序
>>>python proxyPool.py schedule

# 然后启动webApi服务
>>>python proxyPool.py webserver


```


### 使用

　　启动过几分钟后就能看到抓取到的代理IP，你可以直接到数据库中查看，推荐一个[SSDB可视化工具](https://github.com/jhao104/SSDBAdmin)。

　　也可以通过api访问http://127.0.0.1:5010 查看。

* Api

| api | method | Description | arg|
| ----| ---- | ---- | ----|
| / | GET | api介绍 | None |
| /get | GET | 随机获取一个代理 | None|
| /get_all | GET | 获取所有代理 |None|
| /get_status | GET | 查看代理数量 |None|
| /delete | GET | 删除代理  |proxy=host:ip|

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
            html = requests.get('https://www.example.com', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 出错5次, 删除代理池中代理
    delete_proxy(proxy)
    return None
```

### 扩展代理

　　项目默认包含几个免费的代理获取方法，但是免费的毕竟质量不好，所以如果直接运行可能拿到的代理质量不理想。所以，提供了代理获取的扩展方法。

　　添加一个新的代理获取方法如下:

* 1、首先在[GetFreeProxy](https://github.com/jhao104/proxy_pool/blob/b9ccdfaada51b57cfb1bbd0c01d4258971bc8352/ProxyGetter/getFreeProxy.py#L32)类中添加你的获取代理的静态方法，
该方法需要以生成器(yield)形式返回`host:ip`格式的代理，例如:

```python

class GetFreeProxy(object):
    # ....

    # 你自己的方法
    @staticmethod
    def freeProxyCustom():  # 命名不和已有重复即可

        # 通过某网站或者某接口或某数据库获取代理 任意你喜欢的姿势都行
        # 假设你拿到了一个代理列表
        proxies = ["139.129.166.68:3128", "139.129.166.61:3128", ...]
        for proxy in proxies:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式就行
```

* 2、添加好方法后，修改Config/setting.py文件中的`PROXY_GETTER`项：

　　在`PROXY_GETTER`下添加自定义的方法的名字:

```shell
PROXY_GETTER = [
    "freeProxy01",    
    "freeProxy02",
    ....
    "freeProxyCustom"  #  # 确保名字和你添加方法名字一致
]
```


　　`ProxySchedule`会每隔一段时间抓取一次代理，下次抓取时会自动识别调用你定义的方法。

### 代理采集

   目前实现的采集免费代理网站有(排名不分先后, 下面仅是对其发布的免费代理情况, 付费代理测评可以参考[这里](https://zhuanlan.zhihu.com/p/33576641)): 
   
  | 厂商名称 |  状态  |  更新速度 |  可用率  |  是否被墙  |  地址 |
  | -----   |  ---- | --------  | ------ | --------- | ----- |
  | 无忧代理 |  可用  | 几分钟一次 |   *     |  否       | [地址](http://www.data5u.com/free/index.html) |
  | 66代理   | 可用  | 更新很慢   |   *     |  否      | [地址](http://www.66ip.cn/) |
  | 西刺代理 | 可用   | 几分钟一次 |   *     | 否       | [地址](http://www.xicidaili.com)|
  | 全网代理 |  可用  | 几分钟一次 |   *     |  否      | [地址](http://www.goubanjia.com/)|
  | 训代理 |  已关闭免费代理  | * |   *     |  否      | [地址](http://www.xdaili.cn/)|
  | 快代理 |  可用  |几分钟一次|   *     |  否      | [地址](https://www.kuaidaili.com/)|
  | 云代理 |  可用  |几分钟一次|   *     |  否      | [地址](http://www.ip3366.net/)|
  | IP海 |  可用  |几小时一次|   *     |  否      | [地址](http://www.iphai.com/)|
  | 免费IP代理库 |  可用  |快|   *     |  否      | [地址](http://ip.jiangxianli.com/)|
  | 中国IP地址 |  可用  |几分钟一次|   *     |  是      | [地址](http://cn-proxy.com/)|
  | Proxy List |  可用  |几分钟一次|   *     |  是      | [地址](https://proxy-list.org/chinese/index.php)|
  | ProxyList+ |  可用  |几分钟一次|   *     |  是      | [地址](https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1)|
  
  如果还有其他好的免费代理网站, 可以在提交在[issues](https://github.com/jhao104/proxy_pool/issues/71), 下次更新时会考虑在项目中支持。

### 问题反馈

　　任何问题欢迎在[Issues](https://github.com/jhao104/proxy_pool/issues) 中反馈，如果没有账号可以去 我的[博客](http://www.spiderpy.cn/blog/message)中留言。

　　你的反馈会让此项目变得更加完美。

### 贡献代码

　　本项目仅作为基本的通用的代理池架构，不接收特有功能(当然,不限于特别好的idea)。

　　本项目依然不够完善，如果发现bug或有新的功能添加，请在[Issues](https://github.com/jhao104/proxy_pool/issues)中提交bug(或新功能)描述，在确认后提交你的代码。

　　这里感谢以下contributor的无私奉献：

　　[@kangnwh](https://github.com/kangnwh)| [@bobobo80](https://github.com/bobobo80)| [@halleywj](https://github.com/halleywj)| [@newlyedward](https://github.com/newlyedward)| [@wang-ye](https://github.com/wang-ye)| [@gladmo](https://github.com/gladmo)| [@bernieyangmh](https://github.com/bernieyangmh)| [@PythonYXY](https://github.com/PythonYXY)| [@zuijiawoniu](https://github.com/zuijiawoniu)| [@netAir](https://github.com/netAir)| [@scil](https://github.com/scil)| [@tangrela](https://github.com/tangrela)| [@highroom](https://github.com/highroom)| [@luocaodan](https://github.com/luocaodan)| [@vc5](https://github.com/vc5)| [@1again](https://github.com/1again)| [@obaiyan](https://github.com/obaiyan)


### Release Notes

   [release notes](https://github.com/jhao104/proxy_pool/blob/master/doc/release_notes.md)

