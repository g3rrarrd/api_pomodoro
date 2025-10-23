import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from utils.database import engine, Base
from models.models import Usuario, Sesion, Pomodoro, PomodoroRule, PomodoroType, PauseTracker
from routers.routers import router


### Descomentar la siguiente línea para eliminar todas las tablas (¡CUIDADO!)
#Base.metadata.drop_all(bind=engine)

### Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pomodoro API",
    description="API para gestión de técnica Pomodoro con seguimiento detallado",
    version="0.5.0"
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a Pomodoro API",
        "version": "0.5.0",
        "description": "Sistema de productividad con técnica Pomodoro"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "message": "API funcionando correctamente",
        "database": "conectado"
    }

@app.get("/info")
def get_info():
    return {
        "name": "Pomodoro API",
        "version": "0.5.0",
        "models": [
            "Usuario", "Sesion", "Pomodoro", 
            "PomodoroRule", "PomodoroType", "PauseTracker"
        ],
        "endpoints": [
            "/usuarios/",
            "/sesiones/", 
            "/pomodoros/",
            "/pausas/",
            "/reglas-pomodoro/",
            "/tipos-pomodoro/",
            "/estadisticas/"
        ]
    }