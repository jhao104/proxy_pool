
## 代理池介绍

本项目通过爬虫方式持续抓取代理网站公布的免费代理IP，实时校验，维护部分可以使用的代理，并通过api的形式提供外部使用。

### 1、问题

构建一个代理IP池，可能有下面这些问题：

* 代理IP从何而来？

　　许多刚接触爬虫的，都试过去西刺、快代理之类有免费代理的网站去抓些免费代理，还是有一些代理能用。
当然，如果你有更好的代理接口也可以自己接入。

　　免费代理的采集也很简单，无非就是：`访问页面`` —> `正则/xpath提取` —> `保存`

* 如何保证代理质量？

　　可以肯定免费的代理IP大部分都是不能用的，不然别人还提供付费接口干嘛(不过事实上很多代理商的付费IP也不稳定，也有很多是不能用)。
所以采集回来的代理IP不能直接使用，检测的办法也很简单：可以写个程序不断的用代理访问一个稳定的网站，看是否可以正常访问即可。
这个过程可以使用多线/进程或异步的方式，因为检测代理是个很慢的过程。

* 采集回来的代理如何存储？

　　这里不得不推荐一个国人开发的高性能支持多种数据结构的NoSQL数据库[SSDB](http://ssdb.io/docs/zh_cn/)，用于替代Redis。支持队列、hash、set、k-v对，支持T级别数据。是做分布式爬虫很好中间存储工具。

* 如何让爬虫更方便的用到这些代理？

　　答案肯定是做成服务咯，Python有这么多的web框架，随便拿一个来写个api供爬虫调用。这样代理和爬虫架构分离有很多好处，
比如：当爬虫完全不用考虑如何校验代理，如何保证拿到的代理可用，这些都由代理池来完成。这样只需要安静的码爬虫代码就行啦。

### 2、代理池设计

　　代理池由四部分组成:

* ProxyGetter:

　　代理获取接口，目前有5个免费代理源，每调用一次就会抓取这个5个网站的最新代理放入DB，支持自定义扩展额外的代理获取接口；

* DB:

　　用于存放代理IP，目前支持SSDB和Redis(推荐SSDB)。至于为什么选择SSDB，大家可以参考这篇[文章](https://www.sdk.cn/news/2684),个人觉得SSDB是个不错的Redis替代方案，如果你没有用过SSDB，安装起来也很简单，可以参考[这里](https://github.com/jhao104/memory-notes/blob/master/SSDB/SSDB%E5%AE%89%E8%A3%85%E9%85%8D%E7%BD%AE%E8%AE%B0%E5%BD%95.md)；

* Schedule:

　　计划任务，定时去检测DB中的代理可用性，删除不可用的代理。同时也会主动通过ProxyGetter去获取最新代理放入DB；

* ProxyApi:

　　代理池的外部接口，由[Flask](http://flask.pocoo.org/)实现，功能是给爬虫提供与代理池交互的接口。

<!--#### 功能图纸-->
![设计](https://pic2.zhimg.com/v2-f2756da2986aa8a8cab1f9562a115b55_b.png)

### 3、代码模块

　　Python中高层次的数据结构,动态类型和动态绑定,使得它非常适合于快速应用开发,也适合于作为胶水语言连接已有的软件部件。用Python来搞这个代理IP池也很简单，代码分为6个模块：

* Api:

　　api接口相关代码，目前api是由Flask实现，代码也非常简单。客户端请求传给Flask，Flask调用`ProxyManager`中的实现，包括`get/delete/refresh/get_all`；

* DB:

　　数据库相关代码，目前数据库是支持SSDB/Redis。代码用工厂模式实现，方便日后扩展其他类型数据库；

* Manager:

　　`get/delete/refresh/get_all`等接口的具体实现类，目前代理池只负责管理proxy，日后可能会有更多功能，比如代理和爬虫的绑定，代理和账号的绑定等等；

* ProxyGetter:

　　代理获取的相关代码，目前抓取了[快代理](http://www.kuaidaili.com)、[代理66](http://www.66ip.cn/)、[有代理](http://www.youdaili.net/Daili/http/)、[西刺代理](http://api.xicidaili.com/free2016.txt)、[guobanjia](http://www.goubanjia.com/free/gngn/index.shtml)这个五个网站的免费代理，经测试这个5个网站每天更新的可用代理只有六七十个，当然也支持自己扩展代理接口；

* Schedule:

　　定时任务相关代码，现在只是实现定时去刷新代理，并验证可用代理，采用多进程方式；

* Util:

　　存放一些公共的模块方法或函数，包含`GetConfig`:读取配置文件config.ini的类，`ConfigParse`: 扩展ConfigParser的类，使其对大小写敏感， `Singleton`:实现单例，`LazyProperty`:实现类属性惰性计算。等等；

* 其他文件:

　　配置文件:`Config.ini``,数据库配置和代理获取接口配置，可以在GetFreeProxy中添加新的代理获取方法，并在Config.ini中注册即可使用；

### 4、安装

下载代码:
```
git clone git@github.com:jhao104/proxy_pool.git

或者直接到https://github.com/jhao104/proxy_pool 下载zip文件
```

安装依赖:
```
pip install -r requirements.txt
```

启动:

```
如果你的依赖已经安全完成并且具备运行条件,可以直接在Run下运行main.py
到Run目录下:
>>>python main.py

如果运行成功你应该可以看到有4个main.py进程在


你也可以分别运行他们,依次到Api下启动ProxyApi.py,Schedule下启动ProxyRefreshSchedule.py和ProxyValidSchedule.py即可
```

docker:
```
git clone git@github.com:jhao104/proxy_pool.git

cd proxy_pool

docker build -t proxy:latest -f Dockerfile .

docker run -p 5000:5000 -d proxy:latest

# Wait a few minutes
curl localhost:5000/get/
# result: xxx.xxx.xxx.xxx:xxxx

curl localhost:5000/get_all/
```

### 5、使用
　　定时任务启动后，会通过GetFreeProxy中的方法抓取代理存入数据库并验证。此后默认每10分钟会重复执行一次。定时任务启动大概一两分钟后，便可在[SSDB](https://github.com/jhao104/SSDBAdmin)中看到刷新出来的可用的代理：

![useful_proxy](https://pic2.zhimg.com/v2-12f9b7eb72f60663212f317535a113d1_b.png)

　　启动ProxyApi.py后即可在浏览器中使用接口获取代理，一下是浏览器中的截图:

　　index页面:

![index](https://pic3.zhimg.com/v2-a867aa3db1d413fea8aeeb4c693f004a_b.png)

　　get：

![get](https://pic1.zhimg.com/v2-f54b876b428893235533de20f2edbfe0_b.png)

　　get_all：

![get_all](https://pic3.zhimg.com/v2-5c79f8c07e04f9ef655b9bea406d0306_b.png)


　　爬虫中使用，如果要在爬虫代码中使用的话， 可以将此api封装成函数直接使用，例如:
```
import requests

def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

# your spider code

def spider():
    # ....
    requests.get('https://www.example.com', proxies={"http": "http://{}".format(get_proxy())})
    # ....

```

　　测试地址：http://123.207.35.36:5010 单机勿压测。谢谢

### 6、最后
　　时间仓促，功能和代码都比较简陋，以后有时间再改进。喜欢的在github上给个star。感谢！
