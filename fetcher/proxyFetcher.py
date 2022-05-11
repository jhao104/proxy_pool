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
from helper.proxy import Proxy
from fetcher.testVmess import testVmess
from fetcher.testSs import testSs
from fetcher.prehandle_url import getProxyFromWeb
from handler.proxyHandler import ProxyHandler
from server2user.logout import logout


def telnet(host, port)->bool:
    """
    测试代理端口是否通
    """
    import telnetlib
    try:
        tel = telnetlib.Telnet(str(host), port=int(port), timeout=2)
        logout("proxyFetcher", f"telnet--{str(host)}:{str(port)}-- connecting pass ...")
        tel.close()
        return True
    except Exception as e:
        logout("proxyFetcher", f"telnet--{str(host)}:{str(port)}-- {e}")
        return False
    

class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        vmess代理池
        """
        # 操作redis数据库对象
        proxy_handler = ProxyHandler()

        # log可读性相关参数
        proxyNums, proxyList = getProxyFromWeb()
        proxyCount = 0
        proxyCount_successful = 0

        for proxy in proxyList:

            proxyCount += 1  # 代理计数器，提高log可读性

            try:
                # 代理提取并转为dict格式，并打印进度
                proxy = json.loads(proxy)
                logout("proxyFetcher", f"--正在处理-({proxyCount}/{proxyNums})-代理数据--")
                logout("proxyFetcher", f"--正在处理-({proxy})-代理数据--")

                # 代理过滤0：CN即中国代理,部分代理没有country字段则跳过
                try:
                    if proxy["country"][-2:] == "CN":
                        logout("proxyFetcher", f"--当前代理归属地为-<CN>-跳过--")
                        continue

                except Exception as e:
                    logout("proxyFetcher", f"--error-当前代理归属地为-<CN>-跳过--")
                    pass

                # 代理过滤1:只获取Vmess代理
                if proxy['type'] == 'vmess':

                    # 代理过滤1-1：pass1-telnet端口不通
                    if not telnet(proxy['server'], proxy['port']):
                        continue

                    # 代理过滤1-2：实际不可用
                    if not testVmess(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                        continue

                    # 可用代理计数器，提高log可读性
                    proxyCount_successful += 1
                    logout("proxyFetcher",
                           f"Successful--代理-{proxy['server']}:{proxy['port']}-测试通过-- 当前累计可用代理数量为-<{proxyCount_successful}>-")

                    # result:生成可用代理标准格式
                    UseProxy = '{"server": "%s",' \
                          '"port": "%s",' \
                          '"uuid": "%s",' \
                          '"alterId": "%s",' \
                          '"cipher": "%s",' \
                          '"network": "%s",' \
                          '"ws-path": "%s",' \
                          '"protocol": "vmess"}' % \
                          (proxy['server'],
                           proxy['port'],
                           proxy['uuid'],
                           proxy['alterId'],
                           proxy['cipher'],
                           proxy['network'],
                           # proxy['ws-path']
                           proxy.get('ws-path', None)
                           )

                    # 用途1：直接加入redis数据库
                    proxy = Proxy(UseProxy)
                    try:
                        """
                        返回int类型，1为插入成功，0为数据更新成功
                        """
                        flag = proxy_handler.put(proxy)
                        logout("proxyFetcher", f"--可用代理数据直插数据成功flag：{flag}--")
                    except Exception as e:
                        logout("proxyFetcher", f"--error-可用代理数据:{type(proxy.proxy)}-{proxy.proxy}-{type(proxy.to_json)}-{proxy.to_json}--直插数据发生错误：{e}--")

                    # 用途2：返回给服务框架
                    yield UseProxy

                # 代理过滤2:只获取Vmess代理
                elif proxy['type'] == 'ss':

                    # 代理过滤2-1：pass1-telnet端口不通
                    if not telnet(proxy['server'], proxy['port']):
                        continue

                    # 代理过滤2-2：实际可用性
                    if not testSs(proxy['server'], proxy['port'], proxy['password'], proxy['cipher']):
                        continue

                    # 可用代理计数器，提高log可读性
                    proxyCount_successful += 1
                    logout("proxyFetcher",
                           f"Successful--代理-{proxy['server']}:{proxy['port']}-测试通过-- 当前累计可用代理数量为-<{proxyCount_successful}>-")

                    # result:生成可用代理标准格式
                    UseProxy = '{"server": "%s",' \
                          '"port": "%s",' \
                          '"password": "%s",' \
                          '"cipher": "%s",' \
                          '"protocol": "ss"}' % \
                          (proxy['server'],
                           proxy['port'],
                           proxy['password'],
                           proxy['cipher']
                           )

                    # 用途1：直接加入redis数据库
                    proxy = Proxy(UseProxy)
                    try:
                        """
                        返回int类型，1为插入成功，0为数据更新成功
                        """
                        flag = proxy_handler.put(proxy)
                        logout("proxyFetcher", f"--可用代理数据直插数据成功flag：{flag}--")
                    except Exception as e:
                        logout("proxyFetcher", f"--error-可用代理数据:{type(proxy.proxy)}-{proxy.proxy}-{type(proxy.to_json)}-{proxy.to_json}--直插数据发生错误：{e}--")

                    # 用途2：返回给服务框架
                    yield UseProxy

                # 过滤其他类型代理
                else:
                    logout("proxyFetcher", f"--error-当前代理协议非<ss, vmess>-跳过--")
                    continue

            except Exception as e:
                logout("proxyFetcher", f"代理数据-{proxy}-测试失败ERROR-{e}")
                pass

    @staticmethod
    def freeProxy02():
        """
        vmess代理池
        """

        html_r = [
            {"name": "🇦🇺AU_66", "server": "cdn-cn.nekocloud.cn", "type": "vmess", "country": "🇦🇺AU", "port": 19057,\
             "uuid": "76cb50a4-9fd8-352e-99f4-a7bb5959b07b", "alterId": 0, "cipher": "auto", "network": "ws",\
             "ws-path": "/catnet", "http-opts": {}, "h2-opts": {}, "skip-cert-verify": True},
            {"name": "🇦🇺AU_67", "server": "cdn-cn.nekocloud.cn", "type": "vmess", "country": "🇦🇺AU", "port": 19046,\
             "uuid": "76cb50a4-9fd8-352e-99f4-a7bb5959b07b", "alterId": 0, "cipher": "auto", "network": "ws",\
             "ws-path": "/catnet", "http-opts": {}, "h2-opts": {}, "skip-cert-verify": True}
        ]

        for proxy in html_r:
            try:

                # 代理过滤1:只获取Vmess代理
                if not proxy['type'] == 'vmess':
                    continue

                # 代理过滤2：pass1-telnet端口不通
                if not telnet(proxy['server'], proxy['port']):
                    continue

                # 代理过滤3：实际不可用
                if not testVmess(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                    continue

                # yield "%s, %s, %s, %s" % (proxy['server'], proxy['port'], proxy['password'], proxy['cipher'])
                # yield '%s:%s' % (proxy['server'], proxy['port'])
                yield '{"server": "%s",' \
                      '"port": "%s",' \
                      '"uuid": "%s",' \
                      '"alterId": "%s",' \
                      '"cipher": "%s",' \
                      '"network": "%s",' \
                      '"ws-path": "%s"}' % \
                      (proxy['server'],
                       proxy['port'],
                       proxy['uuid'],
                       proxy['alterId'],
                       proxy['cipher'],
                       proxy['network'],
                       # proxy['ws-path']
                       proxy.get('ws-path', None)
                       )
                # yield f"{proxy}"

            except Exception as e:
                logout("proxyFetcher", f"测试用-网页解析-{proxy}-失败ERROR-{e}")
                pass

