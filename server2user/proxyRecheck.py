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
    def __init__(self, recordList, validList, unvalidList):
        """
        更新代理池的数据至本地，并巡查当前代理列表的代理是否可用
        :param recordList: 记录当前服务涉及所有代理，用于比较判断新获取的代理有哪些
        :param unvalidList: 可用的代理
        :param unvalidList: 不可用的代理
        :return: True or False
        """
        self.poolUrl = setting.poolUrl
        self.deleteUrl = setting.deleteUrl
        self.recordList = recordList
        self.validList = validList
        self.unvalidList = unvalidList
        self.dbOperate = ProxyHandler()

        logout("proxyRecheck", f"接收recordList:{self.recordList}")
        logout("proxyRecheck", f"解说validList:{self.validList}")
        logout("proxyRecheck", f"接收unvalidList:{self.unvalidList}")
        logout("proxyRecheck", "proxyRecheck启动初始化完成")

    def getproxy(self, poolUrl, recordList, validList, unvalidList):
        """
        更新代理池的数据至本地，并巡查当前代理列表的代理是否可用
        :param recordList: 记录当前服务涉及所有代理，用于比较判断新获取的代理有哪些
        :param unvalidList: 可用的代理
        :param unvalidList: 不可用的代理
        :return: message
        """

        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入recordList:{recordList}")
        logout("proxyRecheck", f"输入validList:{validList}")
        logout("proxyRecheck", f"输入unvalidList:{unvalidList}")

        # 1.从数据库里获取当前最新代理数据
        temp = []

        # res = requests.get(poolUrl).json()
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
            # True表示当前代理为新代理
            pp_flag = True
            for old in recordList:
                if new["server"] == old["server"] and new["port"] == old["port"]:
                    # ip,port都相同的即为已添加，当前代理为旧代理
                    pp_flag = False
            # 比对recordList完毕，若标志位仍为True则说明当前代理为新代理
            if pp_flag:
                # a.添加至recordList
                recordList.append(new)
                # b. 测试代理是否可用, 可用则添加至validList，不可用则添加至unvalidList以便后续删除
                if testVmess2(new['server'], new['port'], new['uuid'], new['alterId'], new['cipher'], new['network'], new.get('ws-path', None)):
                    validList.append(new)
                else:
                    unvalidList.append(new)

        logout("proxyRecheck", "当次新增完成")
        logout("proxyRecheck", f"输出recordList:{recordList}")
        logout("proxyRecheck", f"输出validList:{validList}")
        logout("proxyRecheck", f"输出unvalidList:{unvalidList}")
        logout("proxyRecheck", "="*30)

    def checkproxy(self, validList, unvalidList):
        """
        巡检当前可用代理列表里的代理最新状态
        :param unvalidList: 可用的代理
        :param unvalidList: 不可用的代理
        :return: message
        """
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入validList:{validList}")
        logout("proxyRecheck", f"输入unvalidList:{unvalidList}")

        for proxy in validList:
            if testVmess2(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None)):
                continue
            else:
                try:
                    validList.remove(proxy)
                except Exception as e:
                    logout("proxyRecheck", f"error-checkproxy-{e}")
                unvalidList.append(proxy)

        logout("proxyRecheck", "当次巡检完成")
        logout("proxyRecheck", f"输出validList:{validList}")
        logout("proxyRecheck", f"输出unvalidList:{unvalidList}")
        logout("proxyRecheck", "="*30)

    def deletevalidproxy(self, deleteUrl, unvalidList):
        """
        移除代理池中不可用的代理
        :param unvalidList: 不可用的代理
        :return: message
        """
        logout("proxyRecheck", "="*30)
        logout("proxyRecheck", f"输入unvalidList:{unvalidList}")

        for proxy in unvalidList:
            re_proxy = "{'server': %s," \
                        "'port': %s," \
                        "'uuid': %s," \
                        "'alterId': %s," \
                        "'cipher': %s," \
                        "'network': %s," \
                        "'ws-path': %s}" % \
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
                status = self.dbOperate.delete(str(Proxy(proxy)))
                logout("proxyRecheck", f"删除代理{Proxy(proxy)}请求结果--{status}")

            except Exception as e:
                logout("proxyRecheck", f"{e}")

        logout("proxyRecheck", "移除不可用代理完成")
        logout("proxyRecheck", f"输出unvalidList:{unvalidList}")
        logout("proxyRecheck", "="*30)

    def run(self):
        while True:
            try:
                self.checkproxy(self.validList, self.unvalidList)
                self.getproxy(self.poolUrl, self.recordList, self.validList, self.unvalidList)
                self.deletevalidproxy(self.deleteUrl, self.unvalidList)
                time.sleep(120)
            except Exception as e:
                logout("proxyRecheck", f"RECHECK模块错误{e}")
                time.sleep(60)


if __name__ == '__main__':

    poolUrl = "http://127.0.0.1:50101/all"
    deleteUrl = "http://127.0.0.1:50101/delete"
    PR = ProxyRecheck()
    PR.getproxy(poolUrl, [], [], [])
