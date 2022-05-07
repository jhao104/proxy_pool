from server2user.proxyManage import ProxyManager
from server2user.proxyRecheck import ProxyRecheck
import random, threading, json
from server2user.logout import logout
from db import redisApi


class ProxyMain:
    """
    代理管理器，负责从代理池服务端到该服务到用户之间的数据流
    """
    def __init__(self):
        # valid = []  # 可用代理的列表
        # using = []  # 在使用中的代理列表
        # unvalid = []  # 已失效代理的列表
        # lsportList = []

        self.db = redisApi.RedisClient()
        # 初始化代理管理对象
        self.PM = ProxyManager()
        self.PR = ProxyRecheck()

    def startproxy(self):
        """
        启动一条代理进程
        :return: success-{pid,ip,port}; fail-NOne
        """
        # 从redis里取数据
        valid = self.db.list_get("valid")
        lsport = self.db.list_get("lsport")

        flag = False

        try:
            # 进程开启失败则重试
            while not flag:
                # a.无可用代理
                if len(valid) == 0:
                    logout("proxyMain", f"startproxy-当前可用代理数量---{len(valid)}---")
                    raise ValueError("当前没有可用代理")
                # b.有可用代理
                proxy = random.choice(valid)

                # 随机分配监听端口，控制最大同时启动代理在200左右
                listenport = 10800
                while str(listenport) in lsport:  # redis返回的键也是str，所以加str()
                    listenport = random.randint(10800, 11000)

                # 配置相关参数，调用代理启动程序
                if proxy["protocol"] == "vmess":
                    flag, pid = self.PM.startproxy_vmess(proxy['server'], proxy['port'], proxy['uuid'], proxy['alterId'], proxy['cipher'], proxy['network'], proxy.get('ws-path', None), listenport)
                    logout("proxyMain", f"代理启动，参数信息-{proxy['server']}-{proxy['port']}-{proxy['uuid']}-{proxy['alterId']}-{proxy['cipher']}-{proxy['network']}-{proxy.get('ws-path', None)}-{listenport}")
                if proxy["protocol"] == "ss":
                    flag, pid = self.PM.startproxy_ss(proxy['server'], proxy['port'], proxy['password'], proxy['cipher'], listenport)
                    logout("proxyMain", f"代理启动，参数信息-{proxy['server']}-{proxy['port']}-{proxy['password']}-{proxy['cipher']}-{listenport}")
                else:
                    pass

                # 代理启动成功，同步修改相关信息，返回ip、port、pid
                if flag:
                    # 在可用代理列表中移除该代理
                    self.db.list_del("valid", proxy)

                    proxy = json.loads(proxy)
                    proxy['listenport'] = listenport  # 代理添加监听端口信息

                    # 在当前使用列表中，以pid为键，代理信息为值，添加此代理
                    self.db.dict_add("using", pid, proxy)

                    # 在当前使用端口中，添加此端口
                    self.db.list_add("lsport", listenport)

                    return {"ip": "127.0.0.1", "port": listenport, "pid": pid}

        except Exception as e:
            logout("proxyMain", f"startproxy模块报错---{e}---")
            return {"当前无可用代理"}

    def closeproxy(self, pid):
        """
        关闭一条代理进程
        :return:
        """
        # 从redis里取数据
        using = self.db.dict_getall("using")

        try:
            _proxy = None
            for key in using:  # 遍历的是键
                if key == str(pid):
                    _proxy = using[str(pid)]
            proxy = json.loads(_proxy)  # 将str转dict

            # 判断是否在使用列表中查找到对应pid的代理信息
            if proxy is None:
                logout("proxyMain", f"closeproxy模块报错---未在使用列表中查找到对应pid-{str(pid)}-的代理---")
                return {f"未在使用列表中查找到对应pid-{str(pid)}-的代理"}

            logout("proxyMain", f"closeproxy模块---找到对应pid-{str(pid)}-的代理信息{proxy}---")

            # 根据代理信息关闭进程
            listenport = proxy['listenport']

            if self.PM.closeproxy(pid):
                del_dict = {pid: proxy}
                logout("proxyMain", f"临时测试-{del_dict}")

                # using.remove(del_dict)
                self.db.dict_del("using", pid)

                # valid.append(proxy)
                self.db.list_add("valid", proxy)

                # lsportList.remove(listenport)
                self.db.list_del("lsport", listenport)

                return f"对应pid-{str(pid)}-的代理已关闭"

            return f"ERROR-对应pid-{str(pid)}-的代理关闭失败"

        except Exception as e:
            logout("proxyMain", f"closeproxy模块报错---{e}---")
            return f"ERROR-对应pid-{str(pid)}-的代理关闭失败"

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
        # 从redis里取数据
        valid = self.db.list_get("valid")
        unvalid = self.db.list_get("unvalid")
        using = self.db.dict_getall("using")
        lsportList = self.db.list_get("lsportList")

        logout("proxyMain", "="*50)
        logout("proxyMain", f"usingTable-{len(using)}-{using}")
        logout("proxyMain", f"validTable-id-{id(valid)}-{len(valid)}-{valid}")
        logout("proxyMain", f"unvalidTable-id-{id(unvalid)}-{len(unvalid)}-{unvalid}")
        logout("proxyMain", f"lsportTable-{len(lsportList)}-{lsportList}")
        logout("proxyMain", "=" * 50)
        return f"usingTable-{len(using)}-{using}\nvalidTable-id-{id(valid)}-{len(valid)}-{valid}\nunvalidTable-id-{id(unvalid)}-{len(unvalid)}-{unvalid}\nlistenportTable-{len(lsportList)}-{lsportList}"


if __name__ == '__main__':
    pm = ProxyMain()
    # pm.recheck()
    pm.pprint()