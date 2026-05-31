# 项目结构

ProxyPool 项目目录结构如下：

```
proxy_pool/
├── api/                    # API 服务
│   └── proxyApi.py         #   Flask RESTful 接口
├── db/                     # 数据库层
│   ├── dbClient.py         #   抽象数据库接口
│   ├── redisClient.py      #   Redis 实现
│   └── ssdbClient.py       #   SSDB 实现
├── fetcher/                # 代理采集器
│   ├── baseFetcher.py      #   BaseFetcher 基类（共享解析方法）
│   └── sources/            #   各代理源独立文件
│       ├── zdaye.py        #     站大爷
│       ├── ip66.py         #     代理66
│       ├── kxdaili.py      #     开心代理
│       ├── kuaidaili.py    #     快代理
│       ├── geonode.py      #     Geonode
│       └── ...             #     其他代理源
├── handler/                # 业务处理器
│   ├── configHandler.py    #   配置读取
│   ├── logHandler.py       #   日志处理
│   └── proxyHandler.py     #   代理 CRUD 逻辑
├── helper/                 # 核心辅助模块
│   ├── scheduler.py        #   APScheduler 定时调度
│   ├── validator.py        #   代理可用性校验
│   ├── proxy.py            #   代理数据模型
│   ├── fetch.py            #   采集任务执行
│   └── check.py            #   校验任务执行
├── util/                   # 工具库
│   ├── singleton.py        #   单例元类
│   ├── lazyProperty.py     #   惰性属性装饰器
│   ├── six.py              #   Python 2/3 兼容层
│   └── webRequest.py       #   HTTP 请求封装
├── tests/                  # 测试
│   ├── conftest.py         #   共享 fixtures
│   ├── unit/               #   单元测试（零外部依赖）
│   ├── api/                #   API 路由测试（Flask test client）
│   └── integration/        #   集成测试（RedisClient/SsdbClient CRUD）
├── docs/                   # MkDocs 文档源文件
├── proxyPool.py            # CLI 入口（click）
├── proxy_pool.sh           # 服务管理脚本
├── setting.py              # 全局配置文件
├── requirements.txt        # Python 依赖
├── requirements-test.txt   # 测试依赖（pytest、pytest-cov、fakeredis）
├── pyproject.toml          # pytest 配置
├── Dockerfile              # Docker 镜像构建
├── docker-compose.yml      # Docker Compose 编排
└── tox.ini                 # 多版本测试配置
```

## 核心模块说明

### `proxyPool.py` — 入口

基于 click 的命令行入口，提供 `schedule`、`server`、`fetcher` 三个子命令。`schedule` 启动代理采集和验证调度器，`server` 启动 Flask API 服务，`fetcher` 查看当前启用的代理源列表。

### `api/proxyApi.py` — API 服务

Flask 应用，提供 `/get`、`/pop`、`/all`、`/count`、`/delete` 等接口，运行在 `setting.py` 配置的 `HOST:PORT`（默认 `0.0.0.0:5010`）。

### `db/` — 数据库层

通过 `dbClient.py` 定义统一接口，`redisClient.py` 和 `ssdbClient.py` 分别实现 Redis 和 SSDB 的存取逻辑。使用 `setting.py` 中的 `DB_CONN` 连接字符串选择后端。

### `fetcher/` — 代理采集

采用插件架构。`baseFetcher.py` 定义 `BaseFetcher` 基类，提供共享解析方法和 `name`/`url`/`enabled` 属性约定。每个代理源在 `sources/` 目录下独立一个文件，继承 `BaseFetcher` 并实现 `fetch()` 方法。调度器自动扫描 `sources/` 目录，加载 `enabled=True` 的源。通过 `setting.py` 的 `PROXY_FETCHER_EXCLUDE` 黑名单可临时禁用指定源。

### `helper/scheduler.py` — 定时调度

基于 APScheduler，按配置间隔驱动采集器和验证器运行，自动维护代理池数量。

### `helper/validator.py` — 代理校验

使用 `HTTP_URL` 和 `HTTPS_URL` 测试代理可用性，超过 `MAX_FAIL_COUNT` 次失败的代理会被移除。

### `handler/` — 业务处理

- `configHandler.py`：封装 `setting.py` 配置项的读取
- `logHandler.py`：统一日志配置
- `proxyHandler.py`：代理的增删改查操作

### `setting.py` — 配置中心

所有运行时配置集中在此文件，包括 API 地址、数据库连接、采集器列表、校验参数等。详见 [配置参考](configuration.md)。
