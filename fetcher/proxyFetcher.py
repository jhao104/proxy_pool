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

import json
import re
from time import sleep

from util.webRequest import WebRequest
from pyquery import PyQuery as pq


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        好像屏蔽了国外服务器,国内可以正常爬取.
        """
        start_url = "https://www.zdaye.com/dayProxy/{}/{}/{}.html"
        from datetime import datetime
        html_tree = WebRequest().get(start_url.format(datetime.now().year, datetime.now().month, 1), verify=False).tree
        latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
        interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 300:  # 只采集5分钟内的更新，当前7个小时更新一次
            target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                sleep(10)

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
    def freeProxy03(page_count=10):
        """ 开心代理 http://www.kxdaili.com/dailiip.html"""
        target_url = "http://www.kxdaili.com/dailiip/{}/{}.html"
        target_urls = []
        for tabIndex in range(2):
            for pageIndex in range(page_count):
                target_urls.append(target_url.format(tabIndex + 1, pageIndex + 1))

        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy05(page_count=10):
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
            sleep(10)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """ FateZero http://proxylist.fatezero.org/ """
        url = "http://proxylist.fatezero.org/proxy.list"
        try:
            resp_text = WebRequest().get(url).text
            for each in resp_text.split("\n"):
                json_info = json.loads(each)
                if json_info.get("country") == "CN":
                    yield "%s:%s" % (json_info.get("host", ""), json_info.get("port", ""))
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
            sleep(10)

    @staticmethod
    def freeProxy10():
        """
        89免费代理
        怀疑封国外请求,境外服务器爬取异常. 
        
        """
        url = "https://www.89ip.cn/{}.html"
        target_url = url.format('index_1')
        next_page = True
        while next_page:
            r = WebRequest().get(target_url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

            next_page = r.tree.xpath("//a[@class='layui-laypage-next']/@href")
            next_page = next_page[0].strip() if next_page else False
            target_url = url.format(next_page)
            sleep(10)

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
    def wingser01():
        """
        seo方法 crawler, https://proxy.seofangfa.com/
        """
        url = 'https://proxy.seofangfa.com/'
        html_tree = WebRequest().get(url, verify=False).tree
        for index, tr in enumerate(html_tree.xpath("//table//tr")):
            if index == 0:
                continue
            yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def wingser02():
        """
        小舒代理 crawler, http://www.xsdaili.cn/
        """
        url = 'http://www.xsdaili.cn/'
        base_url = "http://www.xsdaili.cn/dayProxy/ip/{page}.html"

        '''通过网站,获取最近10个日期的共享'''
        urls = []
        html = WebRequest().get(url, verify=False).tree
        doc = pq(html)
        title = doc(".title:eq(0) a").items()
        latest_page = 0
        for t in title:
            res = re.search(r"/(\d+)\.html", t.attr("href"))
            latest_page = int(res.group(1)) if res else 0
        if latest_page:
            urls = [base_url.format(page=page) for page in range(latest_page - 10, latest_page)]
        else:
            urls = []

        '''每个日期的网站,爬proxy'''
        for u in urls:
            h = WebRequest().get(u, verify=False).tree
            doc = pq(h)
            contents = doc('.cont').text()
            contents = contents.split("\n")
            for content in contents:
                yield content[:content.find("@")]



    @staticmethod
    def wingser03():
        """
        PzzQz https://pzzqz.com/
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
    def wingser04():
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
    def wingser05():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.wingser05():
        print(_)




# http://nntime.com/proxy-list-01.htm

