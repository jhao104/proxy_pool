
爬虫代理IP池
=======
[![Build Status](https://travis-ci.org/jhao104/proxy_pool.svg?branch=master)](https://travis-ci.org/jhao104/proxy_pool)[![Yii2](https://img.shields.io/badge/Powered_by-Yii_Framework-green.svg?style=flat)](http://www.spiderpy.cn/)


> 在公司做分布式深网爬虫，搭建了一套稳定的代理池服务，为上千个爬虫提供有效的代理，保证各个爬虫拿到的都是对应网站有效的代理IP，从而保证爬虫快速稳定的运行，当然在公司做的东西不能开源出来。不过呢，闲暇时间手痒，所以就想利用一些免费的资源搞一个简单的代理池服务。
 

### 1、问题

* 代理IP从何而来？

　　刚自学爬虫的时候没有代理IP就去西刺、快代理之类有免费代理的网站去爬，还是有个别代理能用。当然，如果你有更好的代理接口也可以自己接入。
　　
　　免费代理的采集也很简单，无非就是：访问页面页面 —> 正则/xpath提取 —> 保存

* 如何保证代理质量？

　　可以肯定免费的代理IP大部分都是不能用的，不然别人为什么还提供付费的(不过事实是很多代理商的付费IP也不稳定，也有很多是不能用)。所以采集回来的代理IP不能直接使用，可以写检测程序不断的去用这些代理访问一个稳定的网站，看是否可以正常使用。这个过程可以使用多线程或异步的方式，因为检测代理是个很慢的过程。

* 采集回来的代理如何存储？

　　这里不得不推荐一个高性能支持多种数据结构的NoSQL数据库[SSDB](http://ssdb.io/docs/zh_cn/)，用于替代Redis。支持队列、hash、set、k-v对，支持T级别数据。是做分布式爬虫很好中间存储工具。

* 如何让爬虫更简单的使用这些代理？

　　答案肯定是做成服务咯，python有这么多的web框架，随便拿一个来写个api供爬虫调用。这样有很多好处，比如：当爬虫发现代理不能使用可以主动通过api去delete代理IP，当爬虫发现代理池IP不够用时可以主动去refresh代理池。这样比检测程序更加靠谱。

### 2、代理池设计

　　代理池由四部分组成:

* ProxyGetter:

　　代理获取接口，目前有5个免费代理源，每调用一次就会抓取这个5个网站的最新代理放入DB，可自行添加额外的代理获取接口；

* DB:

　　用于存放代理IP，现在暂时只支持SSDB。至于为什么选择SSDB，大家可以参考这篇[文章](https://www.sdk.cn/news/2684),个人觉得SSDB是个不错的Redis替代方案，如果你没有用过SSDB，安装起来也很简单，可以参考[这里](https://github.com/jhao104/memory-notes/blob/master/SSDB/SSDB%E5%AE%89%E8%A3%85%E9%85%8D%E7%BD%AE%E8%AE%B0%E5%BD%95.md)；

* Schedule:

　　计划任务用户定时去检测DB中的代理可用性，删除不可用的代理。同时也会主动通过ProxyGetter去获取最新代理放入DB；

* ProxyApi:

　　代理池的外部接口，由于现在这么代理池功能比较简单，花两个小时看了下[Flask](http://flask.pocoo.org/)，愉快的决定用Flask搞定。功能是给爬虫提供get/delete/refresh等接口，方便爬虫直接使用。
<!--#### 功能图纸-->
![设计](https://pic2.zhimg.com/v2-f2756da2986aa8a8cab1f9562a115b55_b.png)

### 3、代码模块

　　Python中高层次的数据结构,动态类型和动态绑定,使得它非常适合于快速应用开发,也适合于作为胶水语言连接已有的软件部件。用Python来搞这个代理IP池也很简单，代码分为6个模块：

* Api:

　　api接口相关代码，目前api是由Flask实现，代码也非常简单。客户端请求传给Flask，Flask调用ProxyManager中的实现，包括`get/delete/refresh/get_all`；

* DB:

　　数据库相关代码，目前数据库是采用SSDB。代码用工厂模式实现，方便日后扩展其他类型数据库；

* Manager:

　　`get/delete/refresh/get_all`等接口的具体实现类，目前代理池只负责管理proxy，日后可能会有更多功能，比如代理和爬虫的绑定，代理和账号的绑定等等；

* ProxyGetter:

　　代理获取的相关代码，目前抓取了[快代理](http://www.kuaidaili.com)、[代理66](http://www.66ip.cn/)、[有代理](http://www.youdaili.net/Daili/http/)、[西刺代理](http://api.xicidaili.com/free2016.txt)、[guobanjia](http://www.goubanjia.com/free/gngn/index.shtml)这个五个网站的免费代理，经测试这个5个网站每天更新的可用代理只有六七十个，当然也支持自己扩展代理接口；

* Schedule:

　　定时任务相关代码，现在只是实现定时去刷新代码，并验证可用代理，采用多进程方式；

* Util:

　　存放一些公共的模块方法或函数，包含`GetConfig`:读取配置文件config.ini的类，`ConfigParse`: 集成重写ConfigParser的类，使其对大小写敏感， `Singleton`:实现单例，`LazyProperty`:实现类属性惰性计算。等等；

* 其他文件:

　　配置文件:Config.ini,数据库配置和代理获取接口配置，可以在GetFreeProxy中添加新的代理获取方法，并在Config.ini中注册即可使用；

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

### 5、使用
　　定时任务启动后，会通过代理获取方法fetch所有代理放入数据库并验证。此后默认每20分钟会重复执行一次。定时任务启动大概一两分钟后，便可在[SSDB](https://github.com/jhao104/SSDBAdmin)中看到刷新出来的可用的代理：
    
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
    return requests.get("http://127.0.0.1:5000/get/").content

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5000/delete/?proxy={}".format(proxy))

# your spider code

def spider():
    # ....
    requests.get('https://www.example.com', proxies={"http": "http://{}".format(get_proxy())})
    # ....

```

　　测试地址：http://123.207.35.36:5000 单机勿压测。谢谢

### 6、最后
　　时间仓促，功能和代码都比较简陋，以后有时间再改进。喜欢的在github上给个star。感谢！
