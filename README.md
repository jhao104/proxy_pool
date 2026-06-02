
ProxyPool 爬虫代理IP池
=======
[![Tests](https://github.com/jhao104/proxy_pool/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/jhao104/proxy_pool/actions/workflows/test.yml)
[![](https://img.shields.io/badge/Powered%20by-@j_hao104-green.svg)](http://www.spiderpy.cn/blog/)
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

* 文档: [document](https://jhao104.github.io/proxy_pool/)

* 支持版本: 
[![](https://img.shields.io/badge/Python-3.8-blue.svg)](https://docs.python.org/3.8/)
[![](https://img.shields.io/badge/Python-3.9-blue.svg)](https://docs.python.org/3.9/)
[![](https://img.shields.io/badge/Python-3.10-blue.svg)](https://docs.python.org/3.10/)
[![](https://img.shields.io/badge/Python-3.11-blue.svg)](https://docs.python.org/3.11/)

* 测试地址: http://demo.spiderpy.cn (勿压谢谢)

* 付费代理推荐: [亮数据 Bright Data](https://get.brightdata.com/github_jh)（前身 Luminati）.全球代理与网络抓取行业头部领导者。覆盖 195+ 国家的 1.5亿+ 真人住宅IP，亲测成功率极高，轻松突破反爬封锁。需要高质量代理IP的可以注册后联系中文客服。[申请免费试用](https://get.brightdata.com/github_jh) (PS:用不明白的同学可以参考这个[使用教程](https://www.cnblogs.com/jhao/p/15611785.html))。

&emsp;&emsp; 想自建爬虫？接入 [Bright Data MCP Server](https://get.brightdata.com/cd3yy5)，让 Claude、Cursor、Windsurf 等 AI 助手直接实时抓取网页——自动破解验证码、绕过地区限制。[Scraper Studio](https://get.brightdata.com/cd3yy5) 支持 AI 一键生成或 JS 代码定制，全托管基础设施运行，无需自购代理、无需搭服务器，分钟级上线。所有产品底层均由同一套顶级代理网络驱动。

&emsp;&emsp; API 产品现享7折 + 免费试用额度，注册后可联系中文客服快速上手。(用不明白的同学可参考使用教程，或注册后直接使用互动 AI 智能助手)
👉 [https://get.brightdata.com/cd3yy5](https://get.brightdata.com/cd3yy5)


### 运行项目

##### 下载代码:

* git clone

```bash
git clone https://github.com/jhao104/proxy_pool.git
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


# 配置代理源（可选）
# 默认自动扫描 fetcher/sources/ 目录下所有 enabled=True 的代理源
# 如需禁用某些代理源，在黑名单中添加其 name 即可
# PROXY_FETCHER_EXCLUDE = ["freevpnnode"]
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

* 1、在 `fetcher/sources/` 目录下新建 `.py` 文件，继承 `BaseFetcher` 基类，声明 `name`/`url`/`enabled` 属性，实现 `fetch()` 方法以生成器(yield)形式返回`host:port`格式的代理，例如:

```python
from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest

class MyProxyFetcher(BaseFetcher):
    """我的代理源"""

    name = "myproxy"
    url = "https://www.example.com/"
    enabled = True

    def fetch(self):
        r = WebRequest().get("https://www.example.com/api/proxies")
        for item in r.json:
            yield item["ip"] + ":" + item["port"]
```

* 2、添加好后，`schedule` 进程下次抓取时会自动扫描 `fetcher/sources/` 目录并启用新代理源，无需修改配置。

　　可用 `python proxyPool.py fetcher` 命令查看当前启用的代理源列表。

　　如需临时禁用某个代理源，在 [setting.py](setting.py) 的 `PROXY_FETCHER_EXCLUDE` 黑名单中添加其 `name` 即可。

### 免费代理源

   目前实现的采集免费代理网站有(排名不分先后, 下面仅是对其发布的免费代理情况, 付费代理测评可以参考[这里](https://zhuanlan.zhihu.com/p/33576641)):
   
  | 代理名称          |  状态  |  更新速度 |  可用率  |  地址 | 代码                                             |
  |---------------|  ---- | --------  | ------  | ----- |------------------------------------------------|
  | 66代理          |  ✔    |     ★     |   *     | [地址](http://www.66ip.cn/)         | [`ip66.py`](/fetcher/sources/ip66.py)  |
  | 开心代理          |   ✔   |     ★     |   *     | [地址](http://www.kxdaili.com/)     | [`kxdaili.py`](/fetcher/sources/kxdaili.py)  |

  | 快代理           |  ✔    |     ★     |   *     | [地址](https://www.kuaidaili.com/)  | [`kuaidaili.py`](/fetcher/sources/kuaidaili.py)  |
  | 云代理           |  ✔    |    ★     |   *     | [地址](http://www.ip3366.net/)      | [`ip3366.py`](/fetcher/sources/ip3366.py) |
  | 小幻代理          |  ✔    |    ★★    |    *    | [地址](https://ip.ihuan.me/)        | [`ihuan.py`](/fetcher/sources/ihuan.py) |
  | 免费代理库         |  ✔    |     ☆     |    *    | [地址](http://ip.jiangxianli.com/)   | [`jiangxianli.py`](/fetcher/sources/jiangxianli.py) |
  | 89代理          |  ✔    |     ☆     |   *     | [地址](https://www.89ip.cn/)         | [`ip89.py`](/fetcher/sources/ip89.py) |
  | 稻壳代理          |  ✔    |     ★★    |   ***   | [地址](https://www.docip.ne)         | [`docip.py`](/fetcher/sources/docip.py) |
  | 谷德代理          |  ✔    |     ★★    |   ***   | [地址](https://www.goodips.com)         | [`goodips.py`](/fetcher/sources/goodips.py) |
  | Proxifly      |  ✔    |     ★★    |   **    | [地址](https://proxifly.dev)         | [`proxifly.py`](/fetcher/sources/proxifly.py) |

  
  如果还有其他好的免费代理网站, 可以在提交在[issues](https://github.com/jhao104/proxy_pool/issues/71), 下次更新时会考虑在项目中支持。

### 问题反馈

　　任何问题欢迎在[Issues](https://github.com/jhao104/proxy_pool/issues) 中反馈，同时也可以到我的[博客](http://www.spiderpy.cn/blog/message)中留言。

　　你的反馈会让此项目变得更加完美。

### 贡献代码

　　本项目仅作为基本的通用的代理池架构，不接收特有功能(当然,不限于特别好的idea)。

　　本项目依然不够完善，如果发现bug或有新的功能添加，请在[Issues](https://github.com/jhao104/proxy_pool/issues)中提交bug(或新功能)描述，我会尽力改进，使她更加完美。

　　这里感谢以下contributor的无私奉献：

　　[@kangnwh](https://github.com/kangnwh) | [@bobobo80](https://github.com/bobobo80) | [@halleywj](https://github.com/halleywj) | [@newlyedward](https://github.com/newlyedward) | [@wang-ye](https://github.com/wang-ye) | [@gladmo](https://github.com/gladmo) | [@bernieyangmh](https://github.com/bernieyangmh) | [@PythonYXY](https://github.com/PythonYXY) | [@zuijiawoniu](https://github.com/zuijiawoniu) | [@netAir](https://github.com/netAir) | [@scil](https://github.com/scil) | [@tangrela](https://github.com/tangrela) | [@highroom](https://github.com/highroom) | [@luocaodan](https://github.com/luocaodan) | [@vc5](https://github.com/vc5) | [@1again](https://github.com/1again) | [@obaiyan](https://github.com/obaiyan) | [@zsbh](https://github.com/zsbh) | [@jiannanya](https://github.com/jiannanya) | [@Jerry12228](https://github.com/Jerry12228) | [@zeyudada](https://github.com/zeyudada)


### Release Notes

   [changelog](https://jhao104.github.io/proxy_pool/changelog/)

<a href="https://hellogithub.com/repository/92a066e658d147cc8bd8397a1cb88183" target="_blank"><img src="https://api.hellogithub.com/v1/widgets/recommend.svg?rid=92a066e658d147cc8bd8397a1cb88183&claim_uid=DR60NequsjP54Lc" alt="Featured｜HelloGitHub" style="width: 250px; height: 54px;" width="250" height="54" /></a>
