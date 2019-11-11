# proxy-pool


## helm chart安装方式:
```shell
helm install proxy-pool ./proxy-pool
```
> 如果要配合其他可用参数,可以自行设置,参数列表见文末,例如:
> 
> `helm install proxy-pool ./proxy-pool --set proxyPoolConfig.dbHost=192.168.1.100 --set proxyPoolConfig.dbPassword=calmkart`

运行后将看到输出并创建k8s api对象(deployment&&service):
```shell
➜  helm ✗ helm install proxy-pool ./proxy-pool
NAME: proxy-pool
LAST DEPLOYED: 2019-11-11 16:43:55.381296 +0800 CST m=+0.398530920
NAMESPACE: default
STATUS: deployed

NOTES:
1. Get the application URL by running these commands:
  export POD_NAME=$(kubectl get pods -l "app=proxy-pool,release=proxy-pool" -o jsonpath="{.items[0].metadata.name}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl port-forward $POD_NAME 8080:80
```

我们可以通过port-forward或者ingress访问服务

>`kubectl port-forward svc/proxy-pool 8080:80`
- 访问地址 `http://0.0.0.0:8080/`

>如果我们打开ingress功能,则将proxy-pool.calmkart.com的域名解析切换到ingress地址即可访问(修改hosts或dns皆可)
- 访问地址: `http://proxy-pool.calmkart.com/`

### 3. 其他备注

#### 可用参数
| Parameter | Description | Default |
| ----- | ----------- | ------ |
| `pullPolicy` | docker镜像拉取策略(因为tag使用的是latest,所以推荐使用默认的Always,调试或特殊情况可修改) |`Always`| 
| `proxyPoolConfig.dbType` | proxy-pool使用的数据库类型 |`"REDIS"`|
| `proxyPoolConfig.dbHost` | proxy-pool使用的数据库ip |`"127.0.0.1"`|
| `proxyPoolConfig.dbPort` | proxy-pool使用的数据库端口 |`6379`|
| `proxyPoolConfig.dbPassword` | proxy-pool使用的数据库密码 |`""`|
| `proxyPoolConfig.servePort` | proxy-pool提供服务的端口 |`5010`|
| `ingress.enable` | 是否打开ingress |`false`|
| `ingress.hosts` | ingress域名 | `['proxy-pool.calmkart.com']` | 
