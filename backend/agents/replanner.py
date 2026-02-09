from ollama import AsyncClient
from decouple import config
import os

#should take the next task + reflection and output a new task
#task + reflection -> task

async def replanner(reflection: str, nextTask: str):
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
            .replace("{{NEXT_TASK}}", nextTask)
        }]
    )

    return response['message']['content']