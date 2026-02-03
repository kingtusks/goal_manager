#plan -> quizzes (dont forget score alt it may not be implemented here)
import ollama
from decouple import config

def executePlan(plan: str):
    with open("prompts/executor.txt", "r") as f:
        raw_prompt = f.read()

    response = ollama.chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{GOAL}}", plan)
        }]
    )

    return response['message']['content']