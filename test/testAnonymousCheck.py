# -*- coding: utf-8 -*-
"""
手动触发匿名性检测测试脚本

用于测试匿名代理检测功能，无需等待调度程序
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# 代理池服务地址
PROXY_POOL_URL = "http://192.168.2.127:5010"

# 匿名性检测 URL
ANONYMOUS_CHECK_URL = "http://httpbin.org/ip"

# 超时时间
TIMEOUT = 10


def get_all_proxies():
    """获取所有代理"""
    try:
        resp = requests.get(f"{PROXY_POOL_URL}/all/", timeout=TIMEOUT)
        return resp.json()
    except Exception as e:
        print(f"获取代理失败: {e}")
        return []


def check_anonymous(proxy_info):
    """
    检测代理是否为匿名代理

    Returns:
        (proxy_str, is_anonymous, origin_ip)
    """
    proxy_str = proxy_info.get("proxy")
    if not proxy_str:
        return None, False, None

    proxy_ip = proxy_str.split(':')[0]

    proxies = {
        "http": f"http://{proxy_str}",
        "https": f"http://{proxy_str}",
    }

    try:
        resp = requests.get(
            ANONYMOUS_CHECK_URL,
            proxies=proxies,
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AnonymousChecker/1.0)"}
        )
        resp.raise_for_status()

        origin = resp.json().get("origin", "")
        origin_ips = [ip.strip() for ip in origin.split(',')]

        # 如果 origin 中只有代理 IP，则为匿名代理
        is_anonymous = (len(origin_ips) == 1 and origin_ips[0] == proxy_ip)

        return proxy_str, is_anonymous, origin

    except Exception as e:
        return proxy_str, False, f"error: {str(e)[:30]}"


def main():
    print("=" * 60)
    print("匿名代理检测测试")
    print(f"代理池: {PROXY_POOL_URL}")
    print("=" * 60)

    # 获取所有代理
    print("\n[1] 获取代理列表...")
    proxies = get_all_proxies()
    print(f"    共 {len(proxies)} 个代理")

    if not proxies:
        print("    没有代理可检测")
        return

    # 并发检测
    print("\n[2] 检测匿名性...")
    print("-" * 60)

    anonymous_list = []
    transparent_list = []
    failed_list = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(check_anonymous, p): p
            for p in proxies
        }

        for future in as_completed(futures):
            proxy_str, is_anonymous, origin = future.result()
            if proxy_str is None:
                continue

            if "error" in str(origin):
                failed_list.append(proxy_str)
                print(f"    [FAIL] {proxy_str:<25} {origin}")
            elif is_anonymous:
                anonymous_list.append(proxy_str)
                print(f"    [ANON] {proxy_str:<25} -> {origin}")
            else:
                transparent_list.append(proxy_str)
                print(f"    [TRAN] {proxy_str:<25} -> {origin}")

    # 结果统计
    print("-" * 60)
    print(f"\n[3] 检测结果:")
    print(f"    匿名代理: {len(anonymous_list)}")
    print(f"    透明代理: {len(transparent_list)}")
    print(f"    检测失败: {len(failed_list)}")

    if anonymous_list:
        print(f"\n    匿名代理列表:")
        for p in anonymous_list:
            print(f"        {p}")

    print("\n" + "=" * 60)
    print("检测完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
