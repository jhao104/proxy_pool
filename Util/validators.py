import requests

validators = []


def validator(func):
    validators.append(func)
    return func


@validator
def timeOutValidator(proxy):
    """
    检测超时
    :param proxy:
    :return:
    """
    if isinstance(proxy, bytes):
        proxy = proxy.decode("utf8")
    proxies = {"http": "http://{proxy}".format(proxy=proxy)}
    try:
        r = requests.get('http://www.baidu.com', proxies=proxies, timeout=10, verify=False)
        if r.status_code == 200:
            return True
    except Exception as e:
        pass
    return False


@validator
def customValidator(proxy):
    """
    自定义validator函数，校验代理是否可用
    :param proxy:
    :return:
    """

    return True
