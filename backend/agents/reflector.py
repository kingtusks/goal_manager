import os
import json
from mcp import ClientSession
from mcp.client.sse import sse_client
from decouple import config
from ollama import AsyncClient

mcp_links = {
    "database": "http://localhost:8002/sse",
    "redis": "http://localhost:8003/sse"
}

async def reflectOutput(task_output: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "reflector.txt")

    all_tools = []
    sessions = {}

    with open(prompt_path, "r") as f:
        raw_prompt = f.read()

    for service_name, service_url in mcp_links.items():
        try:
            async with sse_client(service_url) as (read, write):
                session = ClientSession(read, write)
                await session.initialize()
                tools_result = await session.list_tools()
                print(f"{service_name} has {len(tools_result.tools)} tools")

                sessions[service_name] = session

                for tool in tools_result.tools:
                    all_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema
                        },
                        "_service": service_name  
                    })
        except Exception as e:
            print(f"cant connect to {service_name}: {e}")

    print(f"tools available: {len(all_tools)}")

    messages = [{
        "role": "user",
        "content": raw_prompt.replace("{{TASK_OUTPUT}}", task_output)
    }]

    response = await AsyncClient(host="http://ollama:11434").chat(
        model = config("OLLAMA_MODEL"),
        messages=messages,
        tools=[{k: v for k, v in tool.items() if k != "_service"} for tool in all_tools]
    )

    if response["message"].get("tool_calls"):
        print(f"reflector wants to use {len(response['message']['tool_calls'])} tool(s)")
        messages.append(response["message"])

        for tool_call in response["message"]["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = tool_call["function"]["arguments"]
            
            service_name = next(
                (t["_service"] for t in all_tools if t["function"]["name"] == tool_name),
                None
            )

            if not service_name or service_name not in sessions:
                print(f"tool {tool_name} not found")
                continue
            
            print(f"calling {tool_name} ({service_name})")

            session = sessions[service_name]
            tool_result = await session.call_tool(tool_name, tool_args)
            
            content = [item.model_dump() for item in tool_result.content]
            
            messages.append({
                "role": "tool",
                "content": json.dumps(content)
            })
        final_response = await AsyncClient(host="http://ollama:11434").chat(
            model=config("OLLAMA_MODEL"),
            messages=messages,
            tools=[{k: v for k, v in tool.items() if k != "_service"} for tool in all_tools]
        )
            
        result = final_response['message']['content']
    else:
        print("no tools needed")
        result = response['message']['content']

    return result