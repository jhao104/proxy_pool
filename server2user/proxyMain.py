from server2user.proxyManage import ProxyManager
from server2user.proxyRecheck import ProxyRecheck
import random, requests, setting, threading
from server2user.logout import logout


class ProxyMain:
    """
    代理管理器，负责从代理池服务端到该服务到用户之间的数据流
    """
    def __init__(self):
        self.init = []  # 第一次启动将可用代理读入用缓冲表
        self.record = []  # 记录所有使用的代理列表
        self.valid = []  # 可用代理的列表
        self.using = []  # 在使用中的代理列表
        self.unvalid = []  # 已失效代理的列表
        self.listenport = []

        # 初始化代理管理对象
        self.PM = ProxyManager()
        self.PR = ProxyRecheck(self.record, self.valid, self.unvalid)


    def startproxy(self):
        """
        启动一条代理进程
        :return: success-{pid,ip,port}; fail-NOne
        """
        flag = False

        try:
            while not flag:
                proxy = random.choice(self.valid)

                listenport = 10800
                while listenport in self.listenport:
                    listenport = random.randint(10800, 11000)

                ip = proxy['server']
                port = proxy['port']
                flag, pid = self.PM.startproxy(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None), listenport)
                logout("proxyMain", f"启动成功，参数信息-{proxy['server']}-{proxy['port']}-{proxy['uuid']}-{proxy['alterId']}-{proxy['cipher']}-{proxy['network']}-{proxy.get('ws-path', None)}-{listenport}")

                if flag:
                    self.valid.remove(proxy)
                    proxy['listenport'] = listenport
                    self.using.append({f'{pid}': proxy})
                    self.listenport.append(listenport)

                    return {"127.0.0.1", listenport, pid}
        except Exception as e:
            logout("proxyMain", f"startproxy模块报错---{e}---")
            return {None}

    def closeproxy(self, pid):
        """
        关闭一条代理进程
        :return:
        """
        try:
            proxy = self.using[str(pid)]
            listenport = proxy['listenport']

            if self.PM.closeproxy(pid):

                self.using.remove(proxy)
                self.valid.append(proxy)
                self.listenport.remove(listenport)

                return {True}

            return {False}

        except Exception as e:
            logout("proxyMain", f"closeproxy模块报错---{e}---")
            return {False}


    def recheck(self):
        """
        定时检查代理可用性
        :return:
        """
        t = threading.Thread(target=self.PR.run)
        t.start()

    def pprint(self):
        """
        打印当前代理信息
        """
        logout("proxyMain", "="*50)
        logout("proxyMain", f"recordTable-{len(self.record)}-{self.record}")
        logout("proxyMain", f"usingTable-{len(self.using)}-{self.using}")
        logout("proxyMain", f"validTable-{len(self.valid)}-{self.valid}")
        logout("proxyMain", f"unvalidTable-{len(self.unvalid)}-{self.unvalid}")
        logout("proxyMain", f"lsportTable-{len(self.listenport)}-{self.listenport}")
        logout("proxyMain", "=" * 50)
        return {f"recordTable-{len(self.record)}-{self.record}", f"usingTable-{len(self.using)}-{self.using}", f"validTable-{len(self.valid)}-{self.valid}", f"unvalidTable-{len(self.unvalid)}-{self.unvalid}", f"lsportTable-{len(self.listenport)}-{self.listenport}"}


if __name__ == '__main__':
    pm = ProxyMain()
    pm.recheck()
    pm.startproxy()