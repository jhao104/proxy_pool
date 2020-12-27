import os
import re
import time
import requests
from requests.exceptions import ConnectionError


# ==================================================================== #

# 可以在线运行python的网站: https://repl.it/languages
# 依赖:
# requests==2.21.0
# You can run python from the website https://repl.it/languages
# requirements:
# requests==2.21.0

# 保存代理的文件名
# Save proxies file name
CHECKED_PROXY = 'unchecked_proxy_spysone'

url = 'https://spys.one/en/socks-proxy-list/'

# url = 'http://spys.one/en/http-proxy-list/'

# url = 'http://spys.one/en/anonymous-proxy-list/'

# 设置代理配置:
# Proxy Information Settings:

# xpp = '5' 对应网页上Per page的值,即500. 0:30, 1:50, 2:100, 3:200, 4:300, 5:500
# xpp = '5' Set the Per page value to be 500. 0:30, 1:50, 2:100, 3:200, 4:300, 5:500
xpp = '5'

# xf1 = '4' 对应ANM的值,当前为HIA. 0:All, 1:ANM&HIA, 2:NOA, 3:ANM, 4:HIA
# xf1 = '4' Set the ANM value to be HIA. 0:All, 1:ANM&HIA, 2:NOA, 3:ANM, 4:HIA
xf1 = '0'

# xf2 = '0' 对应SSL的值. 0:All, 1:SSL+, 2:SSL-
# xf2 = '0' Set the SSL value to be All. 0:All, 1:SSL+, 2:SSL-
xf2 = '0'

# xf4 = '0' 对应Port的值. 0:All, 1:3128, 2:8080,3:80
# xf4 = '0' Set the Port value to be All. 0:All, 1:3128, 2:8080,3:80
xf4 = '0'

# xf5 = '2' 对应Type的值. 0:All, 1:HTTP, 2:SOCKS
# xf5 = '2' Set the Type value to be SOCKS. 0:All, 1:HTTP, 2:SOCKS
xf5 = '0'

# ==================================================================== #

proxies = {
    "http": "http://127.0.0.1:54321",
    "https": "http://127.0.0.1:54321"
}
unchecked = []
file_path_unchecked = '{0}/{1}.txt'.format(os.getcwd(), CHECKED_PROXY)

# GET HTML [Per page|ANM|SSL|Port|Type]
def get_index(xpp, xf1, xf2, xf4, xf5):
    header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.2 Safari/605.1.15'}
    data = {
        'xpp': xpp,
        'xf1': xf1,
        'xf2': xf2,
        'xf4': xf4,
        'xf5': xf5
    }
    print('Getting the website...')
    try:
        rsp = requests.post(url=url, headers=header, data=data, proxies=proxies, timeout=5)
        if rsp.status_code == 200:
            print('Success.')
            html = rsp.text
            return html
        else:
            exit('Can not get the website.')
    except ConnectionError:
        exit('Please run your proxy app and try again.')

def get_proxy_info(html):
    pattern = re.compile('onmouseout.*?spy14>(.*?)<s.*?write.*?nt>\"\+(.*?)\)</scr.*?\/en\/(.*?)-', re.S)
    infos = re.findall(pattern, html)
    return infos

def parse_proxy_info(html, infos):
    print('Get {} proxies.'.format(len(infos)))
    print('Start to get proxy details...')
    port_word = re.findall('\+\(([a-z0-9^]+)\)+', html)
    # DECRYPT PORT VALUE
    port_passwd = {}
    portcode = (re.findall('table><script type="text/javascript">(.*)</script>', html))[0].split(';')
    for i in portcode:
        ii = re.findall('\w+=\d+', i)
        for i in ii:
            kv = i.split('=')
            if len(kv[1]) == 1:
                k = kv[0]
                v = kv[1]
                port_passwd[k] = v
            else:
                pass
    # GET PROXY INFO
    for i in infos:
        proxies_info = {
            'ip': i[0],
            'port': i[1],
            'protocol': i[2]
        }
        port_word = re.findall('\((\w+)\^', proxies_info.get('port'))
        port_digital = ''
        for i in port_word:
            port_digital += port_passwd[i]
        test_it = '{0}:{1}'.format(proxies_info.get('ip'), port_digital)
        unchecked.append(test_it)


def main():
    html = get_index(xpp, xf1, xf2, xf4, xf5)
    infos = get_proxy_info(html)
    parse_proxy_info(html, infos)
    with open(file_path_unchecked,'a+') as f:
        f.write(time.strftime(">>>%Y-%m-%d %H:%M:%S", time.localtime()) + '\n')
        for proxy in unchecked:
            f.write(proxy + '\n')
    print('Save to {}.\nDone.'.format(file_path_unchecked))


if __name__ == '__main__':
    main()