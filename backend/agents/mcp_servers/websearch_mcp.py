from fastmcp import FastMCP
from decouple import config
from ddgs import DDGS
import asyncio

#port 8001

mcp = FastMCP("Web Search Service")

@mcp.tool()
async def web_search(query: str, max_results: int = 5):
    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, lambda: list(DDGS().text(query, max_results=max_results)))
    return [{"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")} for r in raw]

@mcp.tool()
async def search_news(query: str, max_results: int = 5):
    results = []
    for result in DDGS().news(query, max_results=max_results):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("href", ""),
            "snipped": result.get("body", "")
        })
    
    return results

if __name__ == "__main__":
    mcp.run(transport="sse", host=config("MCP_HOST"), port=8001)

    