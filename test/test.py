import os
# from qqwry import updateQQwry
# from qqwry import QQwry
import requests

from lxml import etree
import base64
# print("1.1.1.1:123".split(':'))
# if False == os.path.isfile("qqwry.dat"):
#     ret = updateQQwry("qqwry.dat")
#     print(ret)

# q = QQwry()
# q.load_file('qqwry.dat')
# area = q.lookup('182.150.123.72')
# print(" ".join(area))

# test = [1,4]
# a = True
# test.extend([1,3])
# print(len(test))
# print(test)

proxies = {
    "http": "socks5://127.0.0.1:54322",
    "https": "socks5://127.0.0.1:54322"
    }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'cookie': 'fp=246340c66c6383077720cfa27f12e2d1'
               }
r = requests.get("http://cn-proxy.com/", headers=headers, proxies=proxies)
print(r.status_code)
print(r.headers)