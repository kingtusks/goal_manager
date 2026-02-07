import redis
import json
from typing import Optional, Any
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
    def set(key: str, value: Any, expiry: int = 3600):
        try:
            redis_client.setex()
