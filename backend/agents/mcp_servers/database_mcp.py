from fastmcp import FastMCP
from decouple import config
import asyncpg

mcp = FastMCP("Database Service")
pool = None

async def get_pool():
    global pool
    if not pool:
        pool = await asyncpg.create_pool(config("DATABASE_URL"))
    return pool

@mcp.tool()

 