# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
from time import sleep

from lxml import etree

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def _parse_proxies_from_text(text):
        if not text:
            return []
        proxy_pattern = re.compile(r'(?<![\d.])(\d{1,3}(?:\.\d{1,3}){3})(?:\s*:\s*|\s+)(\d{2,5})(?!\d)')
        return ["%s:%s" % proxy for proxy in proxy_pattern.findall(text)]

    @staticmethod
    def _parse_proxies_from_json(data):
        proxies = []
        if isinstance(data, dict):
            proxy = data.get("proxy") or data.get("addr") or data.get("address")
            if proxy:
                proxies.extend(ProxyFetcher._parse_proxies_from_text(str(proxy)))

            ip = data.get("ip") or data.get("host") or data.get("server")
            port = data.get("port")
            if ip and port:
                proxies.append("%s:%s" % (ip, port))

            parsed_keys = {"proxy", "addr", "address", "ip", "host", "server", "port"}
            for key, value in data.items():
                if key in parsed_keys:
                    continue
                proxies.extend(ProxyFetcher._parse_proxies_from_json(value))
        elif isinstance(data, list):
            for item in data:
                proxies.extend(ProxyFetcher._parse_proxies_from_json(item))
        elif isinstance(data, str):
            proxies.extend(ProxyFetcher._parse_proxies_from_text(data))
        return proxies

    @staticmethod
    def _parse_proxies_from_tree(tree):
        proxies = []
        if tree is None:
            return proxies
        for tr in tree.xpath("//tr"):
            cells = [" ".join(td.xpath(".//text()")).strip() for td in tr.xpath("./td")]
            if len(cells) < 2:
                continue
            ip = ""
            port = ""
            for cell in cells:
                ip_match = re.search(r'\d{1,3}(?:\.\d{1,3}){3}', cell)
                port_match = re.search(r'\b\d{2,5}\b', cell)
                if ip_match and not ip:
                    ip = ip_match.group()
                    continue
                if port_match and not port:
                    port = port_match.group()
            if ip and port:
                proxies.append("%s:%s" % (ip, port))
        return proxies

    @staticmethod
    def _yield_unique_proxies(proxies):
        seen = set()
        for proxy in proxies:
            if proxy not in seen:
                seen.add(proxy)
                yield proxy

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        start_url = "https://www.zdaye.com/free/"
        html_tree = WebRequest().get(start_url, verify=False).tree
        latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
        from datetime import datetime
        interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 300:  # 只采集5分钟内的更新
            target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                sleep(5)

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/"
        resp = WebRequest().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy04():
        """ FreeProxyList https://www.freeproxylists.net/zh/ """
        url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
        tree = WebRequest().get(url, verify=False).tree
        from urllib import parse

        def parse_ip(input_str):
            html_str = parse.unquote(input_str)
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
            return ips[0] if ips else None

        for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
            ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
            port = "".join(tr.xpath('./td[2]/text()')).strip()
            if ip:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy05(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """ 冰凌代理 https://www.binglx.cn """
        url = "https://www.binglx.cn/?page=1"
        try:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy07():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        request = WebRequest()
        ti_url = "https://ip.ihuan.me/ti.html"
        tqdl_url = "https://ip.ihuan.me/tqdl.html"
        ti_resp = request.get(ti_url, timeout=10, verify=False)
        form_data = {}
        if ti_resp.tree is not None:
            for input_tag in ti_resp.tree.xpath("//form//input[@name]"):
                name = "".join(input_tag.xpath("./@name")).strip()
                value = "".join(input_tag.xpath("./@value")).strip()
                if name:
                    form_data[name] = value

        key = form_data.get("key")
        if not key:
            key_match = re.search(r'name=["\']key["\'][^>]*value=["\']([^"\']+)', ti_resp.text)
            if not key_match:
                key_match = re.search(r'key["\']?\s*[:=]\s*["\']([0-9a-f]{16,})', ti_resp.text)
            key = key_match.group(1) if key_match else ""

        if not key:
            return

        header = {
            "Origin": "https://ip.ihuan.me",
            "Referer": ti_url,
        }
        data = form_data.copy()
        data.update({
            "num": "2000",
            "port": "",
            "kill_port": "",
            "address": "",
            "kill_address": "",
            "anonymity": "",
            "type": "",
            "post": "",
            "sort": "1",
            "key": key,
        })
        r = request.post(tqdl_url, header=header, data=data, timeout=10, verify=False)
        proxies = ProxyFetcher._parse_proxies_from_tree(r.tree)
        proxies.extend(ProxyFetcher._parse_proxies_from_text(r.text))
        for proxy in ProxyFetcher._yield_unique_proxies(proxies):
            yield proxy

    @staticmethod
    def freeProxy09(page_count=1):
        """ 免费代理库 """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def freeProxy10():
        """ 89免费代理 """
        r = WebRequest().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def freeProxy11():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy12():
        """ 谷德代理 https://www.goodips.com/ """
        url = "https://www.goodips.com/"
        tree = WebRequest().get(url, verify=False).tree
        for item in tree.xpath("//div[@class='table-list']"):
            ip = "".join(item.xpath("./ul/li[1]/text()")).strip()
            port = "".join(item.xpath("./ul/li[2]/text()")).strip()
            if ip and port:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy13():
        """ FreeVPNNode 中国代理 https://cn.freevpnnode.com/free-proxy-for-china/ """
        # url = "https://cn.freevpnnode.com/free-proxy-for-china/"
        url = "https://cn.freevpnnode.com/free-proxy/"
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        proxies = ProxyFetcher._parse_proxies_from_tree(r.tree)
        proxies.extend(ProxyFetcher._parse_proxies_from_text(r.text))
        for proxy in ProxyFetcher._yield_unique_proxies(proxies):
            yield proxy

    @staticmethod
    def freeProxy14():
        """ SCDN 代理接口 """
        # url = "https://proxy.scdn.io/get_proxies.php?protocol=&country=%E4%B8%AD%E5%9B%BD&per_page=100&page=1"
        url = "https://proxy.scdn.io/get_proxies.php?protocol=&country=&per_page=100&page=1"
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        try:
            data = r.json
            proxies = []
            table_html = data.get("table_html") if isinstance(data, dict) else ""
            if table_html:
                tree = etree.HTML("<table>%s</table>" % table_html)
                proxies.extend(ProxyFetcher._parse_proxies_from_tree(tree))

            if not proxies:
                proxies = ProxyFetcher._parse_proxies_from_json(data)
            if not proxies:
                proxies = ProxyFetcher._parse_proxies_from_text(r.text)
            for proxy in ProxyFetcher._yield_unique_proxies(proxies):
                yield proxy
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy15():
        """ Geonode Free Proxy 中国代理 https://geonode.com/free-proxy-list/ """
        # url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&country=CN"
        url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
        r = WebRequest().get(url, timeout=5, retry_time=1, verify=False)
        try:
            proxies = ProxyFetcher._parse_proxies_from_json(r.json)
            if not proxies:
                proxies = ProxyFetcher._parse_proxies_from_text(r.text)
            for proxy in ProxyFetcher._yield_unique_proxies(proxies):
                yield proxy
        except Exception as e:
            print(e)

    # @staticmethod
    # def wallProxy01():
    #     """
    #     PzzQz https://pzzqz.com/
    #     """
    #     from requests import Session
    #     from lxml import etree
    #     session = Session()
    #     try:
    #         index_resp = session.get("https://pzzqz.com/", timeout=20, verify=False).text
    #         x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', index_resp)
    #         if x_csrf_token:
    #             data = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
    #             proxy_resp = session.post("https://pzzqz.com/", verify=False,
    #                                       headers={"X-CSRFToken": x_csrf_token[0]}, json=data).json()
    #             tree = etree.HTML(proxy_resp["proxy_html"])
    #             for tr in tree.xpath("//tr"):
    #                 ip = "".join(tr.xpath("./td[1]/text()"))
    #                 port = "".join(tr.xpath("./td[2]/text()"))
    #                 yield "%s:%s" % (ip, port)
    #     except Exception as e:
    #         print(e)

    # @staticmethod
    # def freeProxy10():
    #     """
    #     墙外网站 cn-proxy
    #     :return:
    #     """
    #     urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    # @staticmethod
    # def freeProxy11():
    #     """
    #     https://proxy-list.org/english/index.php
    #     :return:
    #     """
    #     urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
    #     request = WebRequest()
    #     import base64
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
    #         for proxy in proxies:
    #             yield base64.b64decode(proxy).decode()

    # @staticmethod
    # def freeProxy12():
    #     urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy12():
        print(_)

# http://nntime.com/proxy-list-01.htm
