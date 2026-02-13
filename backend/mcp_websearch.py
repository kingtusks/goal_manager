from fastmcp import FastMCP
from ddgs import DDGS

mcp = FastMCP("Web Search Service")

@mcp.tool()
async def web_search(query: str, max_results: int = 5):
    results = []
    for result in DDGS().text(query, max_results=max_results):
        results.append({
            "title": result.get("title", ""),
            "url": result.get("href", ""),
            "snipped": result.get("body", "")
        })

    return results

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
    import uvicorn
    uvicorn.run(mcp.get_asgi_app(), host=config("MCP_HOST"), port=8001)

    