#reflects on the score and feeds data back to planner to make better plans
import ollama
from decouple import config

def reflectPlan(score: str):
    with open("prompts/reflector.txt", "r") as f:
        raw_prompt = f.read()

    response = ollama.chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{GOAL}}", goal)
        }]
    )

    return response['message']['content']