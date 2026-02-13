#task -> quiz (score in frontend)
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
        tools_response = await client.get("https://localhost:8001/tools")
        tools_data = tools_response.json()
        print("tools:" {[t["name"] for t in tools_data]})

        tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["inputSchema"]
                }
            }
            for tool in tools_data
        ]

        response = await AsyncClient().chat(
            model=config("OLLAMA_MODEL"),
            messages=[{
                "role": "user",
                "content": raw_prompt.replace("{{TASK}}", task)
            }],
            tools=tools
        )

        if response["message"].get("tool_calls"):
            print(f"{config("OLLAMA_MODEL")} wants to use {len(response['message']['tool_calls'])} tool(s)")
            messages.append(response["message"])

            for tool_call in response["message"]["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["args"]

                tools_response = await client.post(
                    "http://localhost:8001/call-tool",
                    json = {
                        "name": tool_name,
                        "arguments": tool_args
                    }
                )

                response = tools_response.json()
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result)
                })


            final = await AsyncClient().chat(
                model=config("OLLAMA_MODEL"),
                messages=[{
                    "role": "user",
                    "content": raw_prompt.replace("{{TASK}}", task)
                }],
                tools=tools
            )

            return final["message"]["content"]
        else:
            return response['message']['content']