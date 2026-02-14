import asyncio
from .replanner import replanTask

async def main():
    #lastTask: str, reflection: str, nextTask: str
    result = await replanTask(
        "Understand trading hours and market operations",
        "Reflection Here"
        ""
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())