from fastmcp import FastMCP
import redis.asyncio as redis
from decouple import config
from typing import Optional
import json

#port 8003

mcp = FastMCP("Redis Search")
client = None

async def get_redis():
    global client
    if not client:
        client = await redis.from_url(
            f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default=6379)}",
        )
    return client

@mcp.tool()
async def get_cached_goals(user_id: Optional[int] = None):
    if user_id:
        key = f"goals:user:{user_id}"
    else:
        key: f"goals:all"
    
    r = await get_redis()
    cached = await r.get(key)

    if cached:
        try:
            return json.loads(cached)
        except:
            return {"raw": cached.decode() if isinstance(cached, bytes) else cached}
    
    return None

@mcp.tool()
async def get_cached_goals(goal_id: int):
    r = await get_redis()
    cached = await r.get(f"goal:{goal_id}")

    if cached:
        try:
            return json.loads(cached)
        except:
            return {"raw": cached.decode() if isinstance(cached, bytes) else cached}

    return None

@mcp.tool()
async def get_cached_plan(goal_id: int):
    r = await get_redis()
    cached = await r.get(f"plan:goal:{goal_id}")

    if cached:
        try:
            return json.loads(cached)
        except:
            return {"raw": cached.decode() if isinstance(cached, bytes) else cached}

    return None

@mcp.tool()
async def get_task_execution(task_id: int):
    r = await get_redis()
    cached = await r.get("execution:task:{task_id}")

    if cached:
        try:
            return json.loads(cached)
        except:
            return {"raw": cached.decode() if isinstance(cached, bytes) else cached}

    return None

@mcp.tool()
async def get_task_reflection(task_id: int):
    r = await get_redis()
    cached = await r.get(f"reflection:task:{task_id}")

    if cached:
        try:
            return json.loads(cached)
        except:
            return {"raw": cached.decode() if isinstance(cached, bytes) else cached}

    return None

@mcp.tool()
async def get_task_constructor(task_id: int):
    r = await get_redis()
    cached = await r.get(f"constructor:task:{task_id}")

    if cached:
        try:
            return json.loads(cached)
        except:
            return {"raw": cached.decode() if isinstance(cached, bytes) else cached}

    return None

@mcp.tool()
async def get_all_task_outputs(task_id: int):
    r = await get_redis()
    outputs = {}
    
    exec_cached = await r.get(f"execution:task:{task_id}")
    if exec_cached:
        try:
            outputs["execution"] = json.loads(exec_cached)
        except:
            outputs["execution"] = exec_cached.decode() if isinstance(exec_cached, bytes) else exec_cached
    
    reflect_cached = await r.get(f"reflection:task:{task_id}")
    if reflect_cached:
        try:
            outputs["reflection"] = json.loads(reflect_cached)
        except:
            outputs["reflection"] = reflect_cached.decode() if isinstance(reflect_cached, bytes) else reflect_cached
    
    constructor_cached = await r.get(f"constructor:task:{task_id}")
    if constructor_cached:
        try:
            outputs["constructor"] = json.loads(constructor_cached)
        except:
            outputs["constructor"] = constructor_cached.decode() if isinstance(constructor_cached, bytes) else constructor_cached
    
    return outputs if outputs else {"message": "no cached outputs found"}

@mcp.tool()
async def search_cached_tasks(pattern: str = "*", limit: int = 20):
    r = await get_redis()
    keys = []

    async for key in r.scan_iter(match=pattern, count=100):
        key_str = key.decode() if isinstance(key, bytes) else key
        keys.append(key_str)
        if len(keys) >= limit:
            break
    
    return keys

@mcp.tool()
async def get_cache_stats():
    r = await get_redis()
    
    stats = {
        "goals": 0,
        "plans": 0,
        "executions": 0,
        "reflections": 0,
        "constructors": 0,
        "total_keys": 0
    }
    
    async for key in r.scan_iter(count=1000):
        key_str = key.decode() if isinstance(key, bytes) else key
        stats["total_keys"] += 1
        
        if key_str.startswith("goals:") or key_str.startswith("goal:"):
            stats["goals"] += 1
        elif key_str.startswith("plan:"):
            stats["plans"] += 1
        elif key_str.startswith("execution:"):
            stats["executions"] += 1
        elif key_str.startswith("reflection:"):
            stats["reflections"] += 1
        elif key_str.startswith("constructor:"):
            stats["constructors"] += 1
    
    return stats

@mcp.tool()
async def check_if_cached(key: str):
    r = await get_redis()
    exists = await r.exists(key)

    if exists:
        ttl = await r.ttl(key)
        return {
            "cached": True,
            "ttl_seconds": ttl if ttl > 0 else None,
            "expires": ttl > 0
        }
    
    return {"cached": False}

if __name__ == "__main__":
    mcp.run(transport="sse", host=config("MCP_HOST"), port=8003)
