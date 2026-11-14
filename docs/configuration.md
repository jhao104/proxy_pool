# 配置参考

配置文件 `setting.py` 位于项目的主目录下，配置主要分为五类：**服务配置**、**数据库配置**、**采集配置**、**校验配置**、**调度配置**。

## 服务配置

### `HOST`

API 服务监听的 IP。本机访问设置为 `127.0.0.1`，开启远程访问设置为 `0.0.0.0`。

- 默认值：`"0.0.0.0"`

### `PORT`

API 服务监听的端口。

- 默认值：`5010`

## 数据库配置

### `DB_CONN`

存放代理 IP 的数据库 URI，配置格式为：

```
db_type://[[user]:[pwd]]@ip:port/[db]
```

目前支持的 `db_type`：`redis`、`ssdb`。

配置示例：

```python
# Redis
DB_CONN = 'redis://@127.0.0.1:6379'
DB_CONN = 'redis://:123456@127.0.0.1:6379'
DB_CONN = 'redis://:123456@127.0.0.1:6379/15'

# SSDB
DB_CONN = 'ssdb://@127.0.0.1:8888'
DB_CONN = 'ssdb://:123456@127.0.0.1:8888'
```

### `TABLE_NAME`

存放代理的数据载体名称。SSDB 和 Redis 的存放结构为 hash。

- 默认值：`"use_proxy"`

## 采集配置

代理采集采用插件架构，调度器自动扫描 `fetcher/sources/` 目录，加载所有 `enabled=True` 的代理源。新增代理源只需在 `sources/` 下创建文件，无需修改配置。

查看当前启用的代理源：

```bash
python proxyPool.py fetcher
```

### `PROXY_FETCHER_EXCLUDE`

代理源黑名单。列表中的类名对应的代理源不会被加载，即使 `enabled=True`。适用于临时禁用某个代理源而不修改其源文件。

```python
PROXY_FETCHER_EXCLUDE = [
    # "BinglxFetcher",   # 临时禁用冰凌代理
]
```

如需永久禁用，建议直接在源文件中设置 `enabled = False`。

### 抓取频率

调度器固定每 5 分钟执行一轮采集（代码内硬编码），池内代理数低于 `POOL_SIZE_MIN` 时还会由 2 分钟一次的检查任务触发补采。

个别源有严格限流或更新较慢，可在源类上声明 `interval`（秒）限制最短抓取间隔，未到期的源在采集时被跳过。例如站大爷开放接口 `zdopen.py` 因接口限流（每 10 秒最多 2 次）设为每 2 小时一轮：

```python
class ZdopenFetcher(BaseFetcher):
    interval = 2 * 60 * 60
```

`interval = 0`（默认）表示每轮都抓取。

## 校验配置

### `HTTP_URL`

用于检验代理是否可用的地址。

- 默认值：`"http://httpbin.org"`

### `HTTPS_URL`

用于检验代理是否支持 HTTPS 的地址。

- 默认值：`"https://www.qq.com"`

### `CHECK_URL`

伪造代理检测的请求地址。部分假代理对任何请求都返回 200，仅靠状态码无法识别。校验时通过代理 GET 该地址（不跟随重定向），若响应内容不包含 `CHECK_KEYWORD`，则判定为假代理。

- 默认值：`"http://baidu.com"`

### `CHECK_KEYWORD`

伪造代理检测的特征字符串，即 `http://baidu.com` 正常返回的 301 页面 body 中的锚点。劫持型假代理返回的是自己的 200 页面，不包含该特征。

- 默认值：`'<a href="https://www.baidu.com/">Moved Permanently</a>'`

### `VERIFY_TIMEOUT`

检验代理的超时时间，单位秒。使用代理访问 `HTTP_URL` / `HTTPS_URL` 耗时超过 `VERIFY_TIMEOUT` 时，视为代理不可用。

- 默认值：`10`

### `MAX_FAIL_COUNT`

检验代理允许的最大失败次数。超过则剔除代理。

- 默认值：`0`（即失败一次即删除）

### `POOL_SIZE_MIN`

代理检测定时任务运行前，若代理数量小于 `POOL_SIZE_MIN`，则先运行抓取程序。

- 默认值：`20`

## 代理属性

### `PROXY_REGION`

是否启用代理地域属性。开启后会尝试解析代理 IP 的地理位置信息。

- 默认值：`True`

## 调度配置

### `TIMEZONE`

调度器的时区设置。如果在虚拟机上运行时出现 `ValueError: Timezone offset does not match system offset` 错误，请设置该配置项。

- 默认值：`"Asia/Shanghai"`