# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     poolaggr.py
   Description :   公共代理池聚合源
   Author :        JHao
   date：          2026/11/22
-------------------------------------------------
   Change Activity:
                   2026/11/22: 新增 12 个公共代理池的 /all/ 聚合源
                   2026/11/22: 聚合源抓取间隔调整为 6 小时
-------------------------------------------------
"""
__author__ = 'JHao'

import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

PROXY_PATTERN = re.compile(r'^\d{1,3}(?:\.\d{1,3}){3}:\d{2,5}$')


class _PoolAggrBase(BaseFetcher):
    """公共代理池 /all/ 聚合基类, 每个子类对应一个池"""

    name = ""
    url = ""
    endpoint = ""

    enabled = True
    # 聚合源更新频率不高, 6 小时抓一次, 避免频繁请求他人服务
    interval = 6 * 60 * 60

    def fetch(self):
        try:
            r = WebRequest().get(self.endpoint, timeout=10, retry_time=1)
            proxies = self._extractProxies(r)
            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - %s: %s" % (self.name, e))

    def _extractProxies(self, response):
        """兼容 list[dict] / dict{proxies,data,result} / 纯文本"""
        payload = response.json
        items = []
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            for key in ("proxies", "data", "result"):
                if isinstance(payload.get(key), list):
                    items = payload[key]
                    break

        proxies = []
        for item in items:
            if isinstance(item, str):
                proxies.extend(self.parseProxiesFromText(item))
                continue
            if not isinstance(item, dict):
                continue
            # 池内已标记失效的条目不取, 减少无效验证
            if item.get("last_status") is False:
                continue
            proxy = item.get("proxy")
            if not proxy and item.get("ip") and item.get("port"):
                proxy = "%s:%s" % (item["ip"], item["port"])
            proxy = str(proxy or "").strip()
            if PROXY_PATTERN.match(proxy):
                proxies.append(proxy)

        if not proxies:
            proxies = self.parseProxiesFromText(response.text or "")
        return proxies


class PoolAggrAli39105Fetcher(_PoolAggrBase):
    """阿里云 39.105.98.233:5009"""

    name = "poolaggr_ali_39_105"
    url = "http://39.105.98.233:5009"
    endpoint = url + "/all/"


class PoolAggrTencent182Fetcher(_PoolAggrBase):
    """腾讯云 182.254.172.218:5010"""

    name = "poolaggr_tencent_182_254"
    url = "http://182.254.172.218:5010"
    endpoint = url + "/all/"


class PoolAggrTencentHk43Fetcher(_PoolAggrBase):
    """腾讯云(HK) 43.154.125.140:5010"""

    name = "poolaggr_tencent_hk_43_154"
    url = "http://43.154.125.140:5010"
    endpoint = url + "/all/"


class PoolAggrAli47120Fetcher(_PoolAggrBase):
    """阿里云 47.120.7.67:5010"""

    name = "poolaggr_ali_47_120"
    url = "http://47.120.7.67:5010"
    endpoint = url + "/all/"


class PoolAggrLinode172Fetcher(_PoolAggrBase):
    """Akamai/Linode 172.104.79.56:5050"""

    name = "poolaggr_linode_172_104"
    url = "http://172.104.79.56:5050"
    endpoint = url + "/all/"


class PoolAggrAli12079Fetcher(_PoolAggrBase):
    """阿里云 120.79.73.8:5010"""

    name = "poolaggr_ali_120_79"
    url = "http://120.79.73.8:5010"
    endpoint = url + "/all/"


class PoolAggrAli47102Fetcher(_PoolAggrBase):
    """阿里云 47.102.218.41:5010"""

    name = "poolaggr_ali_47_102"
    url = "http://47.102.218.41:5010"
    endpoint = url + "/all/"


class PoolAggrHostPapa180Fetcher(_PoolAggrBase):
    """HostPapa 172.245.180.249:5010"""

    name = "poolaggr_hostpapa_172_245_180"
    url = "http://172.245.180.249:5010"
    endpoint = url + "/all/"


class PoolAggrHostPapa240Fetcher(_PoolAggrBase):
    """HostPapa 172.245.240.207:5010

    实测连接超时, 默认关闭; 站点恢复后可直接启用。
    """

    name = "poolaggr_hostpapa_172_245_240"
    url = "http://172.245.240.207:5010"
    endpoint = url + "/all/"
    enabled = False


class PoolAggrAli47106Fetcher(_PoolAggrBase):
    """阿里云 47.106.153.111:5010"""

    name = "poolaggr_ali_47_106"
    url = "http://47.106.153.111:5010"
    endpoint = url + "/all/"


class PoolAggrPsychz108Fetcher(_PoolAggrBase):
    """Psychz 108.181.20.225:5010"""

    name = "poolaggr_psychz_108_181"
    url = "http://108.181.20.225:5010"
    endpoint = url + "/all/"


class PoolAggrTelecom120Fetcher(_PoolAggrBase):
    """电信 120.132.146.118:25010"""

    name = "poolaggr_telecom_120_132"
    url = "http://120.132.146.118:25010"
    endpoint = url + "/all/"


if __name__ == '__main__':
    for cls in (
        PoolAggrAli39105Fetcher, PoolAggrTencent182Fetcher,
        PoolAggrTencentHk43Fetcher, PoolAggrAli47120Fetcher,
        PoolAggrLinode172Fetcher, PoolAggrAli12079Fetcher,
        PoolAggrAli47102Fetcher, PoolAggrHostPapa180Fetcher,
        PoolAggrHostPapa240Fetcher, PoolAggrAli47106Fetcher,
        PoolAggrPsychz108Fetcher, PoolAggrTelecom120Fetcher,
    ):
        for proxy in cls().fetch():
            print("%s %s" % (cls.name, proxy))
