from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class UserPydantic(BaseModel):
    user_id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class UserTable(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)  # hash later
    
class GoalsPydantic(BaseModel):
    id: Optional[int] = None
    user_id: int
    goal: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class GoalsTable(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    goal = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

#--

class TasksPydantic(BaseModel):
    user_id: int
    goal_id: int
    description: str
    status: str = "pending"
    scheduled_day: Optional[int]
    estimated_minutes: Optional[int]

    class Config:
        orm_mode = True

class TasksTable(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    goal_id = Column(Integer, index=True, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    scheduled_day = Column(Integer)
    estimated_minutes = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

class AgentOutputsPydantic(BaseModel):
    #id: int
    task_id: int #kept as 1 for now
    agent_type: str #reflector executor planner
    output_text: str 
    #created_at: datetime

    class Config:
        orm_mode = True

class AgentOutputsTable(Base):
    __tablename__ = "agent_outputs"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, index=True)
    agent_type = Column(String)
    output_text = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) #autogens this cus func.now() calls it



    
