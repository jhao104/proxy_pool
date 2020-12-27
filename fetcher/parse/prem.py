import re
import requests
from lxml import etree
from requests.exceptions import ConnectionError


class ParsePrem():
    def __init__(self):
        super().__init__()
        self.js_id = None
        self.proxies = {
                "http": "http://127.0.0.1:54321",
                "https": "http://127.0.0.1:54321"
            }
        pass

    def get_index(self):
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'}
        
        try:
            rsp = requests.post(url=self.url, headers=header, proxies=self.proxies, timeout=10)
            if rsp.status_code == 200:
                html = rsp.text
                js = re.search('<script src="/js[-/](.*?).js"></script>', html)
                # print(js.group()[js.group().index('"/')+1:js.group().index('">')])
                # exit(-1)
                if js == None:
                    return False
                self.js_id = js.group()[js.group().index('"/')+1:js.group().index('">')]
                return html
            else:
                return False
        except ConnectionError:
            return False
        pass

    def get_jsinfo(self):
        header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'}
        
        try:
            url = 'https://premproxy.com' + self.js_id
            rsp = requests.post(url=url, headers=header, proxies=self.proxies, timeout=10)
            if rsp.status_code == 200:
                js = rsp.text.split('}(\'')[1]
                js = js.split(',\'')
                port_info = js[1].split('\'.')[0]
                js = js[0]
                
                return {'js': js, 'port_info': port_info}
            else:
                return False
        except ConnectionError:
            return False
        pass

    def get_htmlinfo(self, html):
        htmltree = etree.HTML(html)
        infos = htmltree.cssselect('.anon')
        # print(len(infos))
        # print(infos[0].cssselect('input')[0].values())
        # exit(-1)
        return infos
        pass
    
    def get_ips(self, infos, pass_dict):
        ips = []
        for info in infos:
            proxy = info.cssselect('input')[0].values()[2].split('|')
            ips.append("{0}:{1}".format(proxy[0], pass_dict[proxy[1]]))
        return ips
        pass
    def decrypt(self, js, port_info, m=62):
        js = str(js)
        j = {}
        i = 0
        js = js[js.index('{'):js.index('}')]
        arr = port_info.split("|")

        def baseN(num, b):
            return ((num == 0) and "0") or \
                (baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[num % b])
                
        for value in arr:
            j[baseN(i, m)] = value
            i = i + 1

        password = {}
        gps = js.split(';')
        for gp in gps:
            key = re.search(r'\'\.\w+\\\'', gp).group()[2:-2]
            value = re.search(r'\(\w+\)', gp).group()[1:-1]
            password[j[key]] = j[value]
            pass

        return password
        pass

    def start(self, url):
        self.url = url
        html = self.get_index()
        if html == False:
            return  False
        htmlinfo = self.get_htmlinfo(html)
        passinfo = self.get_jsinfo()
        if passinfo == False:
            return  False
        pass_arr = self.decrypt(js=passinfo['js'], port_info=passinfo['port_info'])
        ips = self.get_ips(infos=htmlinfo, pass_dict=pass_arr)
        return ips
        pass
    pass

if __name__ == "__main__":
    url = 'https://premproxy.com/socks-list/'
    parse = ParsePrem()
    print(parse.start(url))
    pass