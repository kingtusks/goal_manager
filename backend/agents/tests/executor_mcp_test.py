import asyncio
from executor import executeTask

async def main():
    result = await executeTask("What are the latest developments in AI?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())