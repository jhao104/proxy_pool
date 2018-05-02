# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25:
-------------------------------------------------
"""
import re
import sys
import requests

try:
    from importlib import reload  # py3 实际不会实用，只是为了不显示语法错误
except:
    reload(sys)
    sys.setdefaultencoding('utf-8')

sys.path.append('..')

from Util.utilFunction import robustCrawl, getHtmlTree
from Util.WebRequest import WebRequest

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()

"""
    66ip.cn
    data5u.com
    xicidaili.com
    goubanjia.com
    xdaili.cn
    kuaidaili.com
    cn-proxy.com
    proxy-list.org
    www.mimiip.com to do
"""


class GetFreeProxy(object):
    """
    proxy getter
    """

    def __init__(self):
        pass

    @staticmethod
    def freeProxyFirst(page=10):
        """
        抓取无忧代理 http://www.data5u.com/
        几乎没有能用的
        :param page: 页数
        :return:
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    yield ':'.join(ul.xpath('.//li/text()')[0:2])
                except Exception as e:
                    print(e)

    @staticmethod
    def deprecatedFreeProxySecond(proxy_number=100):
        """
        抓取代理66 http://www.66ip.cn/
        :param proxy_number: 代理数量
        :return:
        """
        url = "http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(
            proxy_number)
        request = WebRequest()
        html = request.get(url).text
        for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
            yield proxy

    @staticmethod
    def freeProxySecond(area=33):
        """
        修改抓取代理66 http://www.66ip.cn/
        :param page:抓取代理页数，page=1北京代理页，page=2上海代理页......
        :return:
        """
        if area > 33:
            page = 33
        for area_index in range(1, area + 1):
            page_count = 5
            for i in range(1, page_count + 1):
                url = "http://www.66ip.cn/areaindex_{}/{}.html".format(area_index, i)
                html_tree = getHtmlTree(url)
                tr_list = html_tree.xpath("//*[@id='footer']/div/table/tr[position()>1]")
                if len(tr_list) == 0:
                    continue
                for tr in tr_list:
                    yield tr.xpath("./td[1]/text()")[0] + ":" + tr.xpath("./td[2]/text()")[0]
                break

    '''
    不能用了
    @staticmethod
    def freeProxyThird(days=1):
        """
        抓取ip181 http://www.ip181.com/
        :param days:
        :return:
        """
        url = 'http://www.ip181.com/'
        html_tree = getHtmlTree(url)
        try:
            tr_list = html_tree.xpath('//tr')[1:]
            for tr in tr_list:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            pass
    '''

    @staticmethod
    def freeProxyFourth(page_count=2):
        """
        抓取西刺代理 http://api.xicidaili.com/free2016.txt
        :return:
        """
        url_list = [
            'http://www.xicidaili.com/nn/',  # 高匿
            'http://www.xicidaili.com/nt/',  # 透明
        ]
        for each_url in url_list:
            for i in range(1, page_count + 1):
                page_url = each_url + str(i)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                for proxy in proxy_list:
                    try:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass

    @staticmethod
    def freeProxyFifth():
        """
        抓取guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = getHtmlTree(url)
        proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]
                yield '{}:{}'.format(ip_addr, port)
            except Exception as e:
                pass

    @staticmethod
    def freeProxySixth():
        """
        抓取讯代理免费proxy http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10
        :return:
        """
        url = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
        request = WebRequest()
        try:
            res = request.get(url).json()
            for row in res['RESULT']['rows']:
                yield '{}:{}'.format(row['ip'], row['port'])
        except Exception as e:
            pass

    @staticmethod
    def freeProxySeventh():
        """
        快代理免费https://www.kuaidaili.com/free/inha/1/
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/{page}/',
            'https://www.kuaidaili.com/free/intr/{page}/'
        ]
        for url in url_list:
            for page in range(1, 5):
                page_url = url.format(page=page)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table//tr')
                for tr in proxy_list[1:]:
                    yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxyEight():
        """
        秘密代理IP网站http://www.mimiip.com
        """
        url_gngao = ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 10)]  # 国内高匿
        url_gnpu = ['http://www.mimiip.com/gnpu/%s' % n for n in range(1, 10)]  # 国内普匿
        url_gntou = ['http://www.mimiip.com/gntou/%s' % n for n in range(1, 10)]  # 国内透明
        url_list = url_gngao + url_gnpu + url_gntou

        request = WebRequest()
        for url in url_list:
            r = request.get(url, use_proxy=True)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W].*<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)


    @staticmethod
    def freeProxyNinth():
        """
        coderBusy
        https://proxy.coderbusy.com/
        :return:
        """
        urls = ['https://proxy.coderbusy.com/classical/country/cn.aspx?page=1']
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall('data-ip="(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})".+?>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)


    @staticmethod
    def freeProxyTen():
        urls = ['http://www.ip3366.net/free/']
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)


    @staticmethod
    def freeProxyEleven():
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)


    @staticmethod
    def freeProxyWallFirst():
        """
        墙外网站 cn-proxy
        并没有被墙
        :return:
        """
        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyWallSecond():
        '''
        并没有被墙
        :return:
        '''
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()


    @staticmethod
    def freeProxyWallThird():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)


import threading

lock = threading.Lock()
success = 0
total = 0


def test_once(proxy):
    ip_port = proxy.split(":")
    ip = ip_port[0]
    port = ip_port[1]
    import requests

    req_url = "http://www.baidu.com"
    proxies = {
        "http": "http://%s:%s" % (ip, port),
        "https": "https://%s:%s" % (ip, port)
    }

    global total

    try:
        response = requests.get(req_url, proxies=proxies, timeout=4)
        if response.status_code != 200:
            print("unknow error, status code:" + str(response.status_code))
            lock.acquire()
            total += 1
            lock.release()
            return 0
        print("success")
        global success
        lock.acquire()
        success += 1
        total += 1
        lock.release()
        return 1
    except requests.exceptions.Timeout:
        print("timeout")
    except requests.exceptions.ConnectionError:
        print("poxy unusable")
    except Exception:
        print("request error")

    lock.acquire()
    total += 1
    lock.release()
    return 0


def test_batch(iterator):
    global success
    global total

    for proxy in iterator:
        t = threading.Thread(target=test_once, args=(proxy,))
        t.start()
        t.join()

    print("success:" + str(success) + "\ttotal:" + str(total))


if __name__ == '__main__':
    gg = GetFreeProxy()

    # test_batch(gg.freeProxyFirst())

    # test_batch(gg.freeProxySecond())

    # test_batch(gg.freeProxyFourth())

    # test_batch(gg.freeProxyFifth())

    # test_batch(gg.freeProxySixth())

    # test_batch(gg.freeProxySeventh())

    # test_batch(gg.freeProxyEight())

    # test_batch(gg.freeProxyNinth())

    # test_batch(gg.freeProxyTen())

    # test_batch(gg.freeProxyEleven())

    # test_batch(gg.freeProxyWallFirst())

    # test_batch(gg.freeProxyWallSecond())

    # test_batch(gg.freeProxyWallThird())
