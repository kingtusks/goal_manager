from fastapi import Depends, FastAPI
from models import UserPydantic, UserTable, Base
from database import sessionDB, engine
from sqlalchemy.orm import Session

app = FastAPI()
#Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionDB()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"ok": True}

