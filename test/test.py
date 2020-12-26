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
    "http": "http://49.89.86.40:4216",
    "https": "http://49.89.86.40:4216"
    }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8',
               'cookie': 'fp='
               }
r = requests.get("https://webvpn.cuit.edu.cn/por/login_auth.csp?apiversion=1'", headers=headers, proxies=proxies, timeout=2)
print(r.status_code)
print(r.headers)