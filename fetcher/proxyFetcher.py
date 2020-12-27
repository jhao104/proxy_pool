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
from time import sleep
from lxml import etree

from util.webRequest import WebRequest
proxies = {
    "http": "http://127.0.0.1:54321",
    "https": "http://127.0.0.1:54321"
}


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        :return:
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        key = 'ABCDEFGHIZ'
        for url in url_list:
            html_tree = WebRequest().get(url).tree
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    ip = ul.xpath('./span[1]/li/text()')[0]
                    classnames = ul.xpath('./span[2]/li/attribute::class')[0]
                    classname = classnames.split(' ')[1]
                    port_sum = 0
                    for c in classname:
                        port_sum *= 10
                        port_sum += key.index(c)
                    port = port_sum >> 3
                    yield '{}:{}'.format(ip, port)
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
        proxies = re.findall(
            r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5})', resp.text)
        for proxy in proxies:
            yield proxy

    # @staticmethod
    # def freeProxy03(page_count=1):
    #     """
    #     西刺代理 http://www.xicidaili.com  网站已关闭
    #     :return:
    #     """
    #     url_list = [
    #         'http://www.xicidaili.com/nn/',  # 高匿
    #         'http://www.xicidaili.com/nt/',  # 透明
    #     ]
    #     for each_url in url_list:
    #         for i in range(1, page_count + 1):
    #             page_url = each_url + str(i)
    #             tree = WebRequest().get(page_url).tree
    #             proxy_list = tree.xpath(
    #                 './/table[@id="ip_list"]//tr[position()>1]')
    #             for proxy in proxy_list:
    #                 try:
    #                     yield ':'.join(proxy.xpath('./td/text()')[0:2])
    #                 except Exception as e:
    #                     pass

    @staticmethod
    def freeProxy04():
        """
        全网代理 http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = WebRequest().get(url).tree
        proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """

        # port是class属性值加密得到
        def _parse_port(port_element):
            port_list = []
            for letter in port_element:
                port_list.append(str("ABCDEFGHIZ".find(letter)))
            _port = "".join(port_list)
            return int(_port) >> 0x3

        for each_proxy in proxy_list:
            try:
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port_str = each_proxy.xpath(
                    ".//span[contains(@class, 'port')]/@class")[0].split()[-1]
                port = _parse_port(port_str.strip())
                yield '{}:{}'.format(ip_addr, int(port))
            except Exception:
                pass

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
    def freeProxy07():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        urls = ['http://www.ip3366.net/free/?stype=1',
                "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """
        IP海 http://www.iphai.com/free/ng
        :return:
        """
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                                 r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """
        http://ip.jiangxianli.com/?page=
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
        urls = ['http://www.xiladaili.com/putong/',
                "http://www.xiladaili.com/gaoni/",
                "http://www.xiladaili.com/http/",
                "http://www.xiladaili.com/https/"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy15():
        """
        http://www.kxdaili.com/
        开心代理(OK)
        :return:
        """
        urls = [
            'http://www.kxdaili.com/dailiip/%s/%s.html#ip' % (i, j) for i in range(1, 3) for j in range(1, 11)
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            html = r.text.replace('\r\n', '').replace(
                ' ', '').replace('</td><td>', ':')
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy16():
        """
        http://www.mrhinkydink.com/

        :return:
        """
        urls = [
            'http://www.mrhinkydink.com/proxies.htm'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            html = r.text.replace('\n', '').replace(' ', '').replace(
                '<sup>*</sup>', '').replace('<sup>&dagger;</sup>', '').replace('</td><td>', ':')
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy17():
        """
        http://ab57.ru/

        :return:
        """
        urls = [
            'http://ab57.ru/downloads/proxyold.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy18():
        """
        http://proxylists.net/

        :return:
        """
        urls = [
            'http://www.proxylists.net/http_highanon.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy19():
        """
        http://my-proxy.com/
        vpn needed
        :return:
        """
        urls = [
            'https://www.my-proxy.com/free-elite-proxy.html',
            'https://www.my-proxy.com/free-anonymous-proxy.html',
            'https://www.my-proxy.com/free-socks-4-proxy.html',
            'https://www.my-proxy.com/free-socks-5-proxy.html'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy20():
        """
        https://www.us-proxy.org/
        vpn needed
        :return:
        """
        urls = [
            'https://www.us-proxy.org/'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy21():
        """
        https://www.socks-proxy.net/
        vpn needed
        :return:
        """
        urls = [
            'https://www.socks-proxy.net/',
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy22():
        """
        https://www.sslproxies.org/
        vpn needed
        :return:
        """
        urls = [
            'https://www.sslproxies.org/',
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy23():
        """
        https://www.atomintersoft.com/
        
        :return:
        """
        urls = [
            'http://www.atomintersoft.com/high_anonymity_elite_proxy_list',
            'http://www.atomintersoft.com/anonymous_proxy_list',
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy24():
        """
        https://www.rmccurdy.com/
        
        :return:
        """
        urls = [
            'https://www.rmccurdy.com/.scripts/proxy/good.txt'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy25():
        """
        https://proxydb.net/
        TODO: ajax support (recaptcha???)
        :return:
        """
        urls = [
            'http://proxydb.net/?offset=%s' % (15 * i) for i in range(20)
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy26():
        """
        https://cool-proxy.net/
        
        :return:
        """
        urls = [
            'http://cool-proxy.net/proxies.json'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxy_json = r.json()
            ips = []
            for a in proxy_json:
                ips += [a.get('ip') + ':' + str(a.get('port'))]
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy27():
        """
        https://www.freeproxy.world/
        
        :return:
        """
        urls = [
            'https://www.freeproxy.world/?type=&anonymity=&country=&speed=&port=&page=%s' % i for i in range(1, 7)
        ]
        for url in urls:
            # print(url)
            r = WebRequest().get(url, timeout=10)
            html = etree.HTML(r.text.replace('\n', '').replace('<tr></tr>', ''))
            infos = html.xpath('//tbody/tr')
            ips = []
            for info in infos:
                if len(info.getchildren()) < 2:
                    continue
                proxy_ip = info.cssselect('.show-ip-div')[0].text
                proxy_port = info.cssselect('a')[0].text
                ips.append(proxy_ip + ':' + proxy_port)
            for ip in ips:
                yield ip.strip()
            sleep(1)

    @staticmethod
    def freeProxy28():
        """
        http://cn-proxy.com/
        vpn needed
        :return:
        """
        urls = [
            'http://cn-proxy.com/',
            'http://cn-proxy.com/archives/218'
        ]
        proxies={
            "http": "socks5://127.0.0.1:54321",
            "https": "socks5://127.0.0.1:54321"
            }
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            html = r.text.replace('</td>\n<td>', ':')
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy29():
        """
        http://free-proxy-list.net/
        vpn needed
        :return:
        """
        urls = [
            'https://free-proxy-list.net/',
            'https://free-proxy-list.net/uk-proxy.html',
            'https://free-proxy-list.net/anonymous-proxy.html',
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies, verify=True)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy30():
        """
        http://www.xroxy.com/
        vpn needed
        :return:
        """
        urls = [
            'http://www.xroxy.com/proxylist.php?port=&type=&ssl=&country=&latency=&reliability=&'
                     'sort=reliability&desc=true&pnum=%s#table' % i for i in range(20)
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            ips = list()
            html = r.tree
            infos = list()
            for x in html.xpath('//tr'):
                # print(dir(x))
                infos += x.cssselect('.row1') + x.cssselect('.row0')
            # print(infos)
            for info in infos:
                proxy_ip = info.cssselect('a')[0].text.replace('\n', '').replace('\r', '')
                proxy_port = info.cssselect('a')[1].text
                proxy_type = info.cssselect('a')[2].text
                ips.append(proxy_ip + ':' + proxy_port)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy31():
        """
        http://list.proxylistplus.com/
        vpn needed
        :return:
        """
        urls = [
            'http://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1',
            'http://list.proxylistplus.com/SSL-List-1'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            html = r.text.replace('\n', '').replace(' ', '').replace('</td><td>', ':')
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy32():
        """
        http://cnproxy.com/
        vpn needed
        :return:
        """
        urls = ['http://www.cnproxy.com/proxy%s.html' % i for i in range(1, 11)] + ['http://www.cnproxy.com/proxyedu%s.html' % i for i in range(1, 3)]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            text = r.text.replace('\n', '')
            
            # 端口字典
            port_dict = dict()
            t = re.findall(r'\w="\d', text, re.M|re.I)
            for d in t:
                port_dict[d.split('="')[0]] = d.split('="')[1]
            
            html = r.text.replace('<SCRIPT type=text/javascript>document.write("', '').replace('"+', '').replace('+', '').replace(')', '').replace('\n', '')
            html = etree.HTML(html)
            ips = list()
            infos = html.xpath('//tr')[2:]
            for info in infos:
                info_str = info.text
                proxy_detail = info.cssselect('td')[0].text
                for d in port_dict:
                    proxy_detail = proxy_detail.replace(d, port_dict[d])
                ips.append(proxy_detail)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy33():
        """
        http://free-proxy.cz/
        vpn needed
        TIPS: IP会被封禁，会出现谷歌验证，有点麻烦
        :return:
        """
        import base64
        urls = ['http://free-proxy.cz/zh/proxylist/country/CN/all/uptime/all/%s' % i for i in range(1, 6)] + ['http://free-proxy.cz/en/proxylist/main/uptime/%s' % i for i in range(1, 6)]
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'http://free-proxy.cz/en/proxylist/main/4',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66',
               'cookie': 'fpxy_tmp_access=a7563-36df0-3c443;fp=246340c66c6383077720cfa27f12e2d1'
                }
        """
        fp:根据浏览器信息算出
        http://free-proxy.cz/js/fp.js?150 格式化后第85行 var r = i.x64hash128(a.join("~~~"), 31); r就是fp的值
        """
        for url in urls:
            print(url)
            r = WebRequest().get(url, timeout=10, proxies=proxies, header=headers)
            html = etree.HTML(r.text.replace('<script type="text/javascript">document.write(Base64.decode("', '').replace('"))</script>', ''))
            ips = list()
            infos = html.xpath('//*[@id="proxy_list"]/tbody')[0].cssselect('tr')
            for info in infos:
                if len(info.cssselect('td')) < 2:
                    continue
                ip = base64.b64decode(info.cssselect('td')[0].text).decode('ascii')
                port = info.cssselect('.fport')[0].text
                ips.append(ip + ':' + port)
            for ip in ips:
                yield ip.strip()
            # 睡一觉，免得太快了
            sleep(1)

    @staticmethod
    def freeProxy34():
        import base64
        """
        http://proxy-list.org/
        vpn needed
        :return:
        """
        urls = [
            'https://proxy-list.org/english/index.php?p=%s' % i for i in range(1, 11)
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            html = etree.HTML(r.text.replace('<script type="text/javascript">Proxy(\'', '').replace('\')</script>', ''))
            infos = html.xpath('//*[@id="proxy-table"]/div[2]/div')[0].xpath('ul')
            ips = list()
            for info in infos:
                ips.append(base64.b64decode(info.cssselect('li')[0].text).decode('ascii'))
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy35():
        """
        https://spys.one/en/
        vpn needed
        :return:
        """
        urls = [
            'https://spys.one/en/free-proxy-list/',
            'https://spys.one/en/https-ssl-proxy/',
            'https://spys.one/en/anonymous-proxy-list/',
            'https://spys.one/en/socks-proxy-list/',
            'https://spys.one/en/http-proxy-list/'
        ]
        from fetcher.parse.spys import ParseSpys
        parse = ParseSpys()
        for url in urls:
            ips = parse.start(url)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy36():
        """
        https://www.proxy-list.download/

        :return:
        """
        urls = [
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://www.proxy-list.download/api/v1/get?type=https',
            # 'https://www.proxy-list.download/api/v1/get?type=socks4',
            # 'https://www.proxy-list.download/api/v1/get?type=socks5'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(
                r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            for ip in ips:
                yield ip.strip()
        sleep(1)

    @staticmethod
    def freeProxy37():
        """
        https://premproxy.com/
        vpn needed
        :return:
        """
        urls = [
            'https://premproxy.com/list/01.htm',
            'https://premproxy.com/socks-list/01.htm'
        ]
        from fetcher.parse.prem import ParsePrem
        parse = ParsePrem()
        for url in urls:
            ips = parse.start(url)
            if not ips:
                continue
            for ip in ips:
                yield ip.strip()
        sleep(1)

    @staticmethod
    def freeProxy38():
        """
        http://www.freeproxylists.net/
        vpn needed
        沙雕人机验证不能显示。。。
        :return:
        """
        urls = [
            'http://www.freeproxylists.net/zh/?c=&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50',
            'http://www.freeproxylists.net/zh/?u=50&page=2'
        ]
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': 'http://www.freeproxylists.net/zh/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66'
                }
        # proxies = {
        #     "http": "http://127.0.0.1:8888",
        #     "https": "http://127.0.0.1:8888"
        # }
        cookies = {}
        import urllib.parse
        for url in urls:
            r = WebRequest().get(url, header=headers, timeout=10, proxies=proxies, cookies=cookies)
            cookies = r.cookies.get_dict()
            # print(r.text)
            infos = etree.HTML(r.text.replace('<script type="text/javascript">IPDecode("', '').replace('")</script>', '')).cssselect('.DataGrid')[0].cssselect('tr')
            infos.pop(0)
            ips = []
            for info in infos:
                if len(info.cssselect('td')) < 3:
                    continue
                proxy_link = urllib.parse.unquote(info.cssselect('td')[0].text)
                proxy_ip = proxy_link[proxy_link.index('>') + 1: -4]
                proxy_port = info.cssselect('td')[1].text
                ips.append("{0}:{1}".format(proxy_ip, proxy_port))
                pass
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy39():
        """
        https://www.proxynova.com/
        vpn needed
        :return:
        """
        urls = [
            'https://www.proxynova.com/proxy-server-list/country-cn/',
            'https://www.proxynova.com/proxy-server-list/'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10, proxies=proxies)
            # print(r.text)
            infos = etree.HTML(r.text.replace('<script>document.write(\'', '').replace('\');</script>', '').replace('\n', '')).cssselect('tr')
            print(len(infos))
            infos.pop(0)
            ips = []
            for info in infos:
                if len(info.cssselect('td')) < 3:
                    continue
                proxy_ip = info.cssselect('td')[0].cssselect('abbr')[0].text.replace(' ', '')
                proxy_port = info.cssselect('td')[1].text.replace(' ', '')
                proxy = "{0}:{1}".format(proxy_ip, proxy_port)
                ips.append(proxy)
                pass
            for ip in ips:
                yield ip.strip()
        pass
