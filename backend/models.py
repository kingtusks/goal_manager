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


'''
class TasksPydantic(BaseModel):

class TasksTable(Base):

class AgentOutputsPydantic(BaseModel):

class AgentOutputsTable(Base):

class ReflectionsPydantic(BaseModel):

class ReflectionsTable(Base):
'''

    
