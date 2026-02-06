from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import sessionDB, engine
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agents.executor import executeTask
from agents.planner import makePlan
from agents.reflector import reflectOutput
from datetime import datetime, timezone
import models

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionDB()
    try:
        yield db
    finally:
        db.close()

@app.get("/") #home (placeholder)
async def root():
    return {"ok": True}

@app.get("/goals") #r
async def get_all_goals(db: Session = Depends(get_db)):
    db_goals = db.query(models.GoalsTable).all()
    return db_goals 

@app.get("/goal/user/{user_id}") #r
async def get_goals_from_userid(user_id: int, db: Session = Depends(get_db)):  
    db_goals = db.query(models.GoalsTable).filter(models.GoalsTable.user_id == user_id).all()  
    if db_goals:
        return db_goals
    raise HTTPException(status_code=404, detail=f"No goals found for user id: {user_id}")

@app.get("/goal/{goal_id}") #r
async def get_goals_from_id(goal_id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == goal_id).first()
    if db_goal:
        return db_goal
    raise HTTPException(status_code=404, detail=f"No goals found with id: {goal_id}") 

@app.post("/creategoal", response_model=models.GoalsPydantic) #c
async def make_goal(goal: models.GoalsPydantic, db: Session = Depends(get_db)):
    db_goal = models.GoalsTable(
        user_id=goal.user_id,
        goal=goal.goal
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

@app.delete("/deletegoal") #d
async def delete_goal(id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == id).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()
        return {"id of goal deleted": id}
    raise HTTPException(status_code=404, detail=f"No goals found with id: {id}")  

@app.post("/agent/plan/goal/{goal_id}")
async def create_plan(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(models.GoalsTable).filter(
        models.GoalsTable.id == goal_id
    ).first()
    if not goal:
        raise HTTPException(404, "Goal not found")
    steps = await makePlan(goal.goal) #returns a list[str]
    created_tasks = []
    for step in steps:
        task = models.TasksTable(
            user_id=goal.user_id,
            goal_id=goal.id,
            description=step
        )
        db.add(task)
        created_tasks.append(task)
    db.commit()
    return {"tasks_created": len(created_tasks)}

@app.post("/agent/execute/task")
async def execute_next_task(db: Session = Depends(get_db)):
    task = (
        db.query(models.TasksTable)
        .filter(models.TasksTable.status == "pending")
        .order_by(models.TasksTable.created_at)
        .with_for_update(skip_locked=True)
        .first()
    )
    if not task:
        return {"message": "No pending tasks"}

    task.status = "running"
    db.commit()
    db.refresh(task)

    try:
        result = await executePlan(task.description)
        task.status = "completed"
        task.completed_at = datetime.utcnow()

        output = models.AgentOutputsTable(
            task_id=task.id,
            agent_type="executor",
            output_text=result
        )
        db.add(output)
        db.commit()
        return {"task_id": task.id, "result": result}
    except Exception as e:
        task.status = "failed"
        db.commit()
        raise HTTPException(500, str(e))

@app.post("/agent/reflect/task/{task_id}")
async def reflect(task_id: int, db: Session = Depends(get_db)):
    existing = db.query(models.AgentOutputsTable).filter(
        models.AgentOutputsTable.task_id == task_id,
        models.AgentOutputsTable.agent_type == "reflector"
    ).first()

    if existing:
        return {"reflection": existing.output_text}

    output = db.query(models.AgentOutputsTable).filter(
        models.AgentOutputsTable.task_id == task_id,
        models.AgentOutputsTable.agent_type == "executor"
    ).first()

    if not output:
        raise HTTPException(404, "No executor output")

    reflection = await reflectPlan(output.output_text)
    db.add(models.AgentOutputsTable(
        task_id=task_id,
        agent_type="reflector",
        output_text=reflection
    ))
    db.commit()
    return {"reflection": reflection}

#maybe connect them all to redis (for read/write) and make redis connect to postgres
#caching ^ (will do today or tomorrow)