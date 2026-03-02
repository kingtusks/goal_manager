import os
import sys
import json
import asyncio
from ollama import AsyncClient
from decouple import config

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from constructor import constructMaterial #type: ignore

test_executor_outputs = [
    ""
]

async def constructorEval(output: str):
    prompt_path = os.path.join(current_dir, "prompts", "constructor.txt")

    template = {
        "passed": False,
        "reason": "none"
    }

    constructorResult = await constructMaterial(output)

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()
    
    messages = [{
        "role": "user",
        "content": raw_prompt
            .replace("{{OUTPUT}}", output)
            .replace("{{CONSTRUCTOR_RESULT}}", json.dumps(constructorResult))
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
        print("error with constructor eval: no json made")

    template.update(jsonObj)
    template["agent_output"] = constructorResult

    return template


async def main():
    for output in test_executor_outputs:
        print(f"executor output: {output}")
        result = await constructorEval(output)
        print(f"result: {result}")

asyncio.run(main())