#reflects on the score and feeds data back to planner to make better plans
import ollama
import os
from decouple import config

def reflectPlan(score: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "reflector.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()

    response = ollama.chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{GOAL}}", score)
        }]
    )

    return response['message']['content']