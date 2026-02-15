import redis

r = redis.Redis()
p = r.ping()
print(p)