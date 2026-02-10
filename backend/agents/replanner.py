from ollama import AsyncClient
from decouple import config
import os

#uses adjacent tasks + reflection as context to fix tasks (adds adaptability ig)
#i am an idiot and didnt do the {{}} tags in the system prompt
#also parse for json object after i parse planner

async def replanTask(lastTask: str, reflection: str, nextTask: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "replanner.txt")
    
    with open(prompt_path, "r") as f:
        raw_prompt = f.read()

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt
            .replace("{{REFLECTION}}", reflection)
            .replace("{{LAST_TASK}}", lastTask)
            .replace("{{NEXT_TASK}}", nextTask)
        }]
    )

    return response['message']['content']