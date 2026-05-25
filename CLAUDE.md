# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。

## 技术栈
Python (3.8–3.12)、Flask (API)、Redis/SSDB (存储)、APScheduler (调度)、click (CLI)、gunicorn (生产服务器)。依赖版本固定记录在 `requirements.txt` 中。

## 常用命令
- 安装依赖：`pip install -r requirements.txt`
- 运行代理爬取/验证调度器：`python proxyPool.py schedule`
- 运行 API 服务器：`python proxyPool.py server`
- 运行全部测试：`pytest`
- 运行单个测试：`pytest test/testProxyFetcher.py::test_freeProxy01`
- Docker 部署：`docker-compose up -d` 或 `docker run --env DB_CONN=redis://:password@ip:port/0 -p 5010:5010 jhao104/proxy_pool:latest`

## 高层架构
免费代理池项目，爬取公开代理源、验证代理可用性、持久化存储到 Redis/SSDB，并通过 Flask RESTful API 提供代理服务。

### 核心组件
- **爬取器** (`fetcher/proxyFetcher.py`)：`ProxyFetcher` 类，每个代理源对应一个静态方法，yield 出 `host:port` 字符串。通过 `setting.py` 中的 `PROXY_FETCHER` 列表启用对应爬取器。
- **数据库层** (`db/`)：抽象 `dbClient` 接口，包含 Redis (`redisClient.py`) 和 SSDB (`ssdbClient.py`) 两种实现。通过 `setting.py` 中的 `DB_CONN` 配置连接（格式：`redis://:pwd@ip:port/db` 或 `ssdb://:pwd@ip:port`）。
- **调度器** (`helper/scheduler.py`)：基于 APScheduler 的定时任务，驱动爬取器运行并触发验证。时区通过 `setting.py` 中的 `TIMEZONE` 配置。
- **验证器** (`helper/validator.py`)：使用 `HTTP_URL` (http://httpbin.org) 和 `HTTPS_URL` (https://www.qq.com) 测试代理，超时时间由 `VERIFY_TIMEOUT` 指定（默认 10 秒）。超过 `MAX_FAIL_COUNT` 的代理会被移除。当代理池数量低于 `POOL_SIZE_MIN`（默认 20）时触发重新爬取。
- **API** (`api/proxyApi.py`)：Flask 接口，包含以下端点：
  - `/get`：随机获取一个代理（`?type=https` 可筛选 HTTPS 代理）
  - `/pop`：获取并删除一个代理
  - `/all`：列出所有代理
  - `/count`：代理数量统计
  - `/delete`：通过 `?proxy=host:port` 删除指定代理
  - 服务运行在 `HOST:PORT`（默认 `0.0.0.0:5010`），配置来自 `setting.py`。
- **命令行入口** (`proxyPool.py`)：基于 click 的命令行工具，包含 `schedule` 和 `server` 两个子命令。

### 扩展代理源
1. 在 `fetcher/proxyFetcher.py` 的 `ProxyFetcher` 类中新增一个静态方法，yield 出 `host:port` 字符串。
2. 将该方名添加到 `setting.py` 的 `PROXY_FETCHER` 列表中。调度器会自动识别并启用新的代理源。

## 关键配置
所有运行时配置均在 `setting.py` 中：
- `HOST`/`PORT`：API 绑定的地址和端口
- `DB_CONN`：数据库连接字符串
- `PROXY_FETCHER`：已启用的爬取器方法名列表
- `HTTP_URL`/`HTTPS_URL`：验证目标 URL
- `VERIFY_TIMEOUT`：验证超时时间（默认 10 秒）
- `MAX_FAIL_COUNT`：代理被移除前允许的最大失败次数
- `POOL_SIZE_MIN`：触发重新爬取的最小代理池数量阈值
- `PROXY_REGION`：是否启用代理地区属性（默认 `True`）
- `TIMEZONE`：调度器时区（默认 `Asia/Shanghai`）

## 代码风格与命名规范
- **缩进**：4 个空格（Python 标准）
- **文件命名**：驼峰命名，如 `proxyFetcher.py`、`dbClient.py`、`redisClient.py`、`webRequest.py`
- **类命名**：帕斯卡命名，如 `ProxyFetcher`、`RedisClient`、`SsdbClient`、`ProxyValidator`
- **方法命名**：混合风格——数据库/爬取器方法使用驼峰命名（`getAll`、`getCount`、`changeTable`、`freeProxy01`），属性和辅助方法使用下划线命名（`user_agent`、`fail_count`、`check_count`）
- **爬取器方法**：命名为 `freeProxy` + 两位数字（如 `freeProxy01`、`freeProxy02`）。新增爬取器必须遵循此模式
- **常量**（在 `setting.py` 中）：大写下划线命名（`DB_CONN`、`PROXY_FETCHER`、`HTTP_URL`、`MAX_FAIL_COUNT`）
- **变量**：下划线命名（`proxy_obj`、`proxy_str`、`https`）
- **注释/文档字符串**：源文件头部和行内注释通常使用中文（普通话）
- **单例模式**：使用自定义 `Singleton` 元类（`util/singleton.py`）结合 `six.withMetaclass` 实现

## 注意事项
- 免费代理稳定性较差，本项目仅供学习/演示使用。生产环境建议使用付费代理（如 Bright Data，详见 README）。
- 本仓库中不存在 `.cursorrules` 或 GitHub Copilot 配置文件。