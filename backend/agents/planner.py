#goal -> plan for today or this week or smtn
import ollama 
from decouple import config

def makePlan(goal: str):
    with open("prompts/planner.txt", "r") as f:
        raw_prompt = f.read()

    response = ollama.chat(
        model=config("OLLAMA_MODEL"),  
        messages=[{
            "role": "user",
            "content": raw_prompt.replace("{{GOAL}}", goal)
        }]
    )

    return response['message']['content']