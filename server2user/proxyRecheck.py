import requests, json, time
from fetcher.testVmess import testVmess2
import setting
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
        :param unvalidList: 可用的代理
        :param unvalidList: 不可用的代理
        """
        self.validList = []
        self.unvalidList = []
        self.dbOperate = ProxyHandler()

        logout("proxyRecheck", f"解说validList:{self.validList}")
        logout("proxyRecheck", f"接收unvalidList:{self.unvalidList}")
        logout("proxyRecheck", "proxyRecheck启动初始化完成")

    def getproxy(self):
        """
        更新代理池的数据至本地，并巡查当前代理列表的代理是否可用
        :param unvalidList: 可用的代理
        :param unvalidList: 不可用的代理
        :return: message
        """
        logout("proxyRecheck", "\n")
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入validList:{self.validList}")
        logout("proxyRecheck", f"输入unvalidList:{self.unvalidList}")

        # 1.从数据库里获取当前最新代理数据
        temp = []

        proxies = self.dbOperate.getAll()
        res = [_.to_dict for _ in proxies]
        logout("proxyRecheck", f"本次从数据库里获取当前的最新数据--{res}")

        for proxy in res:
            # print(proxy)
            # 将proxy的键值内容转换为dict类型
            proxy = json.loads(proxy['proxy'])
            temp.append(
                {
                    'server': proxy['server'],
                    'port': proxy['port'],
                    'uuid': proxy['uuid'],
                    'alterId': proxy['alterId'],
                    'cipher': proxy['cipher'],
                    'network': proxy['network'],
                    'ws-path': proxy.get('ws-path', None)
                }
            )

        # 2.移除已添加过的代理数据
        for new in temp:
            # a. 测试代理是否可用, 可用则添加至validList，不可用则添加至unvalidList以便后续删除
            if testVmess2(new['server'], new['port'], new['uuid'], new['alterId'], new['cipher'], new['network'], new.get('ws-path', None)):
                self.validList.append(new)
            else:
                self.unvalidList.append(new)

        logout("proxyRecheck", "当次新增完成")
        logout("proxyRecheck", f"输出validList:{self.validList}")
        logout("proxyRecheck", f"输出unvalidList:{self.unvalidList}")
        logout("proxyRecheck", "="*30)

    def checkproxy(self):
        """
        巡检当前可用代理列表里的代理最新状态
        :param unvalidList: 可用的代理
        :param unvalidList: 不可用的代理
        :return: message
        """
        logout("proxyRecheck", "\n")
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入validList:{self.validList}")
        logout("proxyRecheck", f"输入unvalidList:{self.unvalidList}")

        temp = []  # 待删除列表

        try:

            for proxy in self.validList:

                ### 该部分未测试 ###
                logout("proxyRecheck", f"测试用--proxy--{proxy}")
                connectFail_count = 0  # 重试次数累计
                logout("proxyRecheck", f"测试用--connectFail_count--{connectFail_count}")

                while connectFail_count < 3:
                    if testVmess2(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                        logout("proxyRecheck", f"测试用inWhile--testVmess2--Successful")
                        break
                    else:
                        logout("proxyRecheck", f"测试用inWhile--testVmess2--fail--connectFail_count--{connectFail_count}")
                        connectFail_count += 1

                if connectFail_count > 2:
                    logout("proxyRecheck", f"测试用--加入删除列表--当前connectFail_count--{connectFail_count}")
                    temp.append(proxy)
                    logout("proxyRecheck", f"测试用--加入删除列表--temp--{temp}")

            logout("proxyRecheck", f"测试用--巡检结束--开始删除--temp--{temp}")
            for delproxy in temp:
                self.validList.remove(delproxy)
                self.unvalidList.append(delproxy)
                logout("proxyRecheck", f"测试用--删完完成--validList--{self.validList}--unvalidList--{self.unvalidList}")

        except Exception as e:
            logout("proxyRecheck", f"error-checkproxy-{e}")

        logout("proxyRecheck", "当次巡检完成")
        logout("proxyRecheck", f"输出validList:{self.validList}")
        logout("proxyRecheck", f"输出unvalidList:{self.unvalidList}")
        logout("proxyRecheck", "="*30)

    def deletevalidproxy(self):
        """
        移除代理池中不可用的代理
        :param unvalidList: 不可用的代理
        :return: message
        """
        logout("proxyRecheck", "\n")
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入unvalidList:{self.unvalidList}")

        temp = []  # 待删除列表

        for proxy in self.unvalidList:
            logout("proxyRecheck", f"即将删除代理{str(proxy)}")
            re_proxy = '{"server": "%s",' \
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
            try:
                status = self.dbOperate.delete(Proxy(str(re_proxy)))
                logout("proxyRecheck", f"删除代理{Proxy(str(re_proxy))}请求结果--{status}")
                if int(status) == 1:
                    temp.append(proxy)

            except Exception as e:
                logout("proxyRecheck", f"{e}")

        # 从失效代理列表中移除已经成功删除的代理数据
        for delproxy in temp:
            self.unvalidList.remove(delproxy)

        logout("proxyRecheck", "移除不可用代理完成")
        logout("proxyRecheck", f"输出unvalidList:{self.unvalidList}")
        logout("proxyRecheck", "="*30)

    def run(self):
        """
        总循环
        """


        while True:
            try:
                logout("proxyRecheck", "\n")
                logout("proxyRecheck", f"valid-id-{id(self.validList)}--unvailid-id-{id(self.unvalidList)}")
                self.checkproxy()
                self.getproxy()
                self.deletevalidproxy()
                time.sleep(120)
            except Exception as e:
                logout("proxyRecheck", f"RECHECK模块错误{e}")
                time.sleep(60)


if __name__ == '__main__':

    PR = ProxyRecheck([], [])
    PR.getproxy()
