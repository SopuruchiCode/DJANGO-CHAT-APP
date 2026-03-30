import redis

r = redis.Redis(host="",
                port="6379",
                
                )
p = r.ping()
print(p)