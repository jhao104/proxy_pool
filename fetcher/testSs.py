import json, subprocess, time, random
from server2user.logout import logout
from setting import testUrl


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


def testSs(ip, port, password, cipher):
    """
    测试代理是否真实可用
    """
    try:
        # 接收当前要测的vmess代理参数
        ss_config = {
            'ip': ip,
            'port': int(port),
            'password': password,
            'cipher': cipher
        }

        # ss配置文件
        # conf_dir = "./tools/Shadowsocks-4.1/gui-config.json"
        conf_dir = "./tools/Shadowsocks/shadowsocks.json"

        # 读取congif
        with open(conf_dir, 'r+', encoding='utf-8') as conf:
            source = json.load(conf)
            # 修改代理配置信息
            source['local_port'] = 10800  # 测试用的监听端口
            source['server'] = ss_config['ip']
            source['server_port'] = ss_config['port']
            source['password'] = ss_config['password']
            source['method'] = ss_config['cipher']

        # 写入config
        with open(conf_dir, 'w+', encoding='utf-8') as conf:
            conf.write(json.dumps(source, indent=4, ensure_ascii=False))

        # 启动进程
        proc_vmess_test = subprocess.Popen("sslocal -c ./tools/Shadowsocks/shadowsocks.json".split(" "))
        time.sleep(3)

        # 测试可用性
        import requests
        flag = False
        testurl = random.choice(testUrl)
        try:
            proxy = {"http": "socks5h://127.0.0.1:10800", "https": "socks5h://127.0.0.1:10800"}

            session = requests.Session()
            session.trust_env = False

            response = session.get(testurl, proxies=proxy, headers=get_request_headers(), timeout=10)
            flag = response.status_code

        except Exception as e:
            logout("testSs", f"ss.get---- {e}")
        time.sleep(5)

        # 关闭进程
        logout("testSs", f'pid--{proc_vmess_test.pid}')
        subprocess.call(["kill", "-9", str(proc_vmess_test.pid)]) # linux用
        # subprocess.call(["taskkill", "-F", "/pid", str(proc_vmess_test.pid)])  # windows用

        # 根据情况返回结果
        if int(flag) == 200:
            logout("testSs", f"ss--{str(ip)}:{str(port)}--测试站点:{testurl} -- connecting successfully ...")
            return True
        else:
            logout("testSs", f"ss--{str(ip)}:{str(port)}--测试站点:{testurl} -- connecting fail !")
            return False

    except Exception as e:
        logout("testSs", f"testss解析模块ERROR-- {e}")
        return False


def testSs2(ip, port, password, cipher):
    """
    测试代理是否真实可用
    """
    try:
        # 接收当前要测的vmess代理参数
        ss_config = {
            'ip': ip,
            'port': int(port),
            'password': password,
            'cipher': cipher
        }

        # ss配置文件
        # conf_dir = "./tools/Shadowsocks-4.1/gui-config.json"
        conf_dir = "./tools/Shadowsocks/shadowsocks.json"

        # 读取congif
        with open(conf_dir, 'r+', encoding='utf-8') as conf:
            source = json.load(conf)
            # 修改代理配置信息
            source['local_port'] = 13960  # recheck测试用的监听端口
            source['server'] = ss_config['ip']
            source['server_port'] = ss_config['port']
            source['password'] = ss_config['password']
            source['method'] = ss_config['cipher']

        # 写入config
        with open(conf_dir, 'w+', encoding='utf-8') as conf:
            conf.write(json.dumps(source, indent=4, ensure_ascii=False))

        # 启动进程
        proc_vmess_test = subprocess.Popen("sslocal -c ./tools/Shadowsocks/shadowsocks.json".split(" "))
        time.sleep(3)

        # 测试可用性
        import requests
        flag = False
        testurl = random.choice(testUrl)
        try:
            proxy = {"http": "socks5h://127.0.0.1:13960", "https": "socks5h://127.0.0.1:13960"}

            session = requests.Session()
            session.trust_env = False

            response = session.get(testurl, proxies=proxy, headers=get_request_headers(), timeout=10)
            flag = response.status_code

        except Exception as e:
            logout("testSs", f"ss.get---- {e}")
        time.sleep(5)

        # 关闭进程
        logout("testSs", f'pid--{proc_vmess_test.pid}')
        subprocess.call(["kill", "-9", str(proc_vmess_test.pid)]) # linux用
        # subprocess.call(["taskkill", "-F", "/pid", str(proc_vmess_test.pid)])  # windows用

        # 根据情况返回结果
        if int(flag) == 200:
            logout("testSs", f"ss--{str(ip)}:{str(port)}--测试站点:{testurl} -- connecting successfully ...")
            return True
        else:
            logout("testSs", f"ss--{str(ip)}:{str(port)}--测试站点:{testurl} -- connecting fail !")
            return False

    except Exception as e:
        logout("testSs", f"testss解析模块ERROR-- {e}")
        return False


def tests():
    # 测试可用性
    import requests
    flag = False
    testurl = random.choice(testUrl)
    try:
        proxy = {"http": "socks5h://127.0.0.1:10800", "https": "socks5h://127.0.0.1:10800"}

        session = requests.Session()
        session.trust_env = False

        response = session.get(testurl, proxies=proxy, )
        flag = response.status_code

    except Exception as e:
        logout("testSs", f"ss.get---- {e}")
    time.sleep(5)

    # 根据情况返回结果
    if int(flag) == 200:
        logout("testSs", f"ss----测试站点:{testurl} -- connecting successfully ...")
        return True
    else:
        logout("testSs", f"ss----测试站点:{testurl} -- connecting fail !")
        return False


if __name__ == '__main__':
    tests()