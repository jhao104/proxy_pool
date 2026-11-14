# API 使用

## 接口列表

启动 ProxyPool 的 `server` 后会提供如下 HTTP 接口：

| 接口 | 方法 | 说明 | 参数 |
|------|------|------|------|
| `/` | GET | 返回 API 列表 | 无 |
| `/get` | GET | 随机返回一个代理 | 可选：`?type=https` 过滤 HTTPS 代理 |
| `/pop` | GET | 返回并删除一个代理 | 可选：`?type=https` 过滤 HTTPS 代理 |
| `/all` | GET | 返回所有代理 | 可选：`?type=https` 过滤 HTTPS 代理 |
| `/count` | GET | 返回代理数量统计 | 无 |
| `/count/source` | GET | 按来源(采集 fetcher)统计：池内数量、抓取数、可用数、存活率、上次抓取时间 | 无 |
| `/count/speed` | GET | 校验速度：最近 1/5/10 分钟内校验的 ip 数量与速度 | 无 |
| `/delete` | GET | 删除指定代理 | `?proxy=host:port` |

## 调用示例

### 在爬虫中使用

通过调用 API 接口来使用代理池：

```python
import requests


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


def get_html():
    retry_count = 5
    proxy = get_proxy().get("proxy")
    while retry_count > 0:
        try:
            # 使用代理访问
            html = requests.get(
                "http://www.example.com",
                proxies={
                    "http": "http://{}".format(proxy),
                    "https": "https://{}".format(proxy),
                },
            )
            return html
        except Exception:
            retry_count -= 1
            # 删除代理池中代理
            delete_proxy(proxy)
    return None
```

本例中在本地 `127.0.0.1` 启动端口为 `5010` 的 `server`，使用 `/get` 接口获取代理，`/delete` 删除代理。

### 获取 HTTPS 代理

```python
# 只获取支持 HTTPS 的代理
proxy = requests.get("http://127.0.0.1:5010/get/?type=https").json()
```

### 获取代理统计

```python
# 返回代理数量、类型分布、来源分布
stats = requests.get("http://127.0.0.1:5010/count/").json()
# 示例返回: {"http_type": {"http": 10, "https": 5}, "source": {"freeProxy01": 8, "freeProxy02": 7}, "count": 15}

# 只看各采集来源的贡献与质量
source_stats = requests.get("http://127.0.0.1:5010/count/source/").json()
# 示例返回:
# {
#   "source": {
#     "ip89":      {"pool_count": 12, "fetched": 60, "valid": 12, "survival_rate": 0.2, "last_fetch_time": "2026-11-14 10:00:00"},
#     "kuaidaili": {"pool_count": 3,  "fetched": 20, "valid": 4,  "survival_rate": 0.2, "last_fetch_time": "2026-11-14 10:05:00"}
#   },
#   "count": 15
# }
```

各字段含义：

| 字段 | 说明 |
|------|------|
| `pool_count` | 当前池中由该来源贡献的可用代理数；多来源代理在各来源下分别计数，因此各来源之和可能大于 `count` |
| `fetched` | 最近一轮采集从该来源抓到的数量（同一轮内按代理去重） |
| `valid` | 最近一轮采集后验证通过的数量（`valid <= fetched`） |
| `survival_rate` | 存活率 `valid / fetched`，保留 4 位小数；`fetched` 为 0 时为 `0.0` |
| `last_fetch_time` | 最近一次抓取时间，格式 `YYYY-MM-DD HH:MM:SS` |

说明：

- 采集统计由 `schedule` 进程在**每轮采集结束后**写入数据库（独立 hash `<TABLE_NAME>:source_stat`），因此 `server` 重启后仍可读取。
- 统计**按轮重置**，只反映最近一轮，不是累计值。
- 对于上一轮因 `interval` 未到期而被跳过的源，其 `last_fetch_time` 保持为上次实际抓取时间。
- 池中存在但从未有过统计记录的来源（如旧数据、已删除的源），仍会返回，抓取相关字段为 0 / 空串。

### 校验速度统计

```python
# 最近 1/5/10 分钟内校验了多少个 ip、平均每秒多少个
speed = requests.get("http://127.0.0.1:5010/count/speed/").json()
# 示例返回:
# {
#   "speed": {
#     "1min":  {"count": 120, "speed": 2.0},
#     "5min":  {"count": 480, "speed": 1.6},
#     "10min": {"count": 900, "speed": 1.5}
#   }
# }
```

| 字段 | 说明 |
|------|------|
| `count` | 对应窗口内完成的校验次数（每个 ip 校验完一次计一次，不区分通过与否） |
| `speed` | `count / 窗口秒数`，单位「个/秒」，保留 4 位小数 |

说明：

- 校验包含 `raw`（新采集验证）和 `use`（池内复检）两类，窗口按查询时刻滑动计算。
- `schedule` 进程只在**每轮校验结束后**把时间戳列表写入数据库（hash `<TABLE_NAME>:speed_stat` 的 `events` 字段），因此 API 展示的时间精度取决于采集/校验任务的执行频率，不是每秒实时刷新。
- 只保留最近 10 分钟的时间戳，写入时已过期的不再保存，避免无限增长。

## 直接读取数据库

除了通过 API 接口，也可以直接读取数据库获取代理。目前支持两种数据库：Redis 和 SSDB。

- **Redis**：存储结构为 hash，hash name 为配置项中的 `TABLE_NAME`（默认 `use_proxy`）
- **SSDB**：存储结构为 hash，hash name 为配置项中的 `TABLE_NAME`

可以在代码中自行读取数据库获取代理列表。