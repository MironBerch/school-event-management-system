from redis import Redis

redis_connection = Redis(host='redis', port=6379, db=1)
