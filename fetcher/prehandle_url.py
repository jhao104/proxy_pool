from util.webRequest import WebRequest
from server2user.logout import logout
from db.redisApi import RedisClient
import time, json

url_list = [
        # 'https://fq.lonxin.net/clash/proxies',
        # 'https://sspool.herokuapp.com/clash/proxies',
        # 'https://free886.herokuapp.com/clash/proxies',
        # 'https://proxypoolss.fly.dev/clash/proxies?type=all',
        # 'https://proxy.yugogo.xyz/clash/proxies',
        # 'https://hellopool.herokuapp.com/clash/proxies',
        # 'http://www.fuckgfw.tk/clash/proxies',
        # 'https://dailici.herokuapp.com/clash/proxies',
        # 'https://origamiboy.herokuapp.com/clash/proxies',
        # 'https://free.dswang.ga/clash/proxies',
        # 'https://proxypoolss.fly.dev/clash/proxies',
        # 'https://us-proxypool.herokuapp.com/clash/proxies',
        # 'https://proxies.bihai.cf/clash/proxies',
        'http://42.194.196.226/clash/proxies',
        # 'https://klausvpn.posyao.com/clash/proxies',
        # 'https://gfwglass.tk/clash/proxies',
        # 'https://klausvpn.posyao.com/clash/proxies?type=vmess',
        # 'http://clash.3wking.com:12580/clash/proxies',
        # 'https://proxypool.ednovas.xyz/clash/proxies',
        # 'https://ss.dswang.ga:8443/clash/proxies',
        # 'http://guobang.herokuapp.com/clash/proxies',
        # 'https://eu-proxypool.herokuapp.com/clash/proxies',
        # 'https://hk.xhrzg2017.xyz/clash/proxies',
        # 'http://213.188.195.234/clash/proxies',
        # 'https://ednovas.design/clash/proxies',
        # 'http://wxshi.top:9090/clash/proxies',
        # 'http://39.106.12.141:8081/clash/proxies',
        # 'http://136.244.114.199/clash/proxies',
    ]
db = RedisClient()
protocol_type = ["ss", "vmess"]


def from_web():

    # 数据库初始化
    db.delete("fromWeb")
    db.delete("raw")

    for url in url_list:
        source = WebRequest().get(url).text
        # 打印当前请求页面
        logout("prehandle-url", "=" * 20 + " " + url + " " + "=" * 20)

        try:
            # 分割每一行为一个代理
            source_lines = source.split('\n')
            for line in source_lines:
                line = line[2:]
                # 过滤1-如果是代码头相关内容，即非{}结构，则跳过
                if not line.startswith("{") or not line.endswith("}"):
                    continue

                # print(line)
                line = json.loads(line)

                # 过滤2-非目标协议代理
                if not line["type"] in protocol_type:
                    continue

                # 过滤3-CN即中国代理,部分代理没有country字段则跳过
                try:
                    if line["country"][-2:] == "CN":
                        # logout("prehandle-url", f"--当前代理归属地为-<CN>-跳过--")
                        continue
                except Exception as e:
                    pass

                # 过滤4-排重
                ip_port = f'{line["server"]}:{line["port"]}'

                # 数据库里已存在则跳过
                if db.set_in("fromWeb", ip_port):
                    continue

                else:
                    # 添加至fromWeb排重数据库
                    db.set_add("fromWeb", ip_port)
                    # proxy原始数据添加至raw数据库
                    db.set_add("raw", json.dumps(line))

        except Exception as e:
            logout("prehandle-url", f"网页内容解析错误 -- {e}")

    logout("prehandle-url", f"从web加载代理完成")


def load_proxies():
    # 从redis中加载raw代理
    proxy_nums = db.set_getnum("raw")
    proxy_list = db.set_get("raw")
    if len(proxy_list) == proxy_nums:
        logout("prehandle-url", f"load数据校验完成")
        return proxy_nums, proxy_list
    else:
        logout("prehandle-url", f"load数据校验错误，proxy_nums={proxy_nums}--proxy_list_nums={len(proxy_list)}")


def getProxyFromWeb():
    from_web()
    return load_proxies()


if __name__ == '__main__':
    # from_web()
    # nums, proxylist = load_proxies()
    # print(type(nums))
    # print(nums)
    # print(type(proxylist))
    # # print(proxylist)
    # for i in proxylist:
    #     print(type(i))
    #     print(i)
    #     print(type(json.loads(i)))
    #     break
    nums, p = getProxyFromWeb()
    print(nums)
    print(len(p))