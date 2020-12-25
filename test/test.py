import os
# from qqwry import updateQQwry
# from qqwry import QQwry
import requests

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
# exit(-1)

proxies = {
    "http": "http://113.238.142.208:3128",
    "https": "https://113.238.142.208:3128"
    }
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.8'}
r = requests.get("https://webvpn.cuit.edu.cn/por/login_auth.csp?apiversion=1", headers=headers, proxies=proxies)
v1 = "login auth success" in r.text

r = requests.get("http://jwc.cuit.edu.cn/", headers=headers, proxies=proxies)
v2 = "datedifference" in r.text
print("" + str(v1) + "|" + str(v2) + "|" + str(v1 or v2))