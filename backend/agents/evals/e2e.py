import asyncio
import random
from . import planner_eval, executor_eval, constructor_eval, reflector_eval, replanner_eval

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

async def handleEvalFailures(result: dict, agent_name: str):
    template = {
        "passed": False,
        "reason": "none"
    }

    if result["passed"] == False:
        template["reason"] = f"{agent_name.capitalize()} eval failed due to {result}"
        return template

async def e2e(goal):
    try:
        plannerEvalResult = await planner_eval.plannerEval(goal)

        #when the eval fails i want it to return the template and just exit
        #check if theres something in handleEvalFailures (is handleEvalFailures) and if so return it 
        evalStatusCheck = await handleEvalFailures(plannerEvalResult, "Planner")
        
        if evalStatusCheck:
            return evalStatusCheck
        
        for i, task in enumerate(plannerEvalResult["agent_output"]):
            executorEvalResult = await executor_eval.executorEval(task)
            evalStatusCheck = await handleEvalFailures(executorEvalResult, "Executor")
            if evalStatusCheck:
                return evalStatusCheck
            
            constructorEvalResult = await constructor_eval.constructorEval(executorEvalResult["agent_output"])
            evalStatusCheck = await handleEvalFailures(constructorEvalResult, "Constructor")
            if evalStatusCheck:
                return evalStatusCheck

            reflectorEvalResult = await reflector_eval.reflectorEval(
                executorEvalResult["agent_output"], 
                f"{random.randint(0, 10)}/10"
            )
            evalStatusCheck = await handleEvalFailures(reflectorEvalResult, "Reflector")
            if evalStatusCheck:
                return evalStatusCheck

            if i == 0:
                replannerEvalResult = await replanner_eval.replannerEval(
                    last_task="The current task is the first task.",
                    reflection=reflectorEvalResult["agent_output"],
                    next_task=plannerEvalResult["agent_output"][1]
                )
            elif i == (len(plannerEvalResult["agent_output"]) - 1):
                replannerEvalResult = await replanner_eval.replannerEval(
                    last_task=plannerEvalResult["agent_output"][i-1],
                    reflection=reflectorEvalResult["agent_output"],
                    next_task="The current task is the last task."
                )            
            else:
                replannerEvalResult = await replanner_eval.replannerEval(
                    last_task=plannerEvalResult["agent_output"][i-1],
                    reflection=reflectorEvalResult["agent_output"],
                    next_task=plannerEvalResult["agent_output"][i+1]
                )
            evalStatusCheck = await handleEvalFailures(replannerEvalResult, "Replanner")
            if evalStatusCheck:
                return evalStatusCheck
        
        return {
            "passed": True,
            "reason": "All goals completed successfully."
        }

    except Exception as e:
        return {"passed": False, "reason": f"Error: {e}"}
    
async def main():
    for goal in test_goals:
        print(f"goal: {goal}")
        result = await e2e(goal)
        print(f"result: {result}")

asyncio.run(main())
