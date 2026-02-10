#will take executor output and create quizzes/etc in react
from ollama import AsyncClient
from decouple import config
import os

async def constructor(executorOutput: str):
    