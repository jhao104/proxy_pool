import re, json, os, subprocess, time, random
from time import sleep
from server2user.logout import logout
from setting import testUrl


def testVmess(ip, port, uuid, alterId, cipher, network, ws_path):
    """
    测试代理是否真实可用
    """
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
        # 测试用，固定一个可用代理
        # vmess_config = {
        #     'ip': "cdn-cn.nekocloud.cn",
        #     'port': 19046,
        #     'uuid': "76cb50a4-9fd8-352e-99f4-a7bb5959b07b",
        #     'alterId': 0,
        #     'cipher': "auto",
        #     'network': "ws",
        #     'ws_path': "/catnet"
        # }
        

        # v2ray配置文件
        conf_dir = "./tools/v2ray-cli/config.json"

        # 读取congif
        with open(conf_dir, 'r+', encoding='utf-8') as conf:
            source = json.load(conf)
            # 修改代理配置信息
            source['inbounds'][0]['port'] = 10800  # 测试用的监听端口
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
        time.sleep(3)

        # 测试可用性
        import requests, socket, socks
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10800)
        socket.socket = socks.socksocket
        flag = False
        try:
            flag = requests.get(random.choice(testUrl), timeout=5).status_code
        except Exception as e:
            logout("testVmess", f"v2ray.get--{str(ip)}:{str(port)}-- {e}")
        time.sleep(5)

        # 关闭进程
        logout("testVmess", f'pid--{proc_vmess_test.pid}')
        subprocess.call(["kill", "-9", str(proc_vmess_test.pid)])

        # 关闭全局代理到10800
        socks.set_default_proxy()
        socket.socket = socks.socksocket

        # 根据情况返回结果
        if int(flag) == 200:
            logout("testVmess", f"v2ray--{str(ip)}:{str(port)}-- connecting successfully ...")
            return True
        else:
            logout("testVmess", f"v2ray--{str(ip)}:{str(port)}-- connecting fail !")
            return False

    except Exception as e:
        logout("testVmess", f"testVmess解析模块ERROR-- {e}")
        return False


def testVmess2(ip, port, uuid, alterId, cipher, network, ws_path):
    """
    测试代理是否真实可用
    """
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
        # 测试用，固定一个可用代理
        # vmess_config = {
        #     'ip': "cdn-cn.nekocloud.cn",
        #     'port': 19046,
        #     'uuid': "76cb50a4-9fd8-352e-99f4-a7bb5959b07b",
        #     'alterId': 0,
        #     'cipher': "auto",
        #     'network': "ws",
        #     'ws_path': "/catnet"
        # }

        # v2ray配置文件
        conf_dir = "./tools/v2ray-cli/config.json"

        # 读取congif
        with open(conf_dir, 'r+', encoding='utf-8') as conf:
            source = json.load(conf)
            # 修改代理配置信息
            source['inbounds'][0]['port'] = 13960  # 测试用的监听端口
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
        time.sleep(3)

        # 测试可用性
        import requests, socket, socks
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 10800)
        socket.socket = socks.socksocket
        flag = False
        try:
            flag = requests.get(random.choice(testUrl), timeout=5).status_code
        except Exception as e:
            logout("testVmess2", f"v2ray.get--{str(ip)}:{str(port)}-- {e}")
        time.sleep(5)

        # 关闭进程
        logout("testVmess2", f'pid--{proc_vmess_test.pid}')
        subprocess.call(["kill", "-9", str(proc_vmess_test.pid)])

        # 关闭全局代理到10800
        socks.set_default_proxy()
        socket.socket = socks.socksocket

        # 根据情况返回结果
        if int(flag) == 200:
            logout("testVmess2", f"v2ray--{str(ip)}:{str(port)}-- connecting successfully ...")
            return True
        else:
            logout("testVmess2", f"v2ray--{str(ip)}:{str(port)}-- connecting fail !")
            return False

    except Exception as e:
        logout("testVmess2", f"testVmess解析模块ERROR-- {e}")
        return False



