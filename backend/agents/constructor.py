#will take executor output and create quizzes/etc in react
from ollama import AsyncClient
from decouple import config
import os

#implement this somehow (this is lowk gon be difficult)
async def constructMaterial(executor_output: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "constructor.txt")

    with open(prompt_path, "r") as f:
        raw_prompt = f.read()

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{EXECUTOR_OUTPUT}}", executor_output)
        }]
    )

    return response['message']['content']
    