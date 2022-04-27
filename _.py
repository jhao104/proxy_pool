import redis

r = redis.Redis(host='localhost', port=6379, db=1, password=None)

r.hset("test1", "bk", "pp")
# print(r.hget("test1"))
print(r.hgetall("test1"))