'''
Does it return a valid list at all (no parse errors)
Are the steps actually relevant to the goal (you can use another LLM call to score relevance 1-5)
Step count sanity check — too few (<2) or too many (>15) is probably a bad plan
Does it use tools when it should vs when it shouldn't

(1-10)
'''
from ollama import AsyncClient

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

def planner_eval(goal):
    score = 0;
    return score

if __name__ == "__main__":
    for goal in test_goals:
        planner_eval(test_goals)