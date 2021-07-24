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
import requests
from time import sleep
from datetime import date, timedelta
import pandas as pd

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        米扑代理 https://proxy.mimvp.com/
        :return:
        """
        url_list = [
            'https://proxy.mimvp.com/freeopen',
            'https://proxy.mimvp.com/freeopen?proxy=in_tp'
        ]
        port_img_map = {'DMxMjg': '3128', 'Dgw': '80', 'DgwODA': '8080',
                        'DgwOA': '808', 'DgwMDA': '8000', 'Dg4ODg': '8888',
                        'DgwODE': '8081', 'Dk5OTk': '9999'}
        for url in url_list:
            html_tree = WebRequest().get(url).tree
            for tr in html_tree.xpath(".//table[@class='mimvp-tbl free-proxylist-tbl']/tbody/tr"):
                try:
                    ip = ''.join(tr.xpath('./td[2]/text()'))
                    port_img = ''.join(tr.xpath('./td[3]/img/@src')).split("port=")[-1]
                    port = port_img_map.get(port_img[14:].replace('O0O', ''))
                    if port:
                        yield '%s:%s' % (ip, port)
                except Exception as e:
                    print(e)

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        :return:
        """
        url = "http://www.66ip.cn/mo.php"

        resp = WebRequest().get(url, timeout=10)
        proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})', resp.text)
        for proxy in proxies:
            yield proxy

    @staticmethod
    def freeProxy03():
        """
        pzzqz https://pzzqz.com/
        """
        from requests import Session
        from lxml import etree
        session = Session()
        try:
            index_resp = session.get("https://pzzqz.com/", timeout=20, verify=False).text
            x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', index_resp)
            if x_csrf_token:
                data = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
                proxy_resp = session.post("https://pzzqz.com/", verify=False,
                                          headers={"X-CSRFToken": x_csrf_token[0]}, json=data).json()
                tree = etree.HTML(proxy_resp["proxy_html"])
                for tr in tree.xpath("//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()"))
                    port = "".join(tr.xpath("./td[2]/text()"))
                    yield "%s:%s" % (ip, port)
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy04():
        """
        神鸡代理 http://www.shenjidaili.com/
        :return:
        """
        url = "http://www.shenjidaili.com/product/open/"
        tree = WebRequest().get(url).tree
        for table in tree.xpath("//table[@class='table table-hover text-white text-center table-borderless']"):
            for tr in table.xpath("./tr")[1:]:
                proxy = ''.join(tr.xpath("./td[1]/text()"))
                yield proxy.strip()

    @staticmethod
    def freeProxy05(page_count=1):
        """
        快代理 https://www.kuaidaili.com
        """
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
    def freeProxy06(page=2):
        """
        极速代理 https://www.superfastip.com/
        :return:
        """
        url = "https://api.superfastip.com/ip/freeip?page={page}"
        for i in range(page):
            page_url = url.format(page=i + 1)
            try:
                resp_json = WebRequest().get(page_url).json
                for each in resp_json.get("freeips", []):
                    yield "%s:%s" % (each.get("ip", ""), each.get("port", ""))
            except Exception as e:
                print(e)

    @staticmethod
    def freeProxy07():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        urls = ['http://www.ip3366.net/free/?stype=1',
                "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """
        小幻代理 https://ip.ihuan.me/
        :return:
        """
        urls = [
            'https://ip.ihuan.me/address/5Lit5Zu9.html',
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>',
                                 r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """
        http://ip.jiangxianli.com/
        免费代理库
        :return:
        """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def freeProxy10():
        """
        墙外网站 cn-proxy
        :return:
        """
        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxy11():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()

    @staticmethod
    def freeProxy12():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxy13(max_page=2):
        """
        http://www.89ip.cn/index.html
        89免费代理
        :param max_page:
        :return:
        """
        base_url = 'http://www.89ip.cn/index_{}.html'
        for page in range(1, max_page + 1):
            url = base_url.format(page)
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxy14():
        """
        http://www.xiladaili.com/
        西拉代理
        :return:
        """
        urls = ['http://www.xiladaili.com/']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()
                
    @staticmethod
    def freeProxy14():
        """
        http://www.xiladaili.com/
        西拉代理
        :return:
        """
        urls = ['http://www.xiladaili.com/']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()
       
    @staticmethod
    def freeProxy15():  # 命名不和已有重复即可
        proxies = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt').text.split()
        for proxy in proxies:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy16():  # 命名不和已有重复即可
        ip_list=[]
        for day in range(0, 30, 1):
            dd=date.today()-timedelta(days=day)
            ip_url='https://webanetlabs.net/proxylist2021/spisok_proksi_na_'+dd.strftime("%d.%m.%Y")+'.html'
            source=requests.get(ip_url)
            if source.status_code==200:
                ip_list+=re.findall(r'[0-9]+(?:\.[0-9]+){3}:[0-9]+', source.text)
        for proxy in ip_list:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy17():  # 命名不和已有重复即可
        http_ips=requests.get('https://www.proxy-list.download/api/v1/get?type=http').text.split()
        https_ips=requests.get('https://www.proxy-list.download/api/v1/get?type=https').text.split()
        for proxy in http_ips+https_ips:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy18():  # 命名不和已有重复即可
        json_results=requests.get('https://proxylist.geonode.com/api/proxy-list?limit=4000&page=1&sort_by=lastChecked&sort_type=desc&protocols=https%2Csocks4%2Csocks5').json()
        ip_list=[s['ip']+':'+s['port'] for s in json_results['data']]
        for proxy in ip_list:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy19():  # 命名不和已有重复即可
        ip_list=[]
        for pg_num in range(1, 7):
            df_ips=pd.read_html(requests.get('https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-'+str(pg_num)).text)[2]
            ip_list+=[s[0]+':'+str(s[1]) for s in df_ips[['IP Address.1', 'Port']].values]
        for proxy in ip_list:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy20():  # 命名不和已有重复即可
        proxy_list=requests.get('https://api.proxyscrape.com/?request=displayproxies&proxytype=all').text.split()
        for proxy in proxy_list:
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy21():  # 命名不和已有重复即可
        proxy_list=requests.get('https://www.proxyscan.io/download?type=https').text.split()
        proxy_list+=requests.get('https://www.proxyscan.io/download?type=socks4').text.split()
        proxy_list+=requests.get('https://www.proxyscan.io/download?type=socks5').text.split()
        for proxy in set(proxy_list):
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
    @staticmethod
    def freeProxy22():  # 命名不和已有重复即可
        proxy_list=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://www.socks-proxy.net/').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        proxy_list+=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://www.sslproxies.org/').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        proxy_list+=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://free-proxy-list.net/').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        proxy_list+=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://www.us-proxy.org/').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        proxy_list+=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://free-proxy-list.net/uk-proxy.html').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        proxy_list+=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://www.sslproxies.org/').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        proxy_list+=[s[0]+':'+str(int(s[1])) for s in 
                    pd.read_html(requests.get('https://free-proxy-list.net/anonymous-proxy.html').text)[0][['IP Address', 'Port']].values 
                    if str(s[0])!='nan']
        for proxy in set(proxy_list):
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回
        
        
    @staticmethod
    def freeProxy23():  # 命名不和已有重复即可
        proxy_list=open('slow_rotate.txt').read().split()
        for proxy in set(proxy_list):
            yield proxy
        # 确保每个proxy都是 host:ip正确的格式返回

if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy13():
        print(_)
