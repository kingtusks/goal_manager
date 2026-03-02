import os
import sys
import json
import asyncio
from decouple import config
from ollama import AsyncClient

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from reflector import reflectOutput #type: ignore

test_outputs = [
    ["", ""] #executor_output, score
]

async def reflectorEval(output):
    prompt_path = os.path.join(current_dir, "prompts", "reflector.txt")

    template = {
        "passed": False,
        "reason": "",
        "agent_output": ""
    }

    reflectorResult = await reflectOutput(output[0])

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()
    
    messages = [{
        "role": "user",
        "content": raw_prompt
            .replace("{{TASK}}", output[0])
            .replace("{{SCORE}}", output[1])
            .replace("{{REFLECTOR_OUTPUT}}", "\n".join(reflectorResult) if isinstance(reflectorResult, list) else str(reflectorResult))
    }]

    response = await AsyncClient(host="http://ollama:11434").chat(
        model=config("EVAL_MODEL"),
        messages=messages
    )

    result = response["message"]["content"]

    print(result)

    try:
        jsonObj = json.loads(result[result.index("{"):result.rindex("}") + 1])
    except ValueError:
        jsonObj = template
        print("error with reflector eval: no json made")

    template.update(jsonObj)
    template["agent_output"] = reflectorResult

    return template

async def main():
    for output in test_outputs:
        print(f"output: {output}")
        result = await reflectorEval(output)
        print(f"result: {result}")

asyncio.run(main())