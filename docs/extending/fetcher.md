# 扩展代理源

项目默认包含多个免费的代理获取源，但是免费的毕竟质量有限，如果直接运行可能拿到的代理质量不理想。因此提供了用户自定义扩展代理获取的方法。

## 添加新的代理源

### 第一步：创建代理源文件

在 `fetcher/sources/` 目录下新建一个 `.py` 文件，继承 `BaseFetcher` 基类，实现 `fetch()` 方法：

```python
# fetcher/sources/mySource.py

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class MySourceFetcher(BaseFetcher):
    """我的代理源 https://example.com/proxy"""

    name = "mysource"                   # 唯一标识，用于日志
    url = "https://example.com/proxy"   # 源网站首页
    enabled = True                      # 设为 False 可禁用

    def fetch(self):
        """yield "host:port" 格式的代理字符串"""
        r = WebRequest().get(self.url, timeout=10)
        for proxy in self.parseProxiesFromText(r.text):
            yield proxy


if __name__ == '__main__':
    for proxy in MySourceFetcher().fetch():
        print(proxy)
```

添加完成后，调度器下一轮采集（默认 4 分钟）会自动发现并启用新源，**无需修改任何配置文件**。

### 第二步：验证

独立调试代理源：

```bash
python -m fetcher.sources.mySource
```

查看当前启用的代理源：

```bash
python proxyPool.py show
```

## 禁用代理源

有两种方式禁用某个代理源：

**方式一：修改源文件**（推荐）

在对应文件中将 `enabled` 设为 `False`：

```python
class MySourceFetcher(BaseFetcher):
    enabled = False  # 禁用该源
```

**方式二：黑名单配置**

在 `setting.py` 的 `PROXY_FETCHER_EXCLUDE` 列表中添加类名，无需修改源文件：

```python
PROXY_FETCHER_EXCLUDE = ["MySourceFetcher"]
```

## BaseFetcher 基类

所有代理源必须继承 `BaseFetcher`，基类提供以下约定和工具：

### 必须声明的属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | str | 唯一标识，用于日志和代理来源标记 |
| `url` | str | 源网站首页 URL |

### 可选属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | `True` | 是否启用 |

### 必须实现的方法

| 方法 | 说明 |
|------|------|
| `fetch(self)` | 生成器，yield `"host:port"` 格式字符串 |

### 共享解析工具

| 方法 | 说明 |
|------|------|
| `parseProxiesFromText(text)` | 从纯文本中用正则提取 ip:port |
| `parseProxiesFromJson(data)` | 从 JSON 结构中递归提取 ip:port |
| `parseProxiesFromTree(tree)` | 从 lxml tree 的 table 行中提取 ip:port |
| `yieldUniqueProxies(proxies)` | 去重 yield |

## 运行时热更新

调度器每轮采集时会重新扫描 `fetcher/sources/` 目录并 reload 模块，因此：

- 新增文件 → 下一轮自动启用
- 修改文件内容 → 下一轮自动加载新版本
- 删除文件 → 下一轮自动移除（建议先从 `PROXY_FETCHER_EXCLUDE` 或 `enabled` 中禁用）

## 命名规范

| 元素 | 风格 | 示例 |
|------|------|------|
| 文件名 | 小写 | `mysource.py` |
| 类名 | PascalCase | `MySourceFetcher` |
| `name` 属性 | 小写 | `"mysource"` |