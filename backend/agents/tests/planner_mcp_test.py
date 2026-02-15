import asyncio
from .planner import makePlan

async def main():
    result = await makePlan("teach me the basics of commodities in a week")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())