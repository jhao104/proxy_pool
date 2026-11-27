# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxynova.py
   Description :   ProxyNova代理源
   Author :        JHao
   date：          2026/11/21
-------------------------------------------------
   Change Activity:
                   2026/11/21: 新增 proxynova 代理源
-------------------------------------------------
"""
__author__ = 'JHao'

import base64
import re

from fetcher.baseFetcher import BaseFetcher
from handler.logHandler import LogHandler
from util.webRequest import WebRequest

logger = LogHandler("fetcher")

_PROXY_RE = re.compile(r'\d{1,3}(?:\.\d{1,3}){3}')
_ATOB_RE = re.compile(r'atob\("([^"]+)"\)')


def _extractIpFromScript(script):
    """
    从第一列 script 中还原 IP

    proxynova 用 atob("base64") 拆分并拼接 IP, 例如:
        document.write(atob("MTg1LjE4Ni4=")+atob("MTYyLjIxNw=="))
    这里用纯 Python 完成 atob 解码, 避免引入 py_mini_racer/ctx.eval。
    """
    if not script:
        return None

    def _decode(match):
        try:
            text = base64.b64decode(match.group(1)).decode('utf-8')
        except Exception:
            return '""'
        return '"%s"' % text.replace('"', '')

    # 先还原 atob 调用, 再按 JS 字符串拼接语义合并所有字面量
    replaced = _ATOB_RE.sub(_decode, script)
    literals = re.findall(r"""['"]([^'"]*)['"]""", replaced)
    candidate = ''.join(literals)

    if not candidate:
        parts = []
        for b64_str in _ATOB_RE.findall(script):
            try:
                parts.append(base64.b64decode(b64_str).decode('utf-8'))
            except Exception:
                pass
        candidate = ''.join(parts)

    match = _PROXY_RE.search(candidate)
    return match.group(0) if match else None


class ProxyNovaFetcher(BaseFetcher):
    """
    ProxyNova https://www.proxynova.com/proxy-server-list/

    实测结论: 当前部署环境 DNS 被污染(解析到不可达地址)且多次请求超时,
    无法确认真实页面数据, 故 enabled=False; 解析逻辑按页面结构完整实现,
    在可正常访问的网络中可置为 True。
    """

    name = "proxynova"
    url = "https://www.proxynova.com/proxy-server-list/"
    enabled = False

    def fetch(self):
        try:
            r = WebRequest().get(self.url, timeout=10, retry_time=1)
            tree = r.tree
            if tree is None:
                return

            proxies = []
            for tr in tree.xpath("//*[@id='tbl_proxy_list']//tr"):
                script = "".join(tr.xpath("./td[1]//script/text()")).strip()
                ip = _extractIpFromScript(script)
                if not ip:
                    # 兜底: 第一列直接是纯文本 IP
                    match = _PROXY_RE.search("".join(tr.xpath("./td[1]//text()")))
                    ip = match.group(0) if match else None

                port_match = re.search(r'\d{2,5}', "".join(tr.xpath("./td[2]//text()")))
                port = port_match.group(0) if port_match else ''
                if not ip or not port:
                    continue

                # td[3] 为代理类型, 只保留 HTTP/HTTPS
                proxy_type = "".join(tr.xpath("./td[3]//text()")).strip().lower()
                if 'socks' in proxy_type:
                    continue

                proxies.append("%s:%s" % (ip, port))

            for proxy in self.yieldUniqueProxies(proxies):
                yield proxy
        except Exception as e:
            logger.error("ProxyFetch - %s: %s" % (self.name, e))


if __name__ == '__main__':
    for proxy in ProxyNovaFetcher().fetch():
        print(proxy)
