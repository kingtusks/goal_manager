#task -> quiz (score in frontend)
from mcp.client.sse import sse_client
from mcp import ClientSession
from ollama import AsyncClient
from decouple import config
import os
import json

#add a "code sandbox so we get accurate code (for coding stuff)"
async def executeTask(task: str):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompts", "executor.txt")

        with open(prompt_path, "r", encoding="utf-8") as f:
            raw_prompt = f.read()

        try:
            async with sse_client("http://mcp_websearch:8001/sse") as (read, write):
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

                    try:
                        response = await AsyncClient(host="http://ollama:11434").chat(
                            model=config("OLLAMA_MODEL"),
                            messages=messages,
                            tools=tools
                        )
                    except Exception as ollama_error:
                        raise ConnectionError(f"Cannot connect to Ollama at http://ollama:11434 - Is Ollama running? Error: {str(ollama_error)}")

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

                        try:
                            final = await AsyncClient(host="http://ollama:11434").chat(
                                model=config("OLLAMA_MODEL"),
                                messages=messages,
                                tools=tools
                            )
                        except Exception as ollama_error:
                            raise ConnectionError(f"Cannot connect to Ollama at http://ollama:11434 - Is Ollama running? Error: {str(ollama_error)}")

                        return final["message"]["content"]
                    else:
                        return response['message']['content']
        except ConnectionError:
            raise
        except Exception as mcp_error:
            raise ConnectionError(f"Cannot connect to MCP server at http://mcp_websearch:8001/sse - Is the MCP server running? Error: {str(mcp_error)}")

    except ConnectionRefusedError as e:
        raise Exception(f"Failed to connect to MCP server or Ollama: {str(e)}")
    except FileNotFoundError as e:
        raise Exception(f"Prompt file not found: {str(e)}")
    except KeyError as e:
        raise Exception(f"Invalid response format from model: {str(e)}")
    except Exception as e:
        error_msg = str(e)
        # Extract more details from TaskGroup errors
        if "TaskGroup" in error_msg:
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg = f"{error_msg} - Caused by: {str(e.__cause__)}"
            if hasattr(e, 'exceptions'):
                sub_errors = [str(ex) for ex in e.exceptions]
                error_msg = f"{error_msg} - Sub-exceptions: {', '.join(sub_errors)}"
        raise Exception(f"Task execution failed: {error_msg}")