from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import sessionDB, engine
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agents.executor import executePlan
from agents.planner import makePlan
from agents.reflector import reflectPlan
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

class AgentRequest(BaseModel):
    plan: str

class PlannerRequest(BaseModel):
    goal: str

class ReflectorRequest(BaseModel):
    result: str  

@app.get("/") #home (placeholder)
async def root():
    return {"ok": True}

@app.get("/goals") #r
async def get_all_goals(db: Session = Depends(get_db)):
    db_goals = db.query(models.GoalsTable).all()
    return db_goals 

@app.get("/goal/{uid}") #r
async def get_goals_from_userid(user_id: int, db: Session = Depends(get_db)):  
    db_goals = db.query(models.GoalsTable).filter(models.GoalsTable.user_id == user_id).all()  
    if db_goals:
        return db_goals
    raise HTTPException(status_code=404, detail=f"No goals found for user id: {user_id}")

@app.get("/goal/{id}") #r
async def get_goals_from_id(id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == id).first()
    if db_goal:
        return db_goal
    raise HTTPException(status_code=404, detail=f"No goals found with id: {id}") 

@app.post("/creategoal") #c
async def make_goal(goal: models.GoalsPydantic, db: Session = Depends(get_db)):
    db.add(models.GoalsTable(**goal.model_dump()))
    db.commit()
    return {"done": "i think"}

@app.delete("/deletegoal") #d
async def delete_goal(id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == id).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()
        return {"id of goal deleted": id}
    raise HTTPException(status_code=404, detail=f"No goals found with id: {id}")  

@app.post("/agent/execute")
async def execute_plan(request: AgentRequest):
    try:
        result = await executePlan(request.plan)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/plan")
async def create_plan(request: PlannerRequest):
    try:
        result = await makePlan(request.goal)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/reflect")
async def reflect_on_result(request: ReflectorRequest):
    try:
        result = await reflectPlan(request.result)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))