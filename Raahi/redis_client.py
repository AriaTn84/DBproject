import redis
from redis.exceptions import ConnectionError

def get_redis_connection():
    try:
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        client.ping()
        print("Connected to Redis")
        return client
    except ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        return None