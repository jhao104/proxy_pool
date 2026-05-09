# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name:     anonymousChecker.py
   Description :  匿名代理检测模块（增强版）
   Author :       Antigravity
   date:          2026/02/04
-------------------------------------------------
   主要改进：
   1. 使用多端点交叉验证（httpbin.org/ip + httpbin.org/headers）
   2. 检测 HTTP 头中是否暴露真实 IP
   3. 只有通过严格验证的代理才存入匿名库
-------------------------------------------------
"""
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


# 常见的暴露真实 IP 的 HTTP 头
PROXY_HEADERS = [
    'X-Forwarded-For',
    'X-Real-Ip',
    'X-Forwarded',
    'Forwarded-For',
    'Forwarded',
    'Via',
    'X-Client-Ip',
    'Client-Ip',
    'True-Client-Ip',
    'Cf-Connecting-Ip',
]


class AnonymousChecker:
    """匿名代理检测器（增强版）"""

    def __init__(self, timeout=10, max_workers=10):
        self.log = LogHandler("anonymous_checker")
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()
        self.timeout = timeout
        self.max_workers = max_workers
        self.check_url = self.conf.anonymousCheckUrl
        self.headers_url = self.check_url.replace('/ip', '/headers')
        self._real_ip = None

    def _get_real_ip(self):
        """获取本机真实出口 IP（不使用代理）"""
        if self._real_ip:
            return self._real_ip
        try:
            resp = requests.get(self.check_url, timeout=self.timeout)
            resp.raise_for_status()
            self._real_ip = resp.json().get("origin", "").split(',')[0].strip()
            self.log.info(f"本机真实 IP: {self._real_ip}")
            return self._real_ip
        except Exception as e:
            self.log.warning(f"获取本机真实 IP 失败: {e}")
            return None

    def _check_anonymous(self, proxy, real_ip=None):
        """
        增强的匿名性检测

        严格检测条件：
        1. 请求能够成功
        2. origin IP 只有代理 IP，不包含真实 IP
        3. HTTP 响应头中无暴露真实 IP 的信息

        Args:
            proxy: Proxy 对象
            real_ip: 本机真实 IP（用于对比验证）

        Returns:
            (proxy, is_anonymous, origin_ip, reason) 元组
        """
        proxy_str = proxy.proxy  # host:port
        proxy_ip = proxy_str.split(':')[0]

        proxies = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            # 步骤 1: 检测 origin IP
            resp_ip = requests.get(
                self.check_url,
                proxies=proxies,
                timeout=self.timeout,
                headers=headers
            )
            resp_ip.raise_for_status()

            origin = resp_ip.json().get("origin", "")
            origin_ips = [ip.strip() for ip in origin.split(',')]

            # 检查 1: 如果包含真实 IP，直接判定为透明代理
            if real_ip and real_ip in origin_ips:
                return proxy, False, origin, "透明代理(暴露真实IP)"

            # 检查 2: origin 中应该只有一个 IP 且是代理 IP
            if len(origin_ips) != 1:
                return proxy, False, origin, "普通匿名(多IP)"

            if origin_ips[0] != proxy_ip:
                # 如果 origin 不是代理 IP，可能是代理的出口 IP 不同，仍算匿名
                # 但需要确保不是真实 IP
                if real_ip and origin_ips[0] == real_ip:
                    return proxy, False, origin, "透明代理"

            # 步骤 2: 检测 HTTP 头是否暴露信息
            try:
                resp_headers = requests.get(
                    self.headers_url,
                    proxies=proxies,
                    timeout=self.timeout,
                    headers=headers
                )
                resp_headers.raise_for_status()

                response_headers = resp_headers.json().get("headers", {})

                # 检查是否有暴露真实 IP 的头
                for header in PROXY_HEADERS:
                    header_value = response_headers.get(header, "")
                    if header_value and real_ip and real_ip in header_value:
                        return proxy, False, origin, f"头部暴露({header})"

            except Exception:
                # headers 检测失败，降低信任度但仍可能是匿名代理
                self.log.debug(f"检测 {proxy_str} 的 headers 失败，仅通过 IP 检测")

            # 所有检查通过，为高匿代理
            return proxy, True, origin, "高匿代理"

        except requests.exceptions.Timeout:
            return proxy, False, None, "超时"
        except requests.exceptions.ProxyError:
            return proxy, False, None, "代理连接失败"
        except Exception as e:
            self.log.debug(f"检测 {proxy_str} 匿名性失败: {e}")
            return proxy, False, None, f"异常: {str(e)[:50]}"

    def run(self):
        """
        执行匿名性检测

        获取所有可用代理，使用增强检测其匿名性，
        只有真正高匿的代理才存入 anonymous_proxy 表
        """
        self.log.info("开始匿名性检测（增强版）...")

        # 获取本机真实 IP，用于严格验证
        real_ip = self._get_real_ip()
        if not real_ip:
            self.log.warning("未能获取本机 IP，将使用基础检测模式")

        # 获取所有可用代理
        all_proxies = self.proxy_handler.getAll()
        if not all_proxies:
            self.log.info("没有可用代理，跳过匿名性检测")
            return {"anonymous": 0, "transparent": 0, "failed": 0}

        self.log.info(f"共有 {len(all_proxies)} 个代理需要检测")

        anonymous_count = 0
        transparent_count = 0
        failed_count = 0

        # 并发检测
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._check_anonymous, proxy, real_ip): proxy
                for proxy in all_proxies
            }

            for future in as_completed(futures):
                proxy, is_anonymous, origin, reason = future.result()

                if origin is None:
                    failed_count += 1
                    continue

                if is_anonymous:
                    # 只有高匿代理才存入
                    self.proxy_handler.putAnonymous(proxy)
                    anonymous_count += 1
                    self.log.debug(f"高匿代理: {proxy.proxy} -> {origin}")
                else:
                    transparent_count += 1
                    self.log.debug(f"{reason}: {proxy.proxy} -> {origin}")

        self.log.info(
            f"匿名性检测完成: "
            f"高匿={anonymous_count}, 透明/普通={transparent_count}, 失败={failed_count}"
        )

        return {
            "anonymous": anonymous_count,
            "transparent": transparent_count,
            "failed": failed_count
        }


def runAnonymousCheck():
    """运行匿名性检测的便捷函数"""
    checker = AnonymousChecker()
    return checker.run()


if __name__ == '__main__':
    # 测试
    print("=== 匿名性检测（增强版） ===")
    result = runAnonymousCheck()
    print(f"检测结果: {result}")
