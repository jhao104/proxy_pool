from server2user.proxyManage import ProxyManager
from server2user.proxyRecheck import ProxyRecheck
import random, requests, setting, threading
from server2user.logout import logout


class ProxyMain:
    """
    代理管理器，负责从代理池服务端到该服务到用户之间的数据流
    """
    def __init__(self):
        self.valid = []  # 可用代理的列表
        self.using = []  # 在使用中的代理列表
        self.unvalid = []  # 已失效代理的列表
        self.listenport = []

        # 初始化代理管理对象
        self.PM = ProxyManager()
        self.PR = ProxyRecheck(self.valid, self.unvalid)

    def startproxy(self):
        """
        启动一条代理进程
        :return: success-{pid,ip,port}; fail-NOne
        """
        flag = False

        try:
            # 进程开启失败则重试
            while not flag:
                # a.无可用代理
                if len(self.valid) == 0:
                    logout("proxyMain", f"startproxy-当前可用代理数量---{len(self.valid)}---")
                    raise ValueError("当前没有可用代理")
                # b.有可用代理
                proxy = random.choice(self.valid)

                # 随机分配监听端口，控制最大同时启动代理在200左右
                listenport = 10800
                while listenport in self.listenport:
                    listenport = random.randint(10800, 11000)

                # 配置相关参数，调用代理启动程序
                ip = proxy['server']
                port = proxy['port']
                flag, pid = self.PM.startproxy(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None), listenport)
                logout("proxyMain", f"代理启动，参数信息-{proxy['server']}-{proxy['port']}-{proxy['uuid']}-{proxy['alterId']}-{proxy['cipher']}-{proxy['network']}-{proxy.get('ws-path', None)}-{listenport}")

                # 代理启动成功，同步修改相关信息，返回ip、port、pid
                if flag:
                    self.valid.remove(proxy)  # 在可用代理列表中移除该代理
                    proxy['listenport'] = listenport  # 代理添加监听端口信息
                    self.using.append({f'{pid}': proxy})  # 在当前使用列表中，以pid为键，代理信息为值，添加此代理
                    self.listenport.append(listenport)  # 在当前使用端口中，添加此端口

                    return {"127.0.0.1", listenport, pid}

        except Exception as e:
            logout("proxyMain", f"startproxy模块报错---{e}---")
            return {"当前无可用代理"}

    def closeproxy(self, pid):
        """
        关闭一条代理进程
        :return:
        """
        try:
            _proxy = None
            for proxy in self.using:
                for key in proxy.keys():
                    if key == str(pid):
                        _proxy = proxy[str(pid)]
            proxy = _proxy

            # 判断是否在使用列表中查找到对应pid的代理信息
            if proxy is None:
                logout("proxyMain", f"closeproxy模块报错---未在使用列表中查找到对应pid-{str(pid)}-的代理---")
                return {f"未在使用列表中查找到对应pid-{str(pid)}-的代理"}

            # 根据代理信息关闭进程
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
        logout("proxyMain", f"usingTable-{len(self.using)}-{self.using}")
        logout("proxyMain", f"validTable-{len(self.valid)}-{self.valid}")
        logout("proxyMain", f"unvalidTable-{len(self.unvalid)}-{self.unvalid}")
        logout("proxyMain", f"lsportTable-{len(self.listenport)}-{self.listenport}")
        logout("proxyMain", "=" * 50)
        return {
            f"usingTable-{len(self.using)}-{self.using}",
            f"validTable-{len(self.valid)}-{self.valid}",
            f"unvalidTable-{len(self.unvalid)}-{self.unvalid}",
            f"lsportTable-{len(self.listenport)}-{self.listenport}"
        }


if __name__ == '__main__':
    pm = ProxyMain()
    pm.recheck()
    pm.startproxy()