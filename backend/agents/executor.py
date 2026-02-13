#task -> quiz (score in frontend)
from mcp.client.sse import sse_client
from mcp import ClientSession
from ollama import AsyncClient
from decouple import config
import os
import json
import httpx

#implement web search
async def executeTask(task: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "executor.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()

    async with httpx.AsyncClient() as client:
        async with sse_client("http://localhost:8001/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                tools_data = tools_result.tools

                print(f"tools: {[t.name for t in tools_data]}")

                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.inputSchema
                        }
                    }
                    for t in tools_data
                ]

                messages = [{
                    "role": "user",
                    "content": raw_prompt.replace("{{TASK}}", task)
                }]

                response = await AsyncClient().chat(
                    model=config("OLLAMA_MODEL"),
                    messages=messages,
                    tools=tools
                )

                if response["message"].get("tool_calls"):
                    print(f"{config("OLLAMA_MODEL")} wants to use {len(response['message']['tool_calls'])} tool(s)")
                    messages.append(response["message"])

                    for tool_call in response["message"]["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        tool_args = tool_call["function"]["arguments"]

                        tool_result = await session.call_tool(tool_name, tool_args)       
                        content = [item.model_dump() for item in tool_result.content]

                        messages.append({
                            "role": "tool",
                            "content": json.dumps(content)
                        })

                    final = await AsyncClient().chat(
                        model=config("OLLAMA_MODEL"),
                        messages=messages,
                        tools=tools
                    )

                    return final["message"]["content"]
                else:
                    return response['message']['content']