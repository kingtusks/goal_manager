from pydantic import BaseModel
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime

Base = declarative_base()

class UserPydantic(BaseModel):
    userid: int
    user: str
    email: str
    password: str

class UserTable(Base): 
    __tablename__ = "users"

    userid = Column(Integer, primary_key=True, index=True)
    user = Column(String(20), unique=True)
    email = Column(String)
    password = Column(String) #(placeholder) hash this later
    
class GoalsPydantic(BaseModel):
    userid: int
    goal: str
    date: datetime

class GoalsTable(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, index=True)
    goal = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())

class TasksPydantic(BaseModel):
    userid: int
    goal: str
    task_history: str
    duration: int

class TasksTable(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(Integer, index=True) #needs to map to the userid
    goal = Column(String) #needs to map to a goal in GoalsTable
    task_history = Column(String) #(placeholder) use json maybe
    last_message = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Integer) #(placeholder) need a scale for this

'''
class AgentOutputsPydantic(BaseModel):

class AgentOutputsTable(Base):

class ReflectionsPydantic(BaseModel):

class ReflectionsTable(Base):
'''

    
