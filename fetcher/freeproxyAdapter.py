# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:     freeproxyAdapter.py
   Description :  额外的免费代理源（移植自 freeproxy 项目）
   Author :       Antigravity
   date:          2026/02/03
-------------------------------------------------
   将 freeproxy 项目的代理源核心逻辑移植到此处
   不依赖外部项目，可在 Docker 容器中独立运行
-------------------------------------------------
"""
import re
import requests
from time import sleep


class FreeproxyAdapter:
    """
    额外的免费代理源

    从多个免费代理源获取代理，返回 host:port 格式
    """

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)

    def fetch_thespeedx(self):
        """
        TheSpeedX 代理列表
        来源: https://github.com/TheSpeedX/SOCKS-List
        """
        urls = [
            'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
        ]

        for url in urls:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                for line in resp.text.strip().split('\n'):
                    line = line.strip()
                    if line and ':' in line:
                        # 验证格式 ip:port
                        parts = line.split(':')
                        if len(parts) == 2 and parts[1].isdigit():
                            yield line
            except Exception as e:
                print(f"[TheSpeedX] 获取失败: {e}")

    def fetch_proxyscrape(self):
        """
        ProxyScrape API
        来源: https://proxyscrape.com/free-proxy-list
        """
        try:
            url = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=get_proxies&skip=0&proxy_format=protocolipport&format=json&limit=500"
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get('proxies', []):
                if not item.get('alive'):
                    continue
                ip = item.get('ip')
                port = item.get('port')
                if ip and port:
                    yield f"{ip}:{port}"
        except Exception as e:
            print(f"[ProxyScrape] 获取失败: {e}")

    def fetch_geonode(self):
        """
        Geonode 代理列表
        来源: https://geonode.com/free-proxy-list
        """
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=200&page=1&sort_by=lastChecked&sort_type=desc"
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get('data', []):
                ip = item.get('ip')
                port = item.get('port')
                if ip and port:
                    yield f"{ip}:{port}"
        except Exception as e:
            print(f"[Geonode] 获取失败: {e}")

    def fetch_freeproxylist(self):
        """
        Free Proxy List
        来源: https://free-proxy-list.net/
        """
        try:
            url = "https://free-proxy-list.net/"
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()

            # 解析 HTML 中的代理
            pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)'
            matches = re.findall(pattern, resp.text)
            for ip, port in matches:
                yield f"{ip}:{port}"
        except Exception as e:
            print(f"[FreeProxyList] 获取失败: {e}")

    def fetch_proxylistdownload(self):
        """
        Proxy List Download
        来源: https://www.proxy-list.download/
        """
        urls = [
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://www.proxy-list.download/api/v1/get?type=https',
        ]

        for url in urls:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                for line in resp.text.strip().split('\n'):
                    line = line.strip()
                    if line and ':' in line:
                        yield line
            except Exception as e:
                print(f"[ProxyListDownload] 获取失败: {e}")

    def fetch_sunny9577(self):
        """
        Sunny9577 GitHub 代理列表
        来源: https://github.com/sunny9577/proxy-scraper
        """
        urls = [
            'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
        ]

        for url in urls:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                resp.raise_for_status()
                for line in resp.text.strip().split('\n'):
                    line = line.strip()
                    if line and ':' in line:
                        parts = line.split(':')
                        if len(parts) == 2 and parts[1].isdigit():
                            yield line
            except Exception as e:
                print(f"[Sunny9577] 获取失败: {e}")

    def fetch_clarketm(self):
        """
        Clarketm GitHub 代理列表
        来源: https://github.com/clarketm/proxy-list
        """
        try:
            url = 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt'
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            for line in resp.text.strip().split('\n'):
                line = line.strip()
                if line and ':' in line:
                    parts = line.split(':')
                    if len(parts) == 2 and parts[1].isdigit():
                        yield line
        except Exception as e:
            print(f"[Clarketm] 获取失败: {e}")

    def fetch_all(self):
        """
        从所有代理源获取代理

        Yields:
            代理地址 (host:port 格式)
        """
        seen = set()
        sources = [
            ('TheSpeedX', self.fetch_thespeedx),
            ('ProxyScrape', self.fetch_proxyscrape),
            ('Geonode', self.fetch_geonode),
            ('FreeProxyList', self.fetch_freeproxylist),
            ('ProxyListDownload', self.fetch_proxylistdownload),
            ('Sunny9577', self.fetch_sunny9577),
            ('Clarketm', self.fetch_clarketm),
        ]

        for name, fetcher in sources:
            try:
                count = 0
                for proxy in fetcher():
                    if proxy not in seen:
                        seen.add(proxy)
                        count += 1
                        yield proxy
                if count > 0:
                    print(f"[{name}] 获取到 {count} 个代理")
            except Exception as e:
                print(f"[{name}] 处理失败: {e}")
            sleep(0.5)  # 避免请求过快


def get_freeproxy_proxies():
    """
    便捷函数：获取所有外部代理源的代理

    Yields:
        代理地址 (host:port 格式)
    """
    adapter = FreeproxyAdapter()
    for proxy in adapter.fetch_all():
        yield proxy


if __name__ == '__main__':
    # 测试
    print("测试 FreeproxyAdapter...")
    adapter = FreeproxyAdapter()
    count = 0
    for proxy in adapter.fetch_all():
        print(f"  {proxy}")
        count += 1
    print(f"\n总共获取到 {count} 个代理")
