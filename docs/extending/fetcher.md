# 扩展代理源

项目默认包含多个免费的代理获取源，但是免费的毕竟质量有限，如果直接运行可能拿到的代理质量不理想。因此提供了用户自定义扩展代理获取的方法。

## 添加新的代理源

### 第一步：编写获取方法

在 `ProxyFetcher` 类中添加自定义的获取代理的静态方法，该方法需要以生成器（yield）形式返回 `host:port` 格式的代理字符串：

```python
# fetcher/proxyFetcher.py

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
        # 确保每个 proxy 都是 host:port 正确的格式返回
```

### 第二步：注册到配置

修改配置文件 `setting.py` 中的 `PROXY_FETCHER` 项，加入刚才添加的自定义方法的名字：

```python
PROXY_FETCHER = [
    # ....
    "freeProxyCustom01"  # 确保名字和你添加的方法名字一致
]
```

调度程序每次执行采集任务时都会重新加载该配置，添加后会自动启用新的代理源。

## 命名规范

代理获取方法建议命名为 `freeProxy` + 两位数字（如 `freeProxy01`），自定义方法可使用 `freeProxyCustom` + 数字。