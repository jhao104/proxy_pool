# AGENTS.md

本文件为 ZCode 代理在本仓库中工作时提供指导。

## 项目概述

免费代理池：爬取公开代理源 → 验证可用性 → 存入 Redis/SSDB → 通过 Flask REST API 提供代理。
技术栈：Python 3.8–3.11、Flask、Redis/SSDB、APScheduler、click。根目录 `CLAUDE.md` 有更详细的同类说明。

## 目录结构

- `proxyPool.py` — click CLI 入口（`schedule` / `server` / `fetcher` 三个子命令）
- `setting.py` — 全部运行时配置（`VERSION` 也在这里）
- `fetcher/` — 爬取器插件架构；`baseFetcher.py` 定义基类，`sources/` 下每个代理源一个文件
- `db/` — `dbClient.py` 抽象接口 + `redisClient.py` / `ssdbClient.py` 实现
- `handler/` — `configHandler.py`（配置+环境变量覆盖）、`proxyHandler.py`（业务 CRUD）、`logHandler.py`
- `helper/` — `proxy.py`（Proxy 模型，JSON 序列化）、`validator.py`（验证）、`scheduler.py`（APScheduler 调度）、`fetch.py`（fetcher 发现/加载）、`launcher.py`（启动器）、`check.py`
- `api/` — `proxyApi.py` Flask 接口（`/get` `/pop` `/all` `/count` `/count/source` `/count/speed` `/delete`）
- `util/` — `singleton.py`（单例元类）、`lazyProperty.py`、`six.py`（内置的 six 副本，勿用 pip six 替代）、`webRequest.py`
- `docs/` — mkdocs 文档；`tests/` — unit / api / integration 三层

## 常用命令

```bash
pip install -r requirements.txt -r requirements-test.txt

python proxyPool.py schedule    # 启动爬取+验证调度器
python proxyPool.py server      # 启动 API（默认 0.0.0.0:5010）
python proxyPool.py fetcher     # 查看当前启用的代理源

pytest tests/unit/                          # 纯逻辑测试，无外部依赖，最常用
pytest tests/api/                           # Flask test client，mock 掉 DB
pytest tests/integration/ -m integration    # 需要真实 Redis
pytest --cov=. --cov-report=term-missing    # 覆盖率
```

所有命令都在仓库根目录执行（模块顶层互相 import，`sys.path` 依赖根目录）。没有配置 linter/formatter；CI（`.github/workflows/test.yml`）只在 py3.8–3.11 矩阵上跑 `pytest`。`tox.ini` 覆盖相同版本范围。

## 架构分层规则

调用链：API (`api/proxyApi.py`) → `ProxyHandler` → `DbClient`（按 `DB_CONN` URI 前缀自动选 Redis/SSDB 实现）。
调度链：`Scheduler` → `fetch.py` 发现 fetcher → `Validator` 验证 → 池中数量低于 `POOL_SIZE_MIN` 触发补采。

- **新增代理源**：在 `fetcher/sources/` 新建文件，继承 `BaseFetcher`，声明 `name`/`url`/`enabled` 属性，实现 `fetch()` yield 出 `host:port` 字符串。目录会被自动扫描，无需注册；用 `setting.py` 的 `PROXY_FETCHER_EXCLUDE`（类名黑名单）临时禁用。
- **新增配置项**：同时改 `setting.py`（默认值）和 `handler/configHandler.py`（`LazyProperty` + `os.getenv` 环境变量覆盖）。环境变量可覆盖一切配置，Docker 部署即靠此机制。

## 代码约定

- **文件头**：每个 `.py` 必须带标准头（File Name / Description / Author / date / Change Activity）加 `__author__ = 'JHao'`，照抄现有文件格式。
- **命名**：文件名驼峰（`proxyHandler.py`，但 fetcher/sources 下源文件全小写如 `kuaidaili.py`）；类名 PascalCase；方法混合风格——DB/fetcher 方法驼峰（`getAll`、`changeTable`），属性/辅助方法下划线（`fail_count`）；常量大写下划线。
- **注释**：中文（源文件头与行内注释均为普通话）。
- **单例**：`withMetaclass(Singleton)`（来自内置的 `util/six.py`），ConfigHandler 等均如此。
- **兼容性**：最低支持 Python 3.8——不要用 3.9+ 才有的语法/标准库特性；依赖有按版本的条件安装（APScheduler 3.2/3.10 分支）。

## 测试注意事项

- `tests/conftest.py` 有 autouse fixture `reset_singleton`：每个测试前后清空 `Singleton._inst`，防单例泄漏；新测试无需自行处理。
- mock DB 时 patch 的是 `handler.proxyHandler.DbClient`（已 import 进本地命名空间），不是 `db.dbClient.DbClient`，否则不生效。
- 单元/API 测试用 `fakeredis`，不需要任何外部服务；集成测试标 `@pytest.mark.integration`，在 `pyproject.toml` 注册了该 marker。
- 测试函数命名 `test_` 前缀 + 下划线（如 `test_get_with_https`）。

## 修改敏感区域前先读

- 扩展 fetcher/validator：`docs/extending/fetcher.md`、`docs/extending/validator.md`
- 配置项含义：`docs/configuration.md`；项目结构：`docs/project-structure.md`
- Docker 运行方式：`Dockerfile`、`docker-compose.yml`、`docs/docker.md`（alpine 镜像，依赖 lxml 编译）
