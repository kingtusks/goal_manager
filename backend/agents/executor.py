#task -> quiz (score in frontend)
from ollama import AsyncClient
import os
from decouple import config

#make a new executor.txt and refactor this + in app.jsx
async def executeTask(task: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "executor.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{TASK}}", task)
        }]
    )

    return response['message']['content']