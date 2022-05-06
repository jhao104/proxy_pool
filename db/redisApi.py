import redis
import setting
import json

# 获取redis相关配置
redisConfig = setting.redis


def singleton(cls):

    def inner(*args, **kwargs):

        if not hasattr(cls, "ins"):
            setattr(cls, "ins", cls(*args, **kwargs))

        return getattr(cls, "ins")

    return inner


@singleton
class RedisClient:
    """
    Redis控制单例，包含4张表：
        1. valid = []  # 可用代理的列表
        2. using = {}  # 在使用中的代理字典库 {"pid":{proxyParam}}
        3. unvalid = []  # 已失效代理的列表
        4. listenport = []  # 在使用中使用的端口号
    """

    def __init__(self):
        self.db = redis.Redis(
            host=redisConfig["ip"],
            port=redisConfig["port"],
            password=redisConfig["password"],
            db=redisConfig["db"],
            decode_responses=True
        )
        self.lock = False

    def dict_add(self, r_dict, key, value):
        """
        返回int类型，1为插入成功，0为数据更新成功
        """
        if type(value) == dict:
            value = json.dumps(value)
        return self.db.hset(r_dict, key, value)

    def dict_get(self, r_dict, key):
        """
        返回str类型，值
        """
        return self.db.hget(r_dict, key)

    def dict_getall(self, r_dict):
        """
        返回dict类型，若不存在该表也返回空{}
        """
        return self.db.hgetall(r_dict,)

    def dict_del(self, r_dict, key):
        """
        返回int类型，删除个数
        """
        return self.db.hdel(r_dict, key)

    def list_add(self, r_list, value):
        """
        返回int类型，数值代表列表里有多少个该 value，重复值不冲突
        """
        if type(value) == dict:
            value = json.dumps(value)
        return self.db.lpush(r_list, value)

    def list_get(self, r_list):
        """
        返回list类型，若不存在该表也返回空[]
        """
        return self.db.lrange(r_list, 0, -1)

    def list_del(self, r_list, value):
        """
        返回int类型，删除个数，count=0即删除所有符合的值
        """
        return self.db.lrem(r_list, count=0, value=value)

    def delete(self, key):
        """
        删除key
        """
        return self.db.delete(key)

    def set_add(self, name, value):
        """
        返回int类型，1为插入成功，0为未插入-数据已存在。输入数据统一转换为str类型
        """
        return self.db.sadd(name, value)

    def set_get(self, name):
        """
        获取set类型KEY的所有成员
        """
        return self.db.smembers(name)

    def set_getnum(self, name):
        """
        获取set类型KEY的所有成员
        """
        return self.db.scard(name)

    def set_in(self, name, value):
        """
        判断该元素是否在集合set里
        """
        return self.db.sismember(name, value)

    def set_pop(self, name):
        """
        随机返回一个成员，并删除该成员
        """
        return self.db.spop(name)

    def set_del(self, name, value):
        """
        随机返回一个成员，并删除该成员
        """
        return self.db.srem(name, value)


if __name__ == '__main__':

    rr = RedisClient()

    print(rr.set_get("t3"))
    print(type(rr.set_get("t3")))

    print(rr.set_add("t3", "1"))
    print(rr.set_add("t3", "2"))
    print(rr.set_add("t3", 3))

    print(rr.set_get("t3"))
    print(rr.set_getnum("t3"))
    print(rr.set_in("t3", 3))

    print(rr.set_pop("t3"))

    print(rr.set_get("t3"))
    print(rr.set_getnum("t3"))


