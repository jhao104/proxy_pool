---
hide:
  - navigation
  - toc
---

<div class="tx-hero" markdown>

# ProxyPool

**Python爬虫代理IP池** — 定时采集、验证、存储免费代理，通过 RESTful API 提供服务。

[:octicons-mark-github-16: GitHub](https://github.com/jhao104/proxy_pool){ .md-button }
[:octicons-rocket-16: 快速开始](getting-started.md){ .md-button .md-button--primary }

</div>

<div class="tx-features" markdown>

<div class="tx-feature" markdown>

### :material-access-point-network: 多源采集

内置 15+ 免费代理源，支持自定义扩展，定时自动采集。

</div>

<div class="tx-feature" markdown>

### :material-shield-check: 自动验证

HTTP/HTTPS 可用性自动校验，剔除失效代理，保证代理质量。

</div>

<div class="tx-feature" markdown>

### :material-database: 持久存储

Redis/SSDB 持久化存储，支持集群部署，数据不丢失。

</div>

<div class="tx-feature" markdown>

### :material-api: RESTful API

提供 `/get`、`/pop`、`/all`、`/count`、`/delete` 等接口，开箱即用。

</div>

<div class="tx-feature" markdown>

### :material-docker: Docker 部署

一条命令启动，支持 docker-compose，自带 Redis 服务。

</div>

<div class="tx-feature" markdown>

### :material-clock-fast: 定时调度

APScheduler 驱动，自动维护代理池数量，无需人工干预。

</div>

</div>

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/jhao104/proxy_pool.git
cd proxy_pool

# 安装依赖
pip install -r requirements.txt

# 启动调度程序（采集和验证代理）
python proxyPool.py schedule

# 启动 API 服务
python proxyPool.py server
```

启动后访问 `http://127.0.0.1:5010/get` 即可获取一个代理。

## API 示例

```python
import requests

# 获取代理
proxy = requests.get("http://127.0.0.1:5010/get/").json()

# 使用代理
html = requests.get(
    "http://www.example.com",
    proxies={"http": f"http://{proxy['proxy']}"}
)
```

## 文档导航

| 章节 | 说明 |
|------|------|
| [快速开始](getting-started.md) | 安装、配置、启动项目 |
| [项目结构](project-structure.md) | 目录结构与核心模块说明 |
| [配置参考](configuration.md) | `setting.py` 全部配置项详解 |
| [API 使用](api.md) | RESTful API 端点与调用示例 |
| [Docker 部署](docker.md) | Docker / docker-compose 部署方式 |
| [扩展代理源](extending/fetcher.md) | 自定义代理采集方法 |
| [扩展校验器](extending/validator.md) | 自定义代理校验规则 |
| [变更日志](changelog.md) | 版本发布记录 |