import redis
r = redis.Redis(host='192.168.233.4', port=6379, db=0, password='redis')
r.set('test1', 'ok1')
s = r.get('test')
print(s)
