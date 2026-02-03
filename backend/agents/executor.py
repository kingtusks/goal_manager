#plan -> quizzes (dont forget score alt it may not be implemented here)
import ollama
import os
from decouple import config

def executePlan(plan: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "executor.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()

    response = ollama.chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{GOAL}}", plan)
        }]
    )

    return response['message']['content']