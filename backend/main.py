from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import sessionDB, engine
from pydantic import BaseModel
from auth import PasswordManager
from redis_client import RedisCache
from sqlalchemy.orm import Session
from agents.executor import executeTask
from agents.planner import makePlan
from agents.reflector import reflectOutput
from agents.replanner import replanTask
from agents.constructor import constructMaterial
from datetime import datetime
import models

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

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

#takes pydantic
@app.post("/signup") #c
async def signup(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.UserTable).filter(
        models.UserTable.username == user.username
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    existing_email = db.query(models.UserTable).filter(
        models.UserTable.email == user.email
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already in use")

    hashed_password = PasswordManager.hash_password(user.password)

    new_user = models.UserTable(
        username = user.username,
        email = user.email,
        password = hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "user made",
        "user_id": new_user.user_id,
        "username": new_user.username
    }

@app.post("/login") #r
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.UserTable).filter(
        models.UserTable.username == user.username
    ).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not PasswordManager.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if PasswordManager.needs_rehash(db_user.password):
        db_user.password = PasswordManager.hash_password(user.password)
        db.commit()
    
    return {
        "message": "Login successful",
        "user_id": db_user.user_id,
        "username": db_user.username
    }

@app.patch("/user/{user_id}/password") #u (put updates everything while patch does specifics)
async def change_password(user_id: int, old_password: str, new_password: str, db: Session = Depends(get_db)):
    db_user = db.query(models.UserTable).filter(
        models.UserTable.user_id == user_id
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not PasswordManager.verify_password(old_password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect current password")
    
    db_user.password = PasswordManager.hash_password(new_password)
    db.commit()
    
    return {"message": "password updated successfully"}
    
@app.get("/goals") #r
async def get_all_goals(db: Session = Depends(get_db)):
    cached = await RedisCache.get("goals:all")
    if cached:
        return cached
    db_goals = db.query(models.GoalsTable).all()
    goals_dict = [models.GoalsPydantic.from_orm(i).dict() for i in db_goals]
    await RedisCache.set("goals:all", goals_dict, expiry=300)
    return goals_dict 

@app.get("/goal/user/{user_id}") #r
async def get_goals_from_userid(user_id: int, db: Session = Depends(get_db)):  
    cached = await RedisCache.get(f"goals:user:{user_id}")
    if cached:
        return cached
    db_goals = db.query(models.GoalsTable).filter(models.GoalsTable.user_id == user_id).all()  
    if db_goals:
        goals_dict = [models.GoalsPydantic.from_orm(i).dict() for i in db_goals]
        await RedisCache.set(f"goals:user:{user_id}", goals_dict, expiry=300)
        return db_goals
    raise HTTPException(status_code=404, detail=f"No goals found for user id: {user_id}")

@app.get("/goal/{goal_id}") #r
async def get_goals_from_id(goal_id: int, db: Session = Depends(get_db)):
    cached = await RedisCache.get(f"goal:{goal_id}")
    if cached:
        return cached
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == goal_id).first()
    if db_goal:
        goals_dict = [models.GoalsPydantic.from_orm(i).dict() for i in db_goal]
        await RedisCache.set(f"goal:{goal_id}", goals_dict, expiry=300)
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
    await RedisCache.delete("goals:all") #this is so the next r gets updated data
    #await RedisCache.delete(f"goals:user:{goal.user_id}") #this too lol
    return db_goal

@app.delete("/deletegoal") #d
async def delete_goal(id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == id).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()
        await RedisCache.delete("goals:all")
        #await RedisCache.delete(f"goals:user:{user_id}")
        await RedisCache.delete(f"goal:{id}")
        return {"id of goal deleted": id}
    raise HTTPException(status_code=404, detail=f"No goals found with id: {id}")  

@app.post("/agent/plan/goal/{goal_id}")
async def create_plan(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(models.GoalsTable).filter(
        models.GoalsTable.id == goal_id
    ).first()
    if not goal:
        raise HTTPException(404, "Goal not found")

    cached = await RedisCache.get(f"plan:goal:{goal_id}")
    if cached:
        return cached

    steps = await makePlan(goal.goal) #returns a list[str]
    if not steps:
        print("redoing steps")
        steps = await makePlan(goal.goal, False)
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

    result = {"tasks_created": len(created_tasks)}
    await RedisCache.set(f"plan:goal:{goal_id}", result, expiry=3600)
    return result

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

    #may add a goal here idk

    task.status = "running"
    db.commit()
    db.refresh(task)

    try:
        cached = await RedisCache.get(f"execution:task:{task.id}")
        if cached:
            return cached

        result = await executeTask(task.description)
        task.status = "completed"
        task.completed_at = datetime.utcnow()

        output = models.AgentOutputsTable(
            task_id=task.id,
            agent_type="executor",
            output_text=result
        )
        
        db.add(output)
        db.commit()
        result = {"task_id": task.id, "result": result}
        await RedisCache.set(f"execution:task:{task.id}", result, expiry=3600)
        return result
    except Exception as e:
        task.status = "failed"
        db.commit()
        raise HTTPException(500, str(e))

@app.post("/agent/construct/task/{task_id}")
async def construct(task_id: int, db: Session = Depends(get_db)):
    cached = await RedisCache.get(f"constructor:task:{task_id}")
    if cached:
        return cached

    existing = db.query(models.AgentOutputsTable).filter(
        models.AgentOutputsTable.task_id == task_id,
        models.AgentOutputsTable.agent_type == "constructor"
    ).first()

    if existing:
        return {"reflection": existing.output_text}
    
    executor_output = db.query(models.AgentOutputsTable).filter(
        models.AgentOutputsTable.task_id == task_id,
        models.AgentOutputsTable.agent_type == "executor"
    ).first()

    if not executor_output:
        raise HTTPException(404, "No executor output")

    blueprint = await constructMaterial(executor_output.output_text)

    #parse json similar to replanner

    db.add(models.AgentOutputsTable(
        task_id=task_id,
        agent_type="constructor",
        output_text=blueprint
    ))
    db.commit()
    result = {"constructor_output": blueprint}
    await RedisCache.set(f"constructor:task:{task_id}", result, expiry=3600)
    return result

@app.post("/agent/reflect/task/{task_id}")
async def reflect(task_id: int, db: Session = Depends(get_db)):
    cached = await RedisCache.get(f"reflection:task:{task_id}")
    if cached:
        return cached

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

    reflection = await reflectOutput(output.output_text)
    db.add(models.AgentOutputsTable(
        task_id=task_id,
        agent_type="reflector",
        output_text=reflection
    ))
    db.commit()
    result = {"reflection": reflection}
    await RedisCache.set(f"reflection:task:{task_id}", result, expiry=3600)
    return result

@app.post("/agent/replan/task/{task_id}")
async def replan(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.TasksTable).filter_by(id=task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")

    reflection = db.query(models.AgentOutputsTable).filter_by(
        task_id=task_id,
        agent_type="reflector"
    ).first()

    if not reflection:
        raise HTTPException(404, "No reflection")

    next_task = db.query(models.TasksTable).filter(
        models.TasksTable.goal_id == task.goal_id,
        models.TasksTable.status == "pending"
    ).order_by(models.TasksTable.created_at).first()

    if not next_task:
        return {"message": "No next task"}

    decision = await replanTask(
        lastTask=task.description,
        reflection=reflection.output_text,
        nextTask=next_task.description
    )

    db.add(models.AgentOutputsTable(
        task_id=task_id,
        agent_type="replanner",
        output_text=decision
    ))

    action = decision["action"]

    if action == "keep":
        return

    if action == "skip":
        next_task.status = "skipped"
        db.commit()
        return

    if action == "edit":
        next_task.description = decision["edited_task"]
        db.commit()
        return

    if action == "split":
        next_task.status = "skipped"
        for text in decision["new_tasks"]:
            db.add(models.TasksTable(
                user_id=next_task.user_id,
                goal_id=next_task.goal_id,
                description=text,
                parent_task_id=next_task.id
            ))

    db.commit()
    return decision