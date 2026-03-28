# -*- coding: utf-8 -*-
"""
本地完整流程验证脚本

模拟整个流程：获取代理 -> 验证可用性 -> 匿名性检测
"""
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# 配置
ANONYMOUS_CHECK_URL = 'http://httpbin.org/ip'
HTTP_CHECK_URL = 'http://httpbin.org/get'
TIMEOUT = 10


def get_all_proxies_from_sources():
    """从所有代理源获取代理"""
    proxies = set()

    # 从 freeproxyAdapter 获取
    print("  [1] 从 freeproxyAdapter 获取代理...")
    try:
        from fetcher.freeproxyAdapter import FreeproxyAdapter
        adapter = FreeproxyAdapter()
        for proxy in adapter.fetch_all():
            proxies.add(proxy)
    except Exception as e:
        print(f"      错误: {e}")

    print(f"  总计获取到 {len(proxies)} 个代理")
    return list(proxies)


def verify_proxy(proxy_str):
    """验证代理是否可用"""
    proxies = {
        "http": f"http://{proxy_str}",
        "https": f"http://{proxy_str}",
    }
    try:
        resp = requests.get(
            HTTP_CHECK_URL,
            proxies=proxies,
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp.raise_for_status()
        return proxy_str, True, None
    except Exception as e:
        return proxy_str, False, str(e)[:30]


def check_anonymous(proxy_str):
    """检测代理是否匿名"""
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
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp.raise_for_status()

        origin = resp.json().get("origin", "")
        origin_ips = [ip.strip() for ip in origin.split(',')]

        # 只有代理 IP 返回时为匿名
        is_anonymous = (len(origin_ips) == 1 and origin_ips[0] == proxy_ip)
        return proxy_str, is_anonymous, origin
    except Exception as e:
        return proxy_str, None, str(e)[:30]


def main():
    print("=" * 60)
    print("本地完整流程验证")
    print("=" * 60)

    # 阶段1：获取代理
    print("\n[阶段1] 获取代理")
    all_proxies = get_all_proxies_from_sources()

    if not all_proxies:
        print("没有获取到代理，退出")
        return

    # 只测试前50个代理
    test_proxies = all_proxies[:50]
    print(f"\n  将测试前 {len(test_proxies)} 个代理")

    # 阶段2：验证可用性
    print("\n[阶段2] 验证代理可用性")
    print("-" * 60)

    valid_proxies = []
    invalid_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(verify_proxy, p): p for p in test_proxies
        }
        for future in as_completed(futures):
            proxy, is_valid, error = future.result()
            if is_valid:
                valid_proxies.append(proxy)
                print(f"    [OK] {proxy}")
            else:
                invalid_count += 1

    print(f"\n  可用: {len(valid_proxies)}, 不可用: {invalid_count}")

    if not valid_proxies:
        print("没有可用代理，退出")
        return

    # 阶段3：匿名性检测
    print("\n[阶段3] 匿名性检测")
    print("-" * 60)

    anonymous_proxies = []
    transparent_proxies = []
    failed_count = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(check_anonymous, p): p for p in valid_proxies
        }
        for future in as_completed(futures):
            proxy, is_anonymous, origin = future.result()
            if is_anonymous is None:
                failed_count += 1
                print(f"    [FAIL] {proxy:<25} {origin}")
            elif is_anonymous:
                anonymous_proxies.append(proxy)
                print(f"    [ANON] {proxy:<25} -> {origin}")
            else:
                transparent_proxies.append(proxy)
                print(f"    [TRAN] {proxy:<25} -> {origin}")

    # 结果统计
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)
    print(f"  获取代理总数: {len(all_proxies)}")
    print(f"  测试代理数量: {len(test_proxies)}")
    print(f"  可用代理数量: {len(valid_proxies)}")
    print(f"  匿名代理数量: {len(anonymous_proxies)}")
    print(f"  透明代理数量: {len(transparent_proxies)}")

    if anonymous_proxies:
        print(f"\n匿名代理列表:")
        for p in anonymous_proxies:
            print(f"    {p}")


if __name__ == "__main__":
    main()
