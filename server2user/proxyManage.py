import requests, json, time, subprocess
import socket, socks, threading
from fetcher.testVmess import testVmess
import setting
from server2user.logout import logout


class ProxyManager:
    """
    代理管理器，负责该服务与用户交互
    """
    def startproxy(self, ip, port, uuid, alterId, cipher, network, ws_path, listenport):
        """
        开启一个代理
        :param proxy: vmess代理参数
        :return: success-{pid}; fail-None
        """

        """
        测试代理是否真实可用
        """
        pid = ""
        try:
            # 接收当前要测的vmess代理参数
            vmess_config = {
                'ip': ip,
                'port': int(port),
                'uuid': uuid,
                'alterId': int(alterId),
                'cipher': cipher,
                'network': network,
                'ws_path': ws_path
            }

            # v2ray配置文件
            conf_dir = "./tools/v2ray-cli/config.json"

            # 读取congif
            with open(conf_dir, 'r+', encoding='utf-8') as conf:
                source = json.load(conf)
                # 修改代理配置信息
                source['inbounds'][0]['port'] = int(listenport)  # 测试用的监听端口
                source['outbounds'][0]['settings']['vnext'][0] = {
                    "address": vmess_config['ip'],
                    "port": vmess_config['port'],
                    "users": [
                        {
                            "id": vmess_config['uuid'],
                            "alterId": vmess_config['alterId'],
                            "email": "t@t.tt",
                            "security": vmess_config['cipher']
                        }
                    ]
                }
                source['outbounds'][0]['streamSettings'] = {
                    "network": vmess_config['network'],
                    "wsSettings": {
                        "path": vmess_config['ws_path']
                    }
                }
                if vmess_config['ws_path'] is None:
                    source['outbounds'][0]['streamSettings'].pop('ws_path')

            # 写入config
            with open(conf_dir, 'w+', encoding='utf-8') as conf:
                conf.write(json.dumps(source, indent=4, ensure_ascii=False))

            # 启动进程
            proc_vmess_test = subprocess.Popen("./tools/v2ray-cli/v2ray")
            pid =proc_vmess_test.pid
            time.sleep(3)

            # 测试可用性
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", int(listenport))
            socket.socket = socks.socksocket
            flag = False
            try:
                flag = requests.get('https://www.google.com', timeout=5).status_code
            except Exception as e:
                logout("proxyManage", f"v2ray.get--{str(ip)}:{str(port)}--{listenport}-- {e}")
                return False

        except Exception as e:
            print(e)
            time.sleep(3)

        finally:
            # 关闭全局代理
            socks.set_default_proxy()
            socket.socket = socks.socksocket
            logout("proxyManage", f"v2ray.get--{str(ip)}:{str(port)}--{listenport}-- successful")
            return True, pid

    def closeproxy(self, pid):
        """
        根据pid关闭一个代理
        :param pid: 代理进程id
        :return: True or False
        """
        try:
            subprocess.call(["kill", "-9", str(pid)])
            time.sleep(3)
            return True
        except Exception as e:
            logout("proxyManage", f"closeProxy--{e}")
            return False

