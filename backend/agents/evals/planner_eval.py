'''
Are the steps actually relevant to the goal (you can use another LLM call to score relevance 1-5) > 1-5
Does it use tools when it should vs when it shouldn't > T/F
'''

import os
import sys
import asyncio
from decouple import config
from ollama import AsyncClient

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from planner import makePlan

test_goals = [
    "Learn Python programming from scratch",
    "Get fit and lose 10 pounds in 3 months",
    "Build and launch a personal portfolio website",
    "Read 12 books this year",
    "Learn to cook 5 new meals",
    "Save $5000 in 6 months",
    "Start a YouTube channel about cooking",
    "Learn Spanish to conversational level",
]

async def plannerEval(goal):
    score = 10;
    prompt_path = os.path.join(current_dir, "prompts", "planner.txt")

    plannerResult = await makePlan(goal)

    if type(plannerResult) is not list:
        score -= 3
    else:
        if len(plannerResult) <= 2 or len(plannerResult) >= 15:
            score -= 3

    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()
    
    messages = [{
        "role": "user",
        "content": raw_prompt
            .replace("{{GOAL}}", goal)
            .replace("{{SCORE}}", score)
            .replace("{{PLANNER_OUTPUT}}", plannerResult)
    }]

    response = await AsyncClient(host="http://ollama:11434").chat(
        model=config("EVAL_MODEL"),
        messages=messages
    )

    results = response["message"]["content"]

    return score

'''
if __name__ == "__main__":
    for goal in test_goals:
        asyncio.run(plannerEval(goal))
'''

