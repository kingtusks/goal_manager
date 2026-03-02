import os
import sys
import json
import asyncio
from decouple import config
from ollama import AsyncClient

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from executor import executeTask

test_tasks = [
    "",
]

async def executorEval(task):
    score = 10;
    prompt_path = os.path.join(current_dir, "prompts", "executor.txt")

    executorResult = await executeTask(task)

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()
    
    messages = [{
        "role": "user",
        "content": raw_prompt
            .replace("{{TASK}}", task)
            .replace("{{EXECUTOR_OUTPUT}}", "\n".join(executorResult) if isinstance(executorResult, list) else str(executorResult))
    }]

    response = await AsyncClient(host="http://ollama:11434").chat(
        model=config("EVAL_MODEL"),
        messages=messages
    )

    result = response["message"]["content"]

    print(result)

    template = {
        "deductions": "0",
        "final_score": "0",
        "reason": "none"
    }

    try:
        jsonObj = json.loads(result[result.index("{") + 1: result.index("}")])
    except ValueError:
        jsonObj = template
        print("error with executor eval: no json made")

    template.update(jsonObj)

    return template

if __name__ == "__main__":
    async def main():
        for task in test_tasks:
            print(f"task: {task}")
            result = await executorEval(task)
            print(f"result: {result}")
    
    asyncio.run(main())