import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from utils.database import engine, Base
from models.models import Usuario, Sesion, Pomodoro
from routers.routers import router

app = FastAPI(
    title="Pomodoro API",
    description="API para gestión de técnica Pomodoro",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a Pomodoro API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando correctamente"}