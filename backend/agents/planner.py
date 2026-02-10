#goal -> plan List[tasks: str] 
import os
from ollama import AsyncClient
from decouple import config

async def makePlan(goal: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "planner.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL"),  
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{GOAL}}", goal)
        }]
    )

    result = response['message']['content']

    rawSteps = [
        step.strip()
        for step in result.split("\n")
        if step.strip() and not step.strip().startswith("#")
    ]

    try:
        steps = rawSteps[rawSteps.index("[") + 1: rawSteps.index("]")]
    except ValueError:
        steps = []
        print("error with planner: no list made")

    return steps