import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from utils.database import engine, Base
from models.models import Usuario, Sesion, Pomodoro, PomodoroRule, PomodoroType, PauseTracker
from routers.routers import router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

origins = os.getenv("ALLOWED_ORIGINS", "")

### Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)


app_kwargs = {
    "title": "Pomodoro API",
    "description": "API para gestión de técnica Pomodoro con seguimiento detallado",
    "version": "1.0.4"
}


if ENVIRONMENT == "production":
    print("Iniciando en modo PRODUCCIÓN: Documentación (Swagger/ReDoc) desactivada.")
    app_kwargs["docs_url"] = None  # Desactiva /docs
    app_kwargs["redoc_url"] = None # Desactiva /redoc
else:
    print("Iniciando en modo DESARROLLO: Documentación (Swagger/ReDoc) activada.")


app = FastAPI(**app_kwargs)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a Pomodoro API",
        "version": "1.0.4",
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
        "version": "1.0.3",
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