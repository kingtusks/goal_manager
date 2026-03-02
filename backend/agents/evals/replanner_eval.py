import os
import sys
import json
import asyncio
from decouple import config
from ollama import AsyncClient

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from replanner import replanTask #type: ignore

test_cases = [
    ["", "", ""] #last_task, reflection, next_task
]

async def replannerEval(last_task: str, reflection: str, next_task: str):
    prompt_path = os.path.join(current_dir, "prompts", "replanner.txt")

    template = {
        "passed": False,
        "reason": "none"
    }

    replannerResult = await replanTask(last_task, reflection, next_task)

    with open(prompt_path, "r", encoding="utf-8") as f:
            raw_prompt = f.read()
    
    messages = [{
        "role": "user",
        "content": raw_prompt
            .replace("{{LAST_TASK}}", last_task)
            .replace("{{REFLECTION}}", reflection)
            .replace("{{NEXT_TASK}}", next_task)
            .replace("{{REPLANNER_OUTPUT}}", json.dumps(replannerResult))
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
        print("error with replanner eval: no json made")

    template.update(jsonObj)
    print(template)
    template["agent_output"] = replannerResult

    return template

async def main():
    for case in test_cases:
        print(f"case: {case}")
        result = await replannerEval(case[0], case[1], case[2])
        print(f"result: {result}")

asyncio.run(main())
