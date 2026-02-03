from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import sessionDB, engine
from sqlalchemy.orm import Session
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
    if db_goals:
        return db_goals
    raise HTTPException(status_code=404, detail="No Goals Found")

@app.get("/goal/{uid}") #r
async def get_goals_from_userid(userid: int, db: Session = Depends(get_db)):
    db_goals = db.query(models.GoalsTable).filter(models.GoalsTable.userid == userid).all()
    if db_goals:
        return db_goals
    raise HTTPException(status_code=404, detail=f"No goals found for user id: {userid}")

@app.get("/goal/{id}") #r
async def get_goals_from_id(id: int, db: Session = Depends(get_db)):
    db_goal = db.query(models.GoalsTable).filter(models.GoalsTable.id == id).first()
    if db_goal:
        return db_goal
    raise HTTPException(status_code=404, detail="No goals found with id: {id}")

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
    raise HTTPException(status_code=404, detail="No goals found with id: {id}")


