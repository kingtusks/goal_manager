#goal -> plan List[tasks: str] 
import os
#from translate import Translator
from ollama import AsyncClient
from decouple import config


#add web search + memory (redis/psql)
async def makePlan(goal: str, status: bool):
    retry = ""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "planner.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()

    if not status:
        with open(os.path.join(current_dir, "prompts", "plannerRetry.txt"), "r", encoding="utf-8") as f:
            retry = f"{f.read()}\n"

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL", default="qwen2.5:7b-instruct"),  
        messages=[{
            "role": "user",
            "content": f"{retry}{raw_prompt.replace("{{GOAL}}", goal)}"
        }]
    )

    result = response['message']['content']

    rawSteps = [
        step.strip()
        for step in result.split("\n")
        if step.strip() and not step.strip().startswith("#")
    ]

    print(rawSteps)

    try:
        steps = rawSteps[rawSteps.index("[") + 1: rawSteps.index("]")]
    except ValueError:
        steps = []
        print("error with planner: no list made")

    return steps