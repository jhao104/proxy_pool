import requests, json, time, subprocess, random
from fetcher.testVmess import testVmess
from fetcher.testSs import testSs
from setting import testUrl
from server2user.logout import logout


class ProxyManager:
    """
    代理管理器，负责该服务与用户交互
    """
    def startproxy_vmess(self, ip, port, uuid, alterId, cipher, network, ws_path, listenport):
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
            pid = proc_vmess_test.pid
            time.sleep(3)

            # 测试可用性
            import requests
            flag = False
            testurl = random.choice(testUrl)

            try:
                proxy = {"http": f"socks5h://127.0.0.1:{listenport}", "https": f"socks5h://127.0.0.1:{listenport}"}

                session = requests.Session()
                session.trust_env = False

                response = session.get(testurl, proxies=proxy, headers=get_request_headers(), timeout=10)
                flag = response.status_code

            except Exception as e:
                logout("proxyManage", f"v2ray-requests.get-ERROR--{str(ip)}:{str(port)}--{listenport}-- {e}")
                return False, None

            time.sleep(5)

            if int(flag) == 200:
                logout("proxyManage", f"v2ray.get--{str(ip)}:{str(port)}--{listenport}-SUCCESSFUL")
                return True, pid

        except Exception as e:
            logout("proxyManage", f"v2ray.get-ERROR--{str(ip)}:{str(port)}--{listenport}-- {e}")
            # 关闭进程
            logout("proxyManage", f'pid--{pid}')
            subprocess.call(["kill", "-9", str(pid)])
            time.sleep(3)

    def startproxy_ss(self, ip, port, password, cipher, listenport):
        """
        开启一个代理
        :param proxy: ss代理参数
        :return: success-{pid}; fail-None
        """

        """
        测试代理是否真实可用
        """
        pid = ""
        try:
            # 接收当前要测的vmess代理参数
            ss_config = {
                'ip': ip,
                'port': int(port),
                'password': password,
                'cipher': cipher
            }

            # v2ray配置文件
            conf_dir = "./tools/Shadowsocks/shadowsocks.json"

            # 读取congif
            with open(conf_dir, 'r+', encoding='utf-8') as conf:
                source = json.load(conf)
                # 修改代理配置信息
                source['local_port'] = int(listenport)  # 测试用的监听端口
                source['server'] = ss_config['ip']
                source['server_port'] = ss_config['port']
                source['password'] = ss_config['password']
                source['method'] = ss_config['cipher']

            # 写入config
            with open(conf_dir, 'w+', encoding='utf-8') as conf:
                conf.write(json.dumps(source, indent=4, ensure_ascii=False))

            # 启动进程
            proc_ss_test = subprocess.Popen("sslocal -c ./tools/Shadowsocks/shadowsocks.json".split(" "))
            pid = proc_ss_test.pid
            time.sleep(3)

            # 测试可用性
            import requests
            flag = False
            testurl = random.choice(testUrl)

            try:
                proxy = {"http": f"socks5h://127.0.0.1:{listenport}", "https": f"socks5h://127.0.0.1:{listenport}"}

                session = requests.Session()
                session.trust_env = False

                response = session.get(testurl, proxies=proxy, headers=get_request_headers(), timeout=10)
                flag = response.status_code

            except Exception as e:
                logout("proxyManage", f"ss-requests.get-ERROR--{str(ip)}:{str(port)}--{listenport}-- {e}")
                return False, None

            time.sleep(5)

            if int(flag) == 200:
                logout("proxyManage", f"ss.get--{str(ip)}:{str(port)}--{listenport}-SUCCESSFUL")
                return True, pid

        except Exception as e:
            logout("proxyManage", f"ss.get-ERROR--{str(ip)}:{str(port)}--{listenport}-- {e}")
            # 关闭进程
            logout("proxyManage", f'pid--{pid}')
            subprocess.call(["kill", "-9", str(pid)])
            time.sleep(3)

    def closeproxy(self, pid):
        """
        根据pid关闭一个代理
        :param pid: 代理进程id
        :return: True or False
        """
        try:
            subprocess.call(["kill", "-9", str(pid)])
            time.sleep(5)
            return True
        except Exception as e:
            logout("proxyManage", f"closeProxy--{e}")
            return False


def get_request_headers():
    USER_AGENTS = [

        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",

        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",

        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",

        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",

        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",

        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",

        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",

        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",

        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",

        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",

        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",

        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",

        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",

        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",

        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",

        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",

        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",

        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",

        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",

    ]

    headers = {

    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50',

    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',

    'Accept-Language': 'en-US,en;q=0.5',

    'Connection': 'keep-alive',

    }

    return headers
