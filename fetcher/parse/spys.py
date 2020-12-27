import os
import re
import time
import requests
from lxml import etree
from requests.exceptions import ConnectionError


# ==================================================================== #

# 可以在线运行python的网站: https://repl.it/languages
# 依赖:
# requests==2.21.0
# You can run python from the website https://repl.it/languages
# requirements:
# requests==2.21.0

class ParseSpys():

    def __init__(self):
        super().__init__()
        # self.url = 'https://spys.one/en/socks-proxy-list/'

        # url = 'http://spys.one/en/http-proxy-list/'

        # url = 'http://spys.one/en/anonymous-proxy-list/'

        # 设置代理配置:
        # Proxy Information Settings:
        self.xx0 = None

        # xpp = '5' 对应网页上Per page的值,即500. 0:30, 1:50, 2:100, 3:200, 4:300, 5:500
        # xpp = '5' Set the Per page value to be 500. 0:30, 1:50, 2:100, 3:200, 4:300, 5:500
        self.xpp = '5'

        # xf1 = '4' 对应ANM的值,当前为HIA. 0:All, 1:ANM&HIA, 2:NOA, 3:ANM, 4:HIA
        # xf1 = '4' Set the ANM value to be HIA. 0:All, 1:ANM&HIA, 2:NOA, 3:ANM, 4:HIA
        self.xf1 = '0'

        # xf2 = '0' 对应SSL的值. 0:All, 1:SSL+, 2:SSL-
        # xf2 = '0' Set the SSL value to be All. 0:All, 1:SSL+, 2:SSL-
        self.xf2 = '0'

        # xf4 = '0' 对应Port的值. 0:All, 1:3128, 2:8080,3:80
        # xf4 = '0' Set the Port value to be All. 0:All, 1:3128, 2:8080,3:80
        self.xf4 = '0'

        # xf5 = '2' 对应Type的值. 0:All, 1:HTTP, 2:SOCKS
        # xf5 = '2' Set the Type value to be SOCKS. 0:All, 1:HTTP, 2:SOCKS
        self.xf5 = '0'

        # ==================================================================== #
        self.unchecked = []

        self.proxies = {
                "http": "http://127.0.0.1:54321",
                "https": "http://127.0.0.1:54321"
            }
        self.get_xx0()

    def get_xx0(self):
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'}
        try:
            rsp = requests.post(url='https://spys.one/en/free-proxy-list/', headers=header, proxies=self.proxies, timeout=10)
            if rsp.status_code == 200:
                self.xx0 = re.findall('<input type=\'hidden\' name=\'xx0\' value=\'(.*?)\'>', rsp.text)[0]
            else:
                return False
        except ConnectionError:
            return False
        pass

    # GET HTML [Per page|ANM|SSL|Port|Type]
    def get_index(self):
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'}
        data = {
            'xx0': self.xx0,
            'xpp': self.xpp,
            'xf1': self.xf1,
            'xf2': self.xf2,
            'xf4': self.xf4,
            'xf5': self.xf5
        }
        try:
            rsp = requests.post(url=self.url, headers=header, data=data, proxies=self.proxies, timeout=10)
            if rsp.status_code == 200:
                self.xx0 = re.findall('<input type=\'hidden\' name=\'xx0\' value=\'(.*?)\'>', rsp.text)[0]
                html = rsp.text
                return html
            else:
                return False
        except ConnectionError:
            return False

    def get_proxy_info(self, html):
        html = etree.HTML(html.replace('<script type="text/javascript">document.write("<font class=spy2>:<\/font>"+', ':').replace(')</script></font>', '</font>'))
        
        infos = html.xpath('//table[2]')[0]
        infos = infos.cssselect('.spy1x') + infos.cssselect('.spy1xx')
        infos.pop(0)
        return infos

    def parse_proxy_info(self, html, infos):
        port_word = re.findall('\+\(([a-z0-9^]+)\)+', html)
        # DECRYPT PORT VALUE
        port_passwd = {}
        portcode = re.findall('table><script type="text/javascript">(.*)</script>', html)
        if len(portcode) == 0:
            self.unchecked = []
            return False
        portcode = portcode[0].split(';')
        for i in portcode:
            ii = re.findall('\w+=\d+', i)
            for i in ii:
                kv = i.split('=')
                if len(kv[1]) == 1:
                    k = kv[0]
                    v = kv[1]
                    port_passwd[k] = v
                else:
                    pass
        # GET PROXY INFO
        for i in infos:
            proxy = i.cssselect('font')[0].text.split(':')
            
            proxies_info = {
                'ip': proxy[0],
                'port': proxy[1],
                # 'protocol': i[2]
            }
            port_word = re.findall('\((\w+)\^', proxies_info.get('port'))
            port_digital = ''
            for j in port_word:
                port_digital += port_passwd[j]
            test_it = '{0}:{1}'.format(proxies_info.get('ip'), port_digital)
            self.unchecked.append(test_it)


    def start(self, url):
        self.url = url
        html = self.get_index()
        if html:
            infos = self.get_proxy_info(html)
            self.parse_proxy_info(html, infos)
            return self.unchecked
        return []

if __name__ == "__main__":
    test = ParseSpys()
    test.start('https://spys.one/en/free-proxy-list/')
    pass