import redis
import json
from typing import Any
from decouple import config

redis_client = redis.Redis(
    host=config("REDIS_HOST", default="localhost"),
    port=config("REDIS_PORT", default=6379),
    db=0,
    decode_responses=True
)

class RedisCache:
    @staticmethod
    def get(key: str): #r
        try:
            value = redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get(r) error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, expiry: int = 3600): #c
        try:
            #setex is just set with an expiration time (cus yea redis)
            redis_client.setex(
                key,
                expiry,
                json.dumps(value, default=str) #str is for the datetime stuff
            )
            return True
        except Exception as e:
            print(f"Redis set(c) error: {e}")
            return False

    @staticmethod
    def delete(key: str): #d
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            print("Redis delete(d) error: {e}")
            return False

    @staticmethod
    def delete_pattern(pattern: str): #d
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis delete pattern(d) error: {e}")
            return False
    
#make this async cus i forgot