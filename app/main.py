from fastapi import FastAPI
from app.database import engine, Base
import app.models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Notes API",
    description="API de notas inteligentes con autenticación JWT y resumen por LLM",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Smart Notes API is running!"}