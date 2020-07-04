## Release Notes

* 2.1.0 (202007)

    1. 新增免费代理源 `西拉代理`  （2020-03-30）
    2. Fix Bug [#401](https://github.com/jhao104/proxy_pool/issues/401) [#356](https://github.com/jhao104/proxy_pool/issues/356)
    3. 优化Docker镜像体积; (2020-06-19)
    4. 优化配置方式;
    5. 优化代码结构;
    6. 不再储存raw_proxy, 抓取后直接验证入库;

* 2.0.1 (2020)

    1. 新增免费代理源 `89免费代理`;
    2. 新增免费代理源 `齐云代理` 
    
* 2.0.0 (201908)

    1. WebApi集成Gunicorn方式启动, Windows平台暂不支持;
    2. 优化Proxy调度程序;
    3. 扩展Proxy属性;
    4. 提供cli工具, 更加方便启动proxyPool
    
* 1.14 (2019.07)

    1. 修复`ProxyValidSchedule`假死bug,原因是Queue阻塞;
    2. 修改代理源 `云代理` 抓取;
    3. 修改代理源 `码农代理` 抓取;
    4. 修改代理源 `代理66` 抓取, 引入 `PyExecJS` 模块破解加速乐动态Cookies加密;
    
* 1.13 (2019.02)

  1.使用.py文件替换.ini作为配置文件；
  
  2.更新代理采集部分；
  
* 1.12 (2018.4)

  1.优化代理格式检查;

  2.增加代理源;

  3.fix bug [#122](https://github.com/jhao104/proxy_pool/issues/122) [#126](https://github.com/jhao104/proxy_pool/issues/126)

* 1.11 (2017.8)

　　1.使用多线程验证useful_pool;

* 1.10 (2016.11)

　　1. 第一版；

　　2. 支持PY2/PY3;

　　3. 代理池基本功能；