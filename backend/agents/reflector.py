from ollama import AsyncClient
import os
from decouple import config

async def reflectOutput(task_output: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "reflector.txt")

    with open(prompt_path, "r") as f:
        raw_prompt = f.read()

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{TASK_OUTPUT}}", task_output)
        }]
    )

    return response['message']['content']