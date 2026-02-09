import redis.asyncio as redis
import json
from typing import Any
from decouple import config

redis_client = redis.from_url(
    f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default=6379)}",
    decode_responses=True
)

class RedisCache:
    @staticmethod
    async def get(key: str): #r
        try:
            value = await redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get(r) error: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Any, expiry: int = 3600): #c
        try:
            #setex is just set with an expiration time (cus yea redis)
            await redis_client.setex(
                key,
                expiry,
                json.dumps(value, default=str) #str is for the datetime stuff
            )
            return True
        except Exception as e:
            print(f"Redis set(c) error: {e}")
            return False

    @staticmethod
    async def delete(key: str): #d
        try:
            await redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete(d) error: {e}")
            return False

    @staticmethod
    async def delete_pattern(pattern: str): #d
        try:
            keys = []
            async for key in redis_client.scan_iter(pattern):
                keys.append(key)
            if keys:
                await redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Redis delete pattern(d) error: {e}")
            return False
    