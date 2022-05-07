

# Proxy_Pool 代理池项目快速搭建

## 环境准备

* Linux x64
* docker or 本地
* git 工具
* python3



## 项目搭建

### Linux 配置

1.  防火墙关闭

```bash
systemctl stop firewalld // 关闭防火墙
systemctl disable firewalld // 禁用防火墙
```

2. 安装python3

```
sudo yum install python3 python3-pip
```

3. 关闭selinux

```
sudo vim /etc/selinux/config
# 修改SELINUX的值为disabled后重启系统
SELINUX=disabled
```




### docker 安装

1.  一键自动化安装:

```bash
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
```

2. 启动docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

3. docker切换镜像源

```bash
   sudo mkdir -p /etc/docker
   sudo tee /etc/docker/daemon.json <<-'EOF'
   {
     "registry-mirrors": ["https://yytcclg8.mirror.aliyuncs.com"]
   }
   EOF
   sudo systemctl daemon-reload
   sudo systemctl restart docker
```

   

### Redis 安装

1.  利用docker安装redis 

```dockerfile
sudo docker pull redis
```

2.  启动redis
```bash
sudo docker run -d --name redis -p 6379:6379 redis --requirepass "password"
-p 端口
-requirepass "密码"
```



### Proxy_Pool 安装

1.  项目下载

```git
git clone https://github.com/jhao104/proxy_pool.git
```

2. 安装项目依赖

```
python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```



2.  配置修改

```bash
sudo vim setting.py

# 修改配置信息
DB_CONN = 'redis://:pwd@127.0.0.1:6379/0' #修改对应的配置信息
```


```bash
sudo vim star.sh

python3 proxyPool.py server &
python3 proxyPool.py schedule    # 修改对应python3 执行名称
```

3. 运行程序

```bash
yum install screen #安装后台运行程序
screen -S proxy_pool #创建一个名为proxy_pool的终端
./start.sh # 启动程序
ctrl+a+d #返回主终端，proxy_pool终端进入后台运行
```

4. 运行成果
![](https://s2.loli.net/2022/04/06/KTuQ2yHS7zPj8mW.png)

![image-20220406110323384](https://s2.loli.net/2022/04/06/js5Og48puJzQ6Tt.png)