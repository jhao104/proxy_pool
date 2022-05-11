import requests, json, time
from fetcher.testVmess import testVmess2
from fetcher.testSs import testSs2
from db import redisApi
from server2user.logout import logout
from handler.proxyHandler import ProxyHandler
from helper.proxy import Proxy


class ProxyRecheck():
    """
    代理管理器，负责该服务与代理池服务交互
    """
    def __init__(self):
        """
        更新代理池的数据至本地，并巡查当前代理列表的代理是否可用
        :param unvalid: 可用的代理
        :param unvalid: 不可用的代理
        """
        self.db = redisApi.RedisClient()
        self.dbOperate = ProxyHandler()

        logout("proxyRecheck", "proxyRecheck启动初始化完成")

    def getproxy(self):
        """
        更新代理池的数据至本地，并巡查当前代理列表的代理是否可用
        :param unvalid: 可用的代理
        :param unvalid: 不可用的代理
        :return: message
        """
        # 从redis里取数据
        valid = self.db.list_get("valid")
        unvalid = self.db.list_get("unvalid")

        logout("proxyRecheck", "\n")
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入valid个数:{len(valid)}")
        logout("proxyRecheck", f"输入valid:{valid}")
        logout("proxyRecheck", f"输入unvalid个数:{len(unvalid)}")
        logout("proxyRecheck", f"输入unvalid:{unvalid}")

        # 1.从数据库里获取当前最新代理数据
        temp = []

        proxies = self.dbOperate.getAll()

        res = [_.to_json for _ in proxies]
        logout("proxyRecheck", f"本次从数据库里获取当前的最新数据--{res}")

        try:
            for proxy in res:
                print(proxy)
                # 将proxy的键值内容转换为dict类型
                proxy = json.loads(proxy)
                print(proxy)
                print(type(proxy))
                print(proxy['proxy'])
                print(type(proxy['proxy']))

                # 20220507临时测试
                # proxy = json.loads(proxy['proxy'][:-1] + "}")
                proxy = json.loads(proxy['proxy'])

                if proxy['protocol'] == 'vmess':
                    temp.append(
                        {
                            'server': proxy['server'],
                            'port': proxy['port'],
                            'uuid': proxy['uuid'],
                            'alterId': proxy['alterId'],
                            'cipher': proxy['cipher'],
                            'network': proxy['network'],
                            'ws-path': proxy.get('ws-path', None),
                            'protocol': proxy['protocol']
                        }
                    )

                elif proxy['protocol'] == 'ss':
                    temp.append(
                        {
                            "server": proxy["server"],
                            "port": proxy['port'],
                            "password": proxy['password'],
                            "cipher": proxy['cipher'],
                            "protocol": proxy['protocol']
                        }
                    )

                else:
                    pass

        except Exception as e:
            logout("proxyRecheck", f"getproxy-数据解析ERROR-{e}")

        # 2.移除已添加过的代理数据，添加可用的新代理

        # 提高log可读性
        proxyCount = 0
        proxyNums = len(valid)

        for new in temp:

            proxyCount += 1  # 代理计数器，提高log可读性
            logout("proxyRecheck", f"--正在处理-({proxyCount}/{proxyNums})-代理数据--")

            # a.排重
            if json.dumps(new) in valid:
                logout("proxyRecheck", f"跳过重复代理数据-<{type(new)}>-proxy:{new}")
                continue

            # b. 测试代理是否可用, 可用则添加至validList，不可用则添加至unvalid以便后续删除
            if new["protocol"] == "vmess":
                if testVmess2(new['server'], new['port'], new['uuid'], new['alterId'], new['cipher'], new['network'], new.get('ws-path', None)):
                    self.db.list_add("valid", new)
                elif testVmess2(new['server'], new['port'], new['uuid'], new['alterId'], new['cipher'], new['network'], new.get('ws-path', None)):
                    self.db.list_add("valid", new)
                else:
                    self.db.list_add("unvalid", new)
                    logout("proxyRecheck", f"该代理不可用已添加至删除列表-<{type(new)}>-proxy:{new}")

            elif new["protocol"] == "ss":
                if testSs2(new['server'], new['port'], new['password'], new['cipher']):
                    self.db.list_add("valid", new)
                elif testSs2(new['server'], new['port'], new['password'], new['cipher']):
                    self.db.list_add("valid", new)
                else:
                    self.db.list_add("unvalid", new)
                    logout("proxyRecheck", f"该代理不可用已添加至删除列表-<{type(new)}>-proxy:{new}")

            else:
                pass

        # 返回处理后的结果
        valid = self.db.list_get("valid")
        unvalid = self.db.list_get("unvalid")

        logout("proxyRecheck", "当次新增完成")
        logout("proxyRecheck", f"输入valid个数:{len(valid)}")
        logout("proxyRecheck", f"输入valid:{valid}")
        logout("proxyRecheck", f"输入unvalid个数:{len(unvalid)}")
        logout("proxyRecheck", f"输入unvalid:{unvalid}")
        logout("proxyRecheck", "="*30)

    def checkproxy(self):
        """
        巡检当前可用代理列表里的代理最新状态
        :param unvalid: 可用的代理
        :param unvalid: 不可用的代理
        :return: message
        """
        # 从redis里取数据
        valid = self.db.list_get("valid")
        unvalid = self.db.list_get("unvalid")

        logout("proxyRecheck", "\n")
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入valid个数:{len(valid)}")
        logout("proxyRecheck", f"输入valid:{valid}")
        logout("proxyRecheck", f"输入unvalid个数:{len(unvalid)}")
        logout("proxyRecheck", f"输入unvalid:{unvalid}")

        # 提高log可读性
        proxyCount = 0
        proxyNums = len(valid)

        try:

            for proxy in valid:

                proxyCount += 1  # 代理计数器，提高log可读性
                logout("proxyRecheck", f"--正在处理-({proxyCount}/{proxyNums})-代理数据--")

                logout("proxyRecheck", f"--proxy--{proxy}")
                # 转成dict
                proxy = json.loads(proxy)

                # 分协议检测
                if proxy['protocol'] == "vmess":
                    if testVmess2(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                        logout("proxyRecheck", f"--testVmess2--测试<1>次--Successful")
                    elif testVmess2(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                        logout("proxyRecheck", f"--testVmess2--测试<2>次--Successful")
                    elif testVmess2(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                        logout("proxyRecheck", f"--testVmess2--测试<3>次--Successful")
                    else:
                        self.db.list_del("valid", json.dumps(proxy))  # count-0，针对valid有效去重
                        self.db.list_add("unvalid", proxy)
                        logout("proxyRecheck", f"--加入删除列表--temp--{proxy}")

                elif proxy['protocol'] == "ss":
                    if testSs2(proxy['server'], proxy['port'], proxy['password'], proxy['cipher']):
                        logout("proxyRecheck", f"--testSs2--测试<1>次--Successful")
                    elif testSs2(proxy['server'], proxy['port'], proxy['password'], proxy['cipher']):
                        logout("proxyRecheck", f"--testSs2--测试<2>次--Successful")
                    elif testSs2(proxy['server'], proxy['port'], proxy['password'], proxy['cipher']):
                        logout("proxyRecheck", f"--testSs2--测试<3>次--Successful")
                    else:
                        self.db.list_del("valid", json.dumps(proxy))  # count-0，针对valid有效去重
                        self.db.list_add("unvalid", proxy)
                        logout("proxyRecheck", f"--加入删除列表--temp--{proxy}")

            logout("proxyRecheck", f"--巡检结束--")

            valid = self.db.list_get("valid")
            unvalid = self.db.list_get("unvalid")
            logout("proxyRecheck", f"--删完完成--validList--{valid}--unvalid--{unvalid}")

        except Exception as e:
            logout("proxyRecheck", f"error-checkproxy-{e}")

        # 返回处理后的结果
        valid = self.db.list_get("valid")
        unvalid = self.db.list_get("unvalid")
        logout("proxyRecheck", "当次巡检完成")
        logout("proxyRecheck", f"输入valid个数:{len(valid)}")
        logout("proxyRecheck", f"输入valid:{valid}")
        logout("proxyRecheck", f"输入unvalid个数:{len(unvalid)}")
        logout("proxyRecheck", f"输入unvalid:{unvalid}")
        logout("proxyRecheck", "="*30)

    def deletevalidproxy(self):
        """
        移除代理池中不可用的代理
        :param unvalid: 不可用的代理
        :return: message
        """
        # 从redis里取数据
        unvalid = self.db.list_get("unvalid")

        logout("proxyRecheck", "\n")
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入unvalid个数:{len(unvalid)}")
        logout("proxyRecheck", f"输入unvalid:{unvalid}")

        temp = []  # 待删除列表

        for proxy in unvalid:
            # 从redis读出来变成str，需要转dict
            proxy = json.loads(proxy)
            logout("proxyRecheck", f"即将删除代理{str(proxy)}")

            if proxy['protocol'] == "vmess":
                re_proxy = '{"server": "%s",' \
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

            elif proxy['protocol'] == "ss":
                re_proxy = '{"server": "%s",' \
                           '"port": "%s",' \
                           '"password": "%s",' \
                           '"cipher": "%s",' \
                           '"protocol": "ss"}' % \
                           (proxy['server'],
                            proxy['port'],
                            proxy['password'],
                            proxy['cipher']
                            )

            # # 20220507临时测试用
            # elif proxy['protocol'] == "ss":
            #     re_proxy = '{"server": "%s",' \
            #                '"port": "%s",' \
            #                '"password": "%s",' \
            #                '"cipher": "%s",' \
            #                '"protocol": "ss",' % \
            #                (proxy['server'],
            #                 proxy['port'],
            #                 proxy['password'],
            #                 proxy['cipher']
            #                 )

            else:
                continue

            # 向代理池数据库发送代理删除请求
            try:
                status = self.dbOperate.delete(Proxy(str(re_proxy)))
                logout("proxyRecheck", f"删除代理{Proxy(str(re_proxy))}请求结果--{status}")
                # 202205010 将代理池删除成功判定取消，发完删除请求，默认成功
                # if int(status) == 1:
                #     temp.append(proxy)
                temp.append(proxy)

            except Exception as e:
                logout("proxyRecheck", f"{e}")

        # 从失效代理列表中移除已经成功删除的代理数据
        for delproxy in temp:
            del_flag = self.db.list_del("unvalid", json.dumps(delproxy))  # count-0，针对unvalid有效去重
            print(f"{del_flag}--{delproxy}")

        # 返回处理后的结果
        unvalid = self.db.list_get("unvalid")
        logout("proxyRecheck", "移除不可用代理完成")
        logout("proxyRecheck", f"输入unvalid个数:{len(unvalid)}")
        logout("proxyRecheck", f"输入unvalid:{unvalid}")
        logout("proxyRecheck", "=" * 30)

    def run(self):
        """
        总循环
        """
        while True:

            # 从redis里取数据
            valid = self.db.list_get("valid")
            unvalid = self.db.list_get("unvalid")

            try:
                logout("proxyRecheck", "\n")
                logout("proxyRecheck", f"valid-id-{id(valid)}--unvailid-id-{id(unvalid)}")
                self.checkproxy()
                self.getproxy()
                self.deletevalidproxy()
                time.sleep(120)
            except Exception as e:
                logout("proxyRecheck", f"RECHECK模块错误{e}")
                time.sleep(60)


if __name__ == '__main__':

    PR = ProxyRecheck()
    PR.run()

