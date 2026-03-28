# -*- coding: utf-8 -*-
"""
代理池服务可用性测试脚本

测试部署在 http://192.168.2.127:5010/ 的代理池服务
验证获取的代理是否可用
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# 代理池服务地址
PROXY_POOL_URL = "http://192.168.2.127:5010"

# 用于测试代理的目标网站
TEST_URLS = [
    "http://httpbin.org/ip",
    "http://www.baidu.com",
    "https://www.qq.com",
]

# 请求超时时间（秒）
TIMEOUT = 10


class ProxyPoolTester:
    """代理池测试器"""

    def __init__(self, pool_url: str):
        self.pool_url = pool_url.rstrip("/")

    def get_service_info(self) -> dict:
        """获取代理池服务信息"""
        try:
            resp = requests.get(f"{self.pool_url}/", timeout=TIMEOUT)
            resp.raise_for_status()
            return {"success": True, "data": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_proxy_count(self) -> dict:
        """获取代理池中代理数量"""
        try:
            resp = requests.get(f"{self.pool_url}/count", timeout=TIMEOUT)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_random_proxy(self, https: bool = False) -> dict:
        """随机获取一个代理"""
        try:
            url = f"{self.pool_url}/get"
            if https:
                url += "?type=https"
            resp = requests.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_all_proxies(self, https: bool = False) -> dict:
        """获取所有代理"""
        try:
            url = f"{self.pool_url}/all"
            if https:
                url += "?type=https"
            resp = requests.get(url, timeout=TIMEOUT)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_proxy(self, proxy: str) -> dict:
        """删除指定代理"""
        try:
            resp = requests.get(
                f"{self.pool_url}/delete",
                params={"proxy": proxy},
                timeout=TIMEOUT
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ProxyValidator:
    """代理验证器"""

    @staticmethod
    def test_proxy(proxy: str, test_url: str, timeout: int = TIMEOUT) -> dict:
        """
        测试单个代理是否可用

        Args:
            proxy: 代理地址，格式为 host:port
            test_url: 测试目标URL
            timeout: 超时时间

        Returns:
            测试结果字典
        """
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }

        start_time = time.time()
        try:
            resp = requests.get(
                test_url,
                proxies=proxies,
                timeout=timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ProxyTest/1.0)"}
            )
            elapsed = time.time() - start_time

            # 尝试获取响应内容
            response_text = None
            origin_ip = None
            try:
                response_text = resp.text
                # 如果是 httpbin.org/ip，解析返回的 IP
                if "httpbin" in test_url and "/ip" in test_url:
                    origin_ip = resp.json().get("origin")
            except Exception:
                pass

            return {
                "proxy": proxy,
                "test_url": test_url,
                "success": True,
                "status_code": resp.status_code,
                "elapsed": round(elapsed, 3),
                "response_text": response_text,
                "origin_ip": origin_ip,
            }
        except requests.exceptions.Timeout:
            return {
                "proxy": proxy,
                "test_url": test_url,
                "success": False,
                "error": "timeout",
                "elapsed": round(time.time() - start_time, 3),
            }
        except requests.exceptions.ProxyError as e:
            return {
                "proxy": proxy,
                "test_url": test_url,
                "success": False,
                "error": f"proxy_error: {str(e)[:50]}",
                "elapsed": round(time.time() - start_time, 3),
            }
        except Exception as e:
            return {
                "proxy": proxy,
                "test_url": test_url,
                "success": False,
                "error": str(e)[:100],
                "elapsed": round(time.time() - start_time, 3),
            }

    @staticmethod
    def batch_test_proxy(proxy: str, test_urls: list, timeout: int = TIMEOUT) -> dict:
        """
        使用多个目标URL测试代理

        Args:
            proxy: 代理地址
            test_urls: 测试目标URL列表
            timeout: 超时时间

        Returns:
            综合测试结果
        """
        results = []
        success_count = 0

        for url in test_urls:
            result = ProxyValidator.test_proxy(proxy, url, timeout)
            results.append(result)
            if result["success"]:
                success_count += 1

        return {
            "proxy": proxy,
            "total_tests": len(test_urls),
            "success_count": success_count,
            "success_rate": round(success_count / len(test_urls) * 100, 1),
            "details": results,
        }


def print_separator(char: str = "-", length: int = 60):
    """打印分隔线"""
    print(char * length)


def test_proxy_pool_service():
    """测试代理池服务的主函数"""
    print("\n" + "=" * 60)
    print("代理池服务可用性测试")
    print(f"服务地址: {PROXY_POOL_URL}")
    print("=" * 60)

    tester = ProxyPoolTester(PROXY_POOL_URL)
    validator = ProxyValidator()

    # 1. 测试服务连通性
    print("\n[1] 测试服务连通性...")
    service_info = tester.get_service_info()
    if service_info["success"]:
        print(f"    服务连接成功")
    else:
        print(f"    服务连接失败: {service_info['error']}")
        print("\n请检查服务是否正常运行！")
        return

    # 2. 获取代理数量
    print("\n[2] 获取代理池状态...")
    count_result = tester.get_proxy_count()
    if count_result["success"]:
        count_data = count_result["data"]
        print(f"    代理池状态: {count_data}")
        total_count = count_data.get("count", 0)
        if total_count == 0:
            print("\n    代理池中没有可用代理，请等待调度程序采集代理后再试！")
            return
    else:
        print(f"    获取失败: {count_result['error']}")
        return

    # 3. 随机获取代理测试
    print("\n[3] 随机获取代理...")
    proxy_result = tester.get_random_proxy()
    if proxy_result["success"]:
        proxy_data = proxy_result["data"]
        proxy_addr = proxy_data.get("proxy")
        print(f"    获取到代理: {proxy_addr}")
        print(f"    代理详情: {proxy_data}")
    else:
        print(f"    获取失败: {proxy_result['error']}")
        return

    # 4. 测试代理可用性
    print("\n[4] 测试代理可用性...")
    print(f"    代理: {proxy_addr}")
    print(f"    测试目标: {TEST_URLS}")
    print_separator()

    batch_result = validator.batch_test_proxy(proxy_addr, TEST_URLS)
    for detail in batch_result["details"]:
        status = "OK" if detail["success"] else "FAIL"
        elapsed = detail["elapsed"]
        error_info = f" ({detail.get('error', '')})" if not detail["success"] else ""
        print(f"    [{status}] {detail['test_url']:<40} {elapsed}s{error_info}")

    print_separator()
    print(f"    成功率: {batch_result['success_rate']}% "
          f"({batch_result['success_count']}/{batch_result['total_tests']})")

    # 5. 批量测试多个代理
    print("\n[5] 批量测试多个代理...")
    all_result = tester.get_all_proxies()
    if not all_result["success"]:
        print(f"    获取代理列表失败: {all_result['error']}")
        return

    all_proxies = all_result["data"]
    if isinstance(all_proxies, list):
        proxy_list = [p.get("proxy") for p in all_proxies if p.get("proxy")]
    else:
        proxy_list = []

    # 限制测试数量
    max_test_count = 10
    proxies_to_test = proxy_list[:max_test_count]
    print(f"    共有 {len(proxy_list)} 个代理，测试前 {len(proxies_to_test)} 个")

    if not proxies_to_test:
        print("    没有代理可供测试")
        return

    # 使用线程池并发测试
    test_url = "http://httpbin.org/ip"
    print(f"    测试目标: {test_url}")
    print_separator()

    success_proxies = []
    failed_proxies = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(validator.test_proxy, proxy, test_url): proxy
            for proxy in proxies_to_test
        }

        for future in as_completed(futures):
            result = future.result()
            proxy = result["proxy"]
            if result["success"]:
                success_proxies.append(proxy)
                origin_ip = result.get("origin_ip", "")
                origin_info = f" -> origin: {origin_ip}" if origin_ip else ""
                print(f"    [OK]   {proxy:<25} {result['elapsed']}s{origin_info}")
            else:
                failed_proxies.append(proxy)
                error = result.get("error", "unknown")
                print(f"    [FAIL] {proxy:<25} {result['elapsed']}s ({error[:30]})")

    print_separator()
    total = len(proxies_to_test)
    success = len(success_proxies)
    print(f"    测试结果: 成功 {success}/{total} ({round(success/total*100, 1)}%)")

    # 6. 测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"    代理池服务地址: {PROXY_POOL_URL}")
    print(f"    代理池总数: {len(proxy_list)}")
    print(f"    测试代理数: {total}")
    print(f"    可用代理数: {success}")
    print(f"    可用率: {round(success/total*100, 1)}%")

    if success_proxies:
        print("\n    可用代理列表:")
        for p in success_proxies[:5]:
            print(f"        {p}")
        if len(success_proxies) > 5:
            print(f"        ... 还有 {len(success_proxies) - 5} 个")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_proxy_pool_service()
