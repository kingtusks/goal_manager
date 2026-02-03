#goal -> plan for today or this week or smtn
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

    return response['message']['content']