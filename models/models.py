# app/models/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nickname = Column(String(50), nullable=False, unique=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con sesiones
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")

class Sesion(Base):
    __tablename__ = 'sesiones'
    
    id_sesion = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    nombre_sesion = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    total_minutos_acumulados = Column(Integer, default=0)
    
    # Relaciones
    usuario = relationship("Usuario", back_populates="sesiones")
    pomodoros = relationship("Pomodoro", back_populates="sesion", cascade="all, delete-orphan")

class Pomodoro(Base):
    __tablename__ = 'pomodoros'
    
    id_pomodoro = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_sesion = Column(Integer, ForeignKey('sesiones.id_sesion', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    duracion_actividad = Column(Integer, nullable=False)  # minutos activos
    duracion_descanso = Column(Integer, nullable=False)   # minutos de descanso
    inicio = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=True)
    estado = Column(String(20), default='en_progreso')
    minutos_completados = Column(Integer, default=0)
    
    # Restricción CHECK para estado
    __table_args__ = (
        CheckConstraint(
            "estado IN ('completado', 'cancelado', 'en_progreso')", 
            name='ck_pomodoro_estado'
        ),
    )
    
    # Relación
    sesion = relationship("Sesion", back_populates="pomodoros")