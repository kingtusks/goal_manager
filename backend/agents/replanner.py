from ollama import AsyncClient
from decouple import config
from mcp.client.sse import sse_client
from mcp import ClientSession
import json
import os

# uses adjacent tasks + reflection as context to fix tasks (adds adaptability ig)

mcp_links = {
    "websearch": "http://mcp_websearch:8001/sse",
    "database": "http://mcp_database:8002/sse",
    "redis": "http://mcp_redis:8003/sse"
}

async def collect_tools():
    all_tools = []

    for service_name, service_url in mcp_links.items():
        try:
            async with sse_client(service_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()

                    for tool in tools_result.tools:
                        all_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            },
                            "_service": service_name,
                            "_url": service_url
                        })

                    print(f"got {len(tools_result.tools)} tools from {service_name}")
        except Exception as e:
            print(f"cant connect to {service_name}: {e}")

    return all_tools


async def call_tool(tool_meta: dict, tool_name: str, tool_args: dict):
    async with sse_client(tool_meta["_url"]) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, tool_args)
            return [item.model_dump() for item in result.content]


async def replanTask(lastTask: str, reflection: str, nextTask: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "replanner.txt")

    with open(prompt_path, "r") as f:
        raw_prompt = f.read()

    try:
        all_tools = await collect_tools()
        ollama_tools = [{k: v for k, v in tool.items() if not k.startswith("_")} for tool in all_tools]

        print(f"tools available: {len(all_tools)}")

        messages = [{
            "role": "user",
            "content": raw_prompt
                .replace("{{REFLECTION}}", reflection)
                .replace("{{LAST_TASK}}", lastTask)
                .replace("{{NEXT_TASK}}", nextTask)
        }]

        response = await AsyncClient(host="http://ollama:11434").chat(
            model=config("OLLAMA_MODEL"),
            messages=messages,
            tools=ollama_tools
        )

        if response["message"].get("tool_calls"):
            print(f"replanner wants to use {len(response['message']['tool_calls'])} tool(s)")
            messages.append(response["message"])

            for tool_call in response["message"]["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]

                tool_meta = next(
                    (t for t in all_tools if t["function"]["name"] == tool_name),
                    None
                )

                if not tool_meta:
                    print(f"tool {tool_name} not found")
                    continue

                print(f"calling {tool_name} ({tool_meta['_service']})")

                content = await call_tool(tool_meta, tool_name, tool_args)
                messages.append({
                    "role": "tool",
                    "content": json.dumps(content)
                })

            final_response = await AsyncClient(host="http://ollama:11434").chat(
                model=config("OLLAMA_MODEL"),
                messages=messages,
                tools=ollama_tools
            )
            result = final_response["message"]["content"]
        else:
            print("no tools needed")
            result = response["message"]["content"]

    except Exception as e:
        print(f"error with replanner: {e}")
        raise

    template = {
        "action": "keep",
        "reason": "",
        "edited_task": "",
        "new_tasks": []
    }

    try:
        jsonObj = json.loads(result[result.index("{") + 1: result.index("}")])
    except ValueError:
        jsonObj = template
        print("error with replanner: no json made")

    print(jsonObj)
    template.update(jsonObj)
    print(template)

    return template