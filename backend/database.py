from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from decouple import config

engine = create_engine(config("DATABASE_URL"))
sessionDB = sessionmaker(autoflush=False, bind=engine)