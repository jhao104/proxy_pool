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

import re, json, os, subprocess, time
from time import sleep
from fetcher.testVmess import testVmess
from util.webRequest import WebRequest
from server2user.logout import logout


def telnet(host, port)->bool:
    """
    测试代理端口是否通
    """
    import telnetlib
    try:
        telnetlib.Telnet(str(host), port=int(port), timeout=1)
        logout("proxyFetcher", f"telnet--{str(host)}:{str(port)}-- connecting successfully ...")
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
        url_list = [
            'https://fq.lonxin.net/clash/proxies',
            'https://sspool.herokuapp.com/clash/proxies',
            'https://free886.herokuapp.com/clash/proxies',
            'https://proxypoolss.fly.dev/clash/proxies?type=all',
            'https://proxy.yugogo.xyz/clash/proxies',
            'https://hellopool.herokuapp.com/clash/proxies',
            'http://www.fuckgfw.tk/clash/proxies',
            'https://dailici.herokuapp.com/clash/proxies',
            'https://origamiboy.herokuapp.com/clash/proxies',
            'https://free.dswang.ga/clash/proxies',
            'https://proxypoolss.fly.dev/clash/proxies',
            'https://us-proxypool.herokuapp.com/clash/proxies',
            'https://proxies.bihai.cf/clash/proxies',
            'http://42.194.196.226/clash/proxies',
            'https://klausvpn.posyao.com/clash/proxies',
            'https://gfwglass.tk/clash/proxies',
            'https://klausvpn.posyao.com/clash/proxies?type=vmess',
            'http://clash.3wking.com:12580/clash/proxies',
            'https://proxypool.ednovas.xyz/clash/proxies',
            'https://ss.dswang.ga:8443/clash/proxies',
            'http://guobang.herokuapp.com/clash/proxies',
            'https://eu-proxypool.herokuapp.com/clash/proxies',
            'https://hk.xhrzg2017.xyz/clash/proxies',
            'http://213.188.195.234/clash/proxies'
        ]
        for url in url_list:
            html_r = WebRequest().get(url).text
            # 打印当前请求页面
            logout("proxyFetcher", "="*20 + " " + url + " " + "="*20)

            try:
                # 分割每一行为一个代理
                html_r = html_r.split('\n')

                for line in html_r:
                    try:
                        # 代理提取并转为dict格式
                        proxy = json.loads(line[2:])

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
                        logout("proxyFetcher", f"网页解析-{line}-失败ERROR-{e}")
                        pass

            except Exception as e:
                logout("proxyFetcher", f"网页请求失败ERROR-{e}")

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
                logout("proxyFetcher", f"网页解析-{line}-失败ERROR-{e}")
                pass

