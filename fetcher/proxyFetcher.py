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
import urllib
from datetime import datetime
from time import sleep
import urllib.parse

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        '''
        站大爷
        '''
        url = 'https://www.zdaye.com/free/'

        # 第一页
        r = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'<tr>\s*<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td>(\d+)</td>', r.text)
        yield from [':'.join(proxy) for proxy in proxies]
        
        # 后面几页
        pages = re.findall(r'\s+href=\"/free/(\d+)/\"', r.text)
        pages = list(dict.fromkeys(pages))
        for page in pages:
            page_url = urllib.parse.urljoin(url, page)
            sleep(5)
            r = WebRequest().get(page_url, timeout=10)
            proxies = re.findall(r'<tr>\s*<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>\s*<td>(\d+)</td>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/mo.php?sxb=&tqsl=100&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=http%3A%2F%2Fwww.66ip.cn%2F%3Fsxb%3D%26tqsl%3D100%26ports%255B%255D2%3D%26ktip%3D%26sxa%3D%26radio%3Dradio%26submit%3D%25CC%25E1%2B%2B%25C8%25A1"
        r = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', r.text)
        yield from proxies

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in urls:
            r = WebRequest().get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]
            
            more_urls = re.findall(r'<a\s+href=\"(/dailiip/\d+/\d+.html)\">\d+</a>', r.text)
            more_urls = [urllib.parse.urljoin(url, more_url) for more_url in more_urls]
            for more_url in more_urls:
                sleep(1)
                r = WebRequest().get(more_url)
                proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
                yield from [':'.join(proxy) for proxy in proxies]


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
        categories = ['inha', 'intr', 'fps']
        for category in categories:
            max_page = 1
            page = 1
            while page <= max_page:
                url = f'https://www.kuaidaili.com/free/{category}/{page}'
                sleep(5)
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(r'\"ip\":\s+\"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\",\s+\"last_check_time\":\s+\"[\d\-\s\:]+\",\s+\"port\"\:\s+\"(\d+)\"', r.text)
                yield from [':'.join(proxy) for proxy in proxies]
                
                total = re.findall(r'let\s+totalCount\s\=\s+[\'\"](\d+)[\'\"]', r.text)[0]
                max_page = min(int(total)/12, 10)
                page += 1

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
        stypes = ('1', '2')
        for stype in stypes:
            url = f'http://www.ip3366.net/free/?stype={stype}'
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)
            
            pages = re.findall(r'<a\s+href=\"\?stype=[12]&page=(\d+)\">\d+</a>', r.text)
            for page in pages:
                url = f'http://www.ip3366.net/free/?stype={stype}&page={page}'
                sleep(1)
                r = WebRequest().get(url, timeout=10)
                proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
                yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        now = datetime.now()
        url = f'https://ip.ihuan.me/today/{now.year}/{now.month:02}/{now.day:02}/{now.hour:02}.html'
        r = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)', r.text)
        yield from [':'.join(proxy) for proxy in proxies]

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
        urls = ['https://www.89ip.cn/']
        while True:
            try:
                url = urls.pop()
            except IndexError:
                break

            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            if not proxies:
                # 没了
                break

            yield from [':'.join(proxy) for proxy in proxies]

            # 下一页
            r = re.findall(r'<a\s+href=\"(index_\d+.html)\"\s+class=\"layui-laypage-next\"\s+data-page=\"\d+\">下一页</a>', r.text)
            if r:
                next_url = urllib.parse.urljoin(url, r[0])
                urls.append(next_url)
                sleep(1)


    @staticmethod
    def freeProxy11():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
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

    @staticmethod
    def freeProxy13():
        url = 'https://gh-proxy.com/https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.json'
        r = WebRequest().get(url, timeout=10)
        proxies = [f'{proxy["ip"]}:{proxy["port"]}' for proxy in  r.json]
        yield from proxies
    
    @staticmethod
    def freeProxy14():
        url = 'https://gh-proxy.com/https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'
        r = WebRequest().get(url, timeout=10)
        proxies = [proxy for proxy in r.text.split('\n') if proxy]
        yield from proxies
    
    @staticmethod
    def freeProxy15():
        url = 'https://sunny9577.github.io/proxy-scraper/proxies.json'
        r = WebRequest().get(url, timeout=10)
        proxies = [f'{proxy["ip"]}:{proxy["port"]}' for proxy in  r.json]
        yield from proxies
    
    @staticmethod
    def freeProxy16():
        urls = ['https://gh-proxy.com/https://raw.githubusercontent.com/zloi-user/hideip.me/main/https.txt', 'https://gh-proxy.com/https://raw.githubusercontent.com/zloi-user/hideip.me/main/http.txt']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = [':'.join(proxy.split(':')[:2]) for proxy in r.text.split('\n') if proxy]
            yield from proxies
    
    @staticmethod
    def freeProxy17():
        url = 'https://iproyal.com/free-proxy-list/?page=1&entries=100'
        
        while True:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</div><div class=\"flex items-center astro-lmapxigl\">(\d+)</div>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]
            
            next = r.tree.xpath('//a[text()="Next"]/@href')
            if next:
                url = urllib.parse.urljoin(url, next[0])
                sleep(5)
            else:
                break
    
    @staticmethod
    def freeProxy18():
        urls = ['http://pubproxy.com/api/proxy?limit=5&https=true', 'http://pubproxy.com/api/proxy?limit=5&https=false']
        proxies = set()
        for url in urls:
            for _ in range(10):
                sleep(1)
                r = WebRequest().get(url, timeout=10)
                for proxy in [proxy['ipPort'] for proxy in r.json['data']]:
                    if proxy in proxies:
                        continue
                    yield proxy
                    proxies.add(proxy)
    
    @staticmethod
    def freeProxy19():
        urls = ['https://freeproxylist.cc/servers/']
        while True:
            try:
                url = urls.pop()
            except IndexError:
                break

            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]

            r = re.findall(r'''<a\s+href='(https://freeproxylist\.cc/servers/\d+\.html)'>&raquo;</a></li>''', r.text)
            if r:
                urls.append(r[0])
                sleep(1)
    
    @staticmethod
    def freeProxy20():
        url = 'https://hasdata.com/free-proxy-list'
        r = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'<tr><td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d+)</td><td>HTTP', r.text)
        yield from [':'.join(proxy) for proxy in proxies]

    @staticmethod
    def freeProxy21():
        urls = ['https://www.freeproxy.world/?type=https&anonymity=&country=&speed=&port=&page=1', 'https://www.freeproxy.world/?type=http&anonymity=&country=&speed=&port=&page=1']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*</td>\s*<td>\s*<a href=\"/\?port=\d+\">(\d+)</a>', r.text)
            yield from [':'.join(proxy) for proxy in proxies]


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy01():
        print(_)

# http://nntime.com/proxy-list-01.htm
