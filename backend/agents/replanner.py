from ollama import AsyncClient
from decouple import config
import json
import os

#uses adjacent tasks + reflection as context to fix tasks (adds adaptability ig)
#i am an idiot and didnt do the {{}} tags in the system prompt
#also parse for json object after i parse planner

async def replanTask(lastTask: str, reflection: str, nextTask: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(current_dir, "prompts", "replanner.txt")
    
    with open(prompt_path, "r") as f:
        raw_prompt = f.read()

    response = await AsyncClient().chat(
        model=config("OLLAMA_MODEL"),
        messages=[{
            "role": "user",
            "content": raw_prompt
            .replace("{{REFLECTION}}", reflection)
            .replace("{{LAST_TASK}}", lastTask)
            .replace("{{NEXT_TASK}}", nextTask)
        }]
    )
    
    result = response['message']['content']

    #print(rawResponse)

    template = {
        "action": "keep",
        "reason": "",
        "edited_task": "",
        "new_tasks": []
    }

    try:
        jsonObj = json.loads(result[result.index("{") + 1: result.index("}")])
    except ValueError:
        jsonObj = template
        print("error with planner: no list made")
    
    print(jsonObj)
    template.update(jsonObj)
    print(template)

    return template