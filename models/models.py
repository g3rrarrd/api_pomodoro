from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.database import Base
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional

class Usuario(Base):
    __tablename__ = 'tbl_users'
    
    id_user = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nickname = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación con sesiones 
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")

class Sesion(Base):
    __tablename__ = 'tbl_sessions'
    
    id_session = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_user = Column(Integer, ForeignKey('tbl_users.id_user', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    session_name = Column(String(100), nullable=False)
    total_focus_seconds = Column(Integer, default=0)
    total_break_seconds = Column(Integer, default=0)
    total_pause_seconds = Column(Integer, default=0)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones 
    usuario = relationship("Usuario", back_populates="sesiones")
    pomodoros = relationship("Pomodoro", back_populates="sesion", cascade="all, delete-orphan")

class PomodoroRule(Base):
    __tablename__ = 'tbl_pomodoro_rules'
    
    id_pomodoro_rule = Column(Integer, primary_key=True, autoincrement=True, index=True)
    difficulty_level = Column(String(50), nullable=False, unique=True)  # CORREGIDO: unique=True
    focus_duration = Column(Integer, nullable=False) 
    break_duration = Column(Integer, nullable=False)   
    description = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relación 
    pomodoros = relationship("Pomodoro", back_populates="rule")

class PomodoroType(Base):
    __tablename__ = 'tbl_pomodoro_types'
    
    id_pomodoro_type = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name_type = Column(String(50), nullable=False, unique=True)
    
    # Relación 
    pomodoros = relationship("Pomodoro", back_populates="type")

class Pomodoro(Base):
    __tablename__ = 'tbl_pomodoro_details'
    
    id_pomodoro_detail = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_session = Column(Integer, ForeignKey('tbl_sessions.id_session', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_pomodoro_rule = Column(Integer, ForeignKey('tbl_pomodoro_rules.id_pomodoro_rule', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    id_pomodoro_type = Column(Integer, ForeignKey('tbl_pomodoro_types.id_pomodoro_type', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    event_type = Column(String(20), nullable=False) 
    planned_duration = Column(Integer, nullable=False)
    is_completed = Column(Boolean, default=False)
    focus_time = Column(Integer, default=0)
    break_time = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('focus', 'break')", 
            name='ck_pomodoro_event_type'
        ),
    )
    
    # Relaciones
    sesion = relationship("Sesion", back_populates="pomodoros")
    rule = relationship("PomodoroRule", back_populates="pomodoros")
    type = relationship("PomodoroType", back_populates="pomodoros")
    pauses = relationship("PauseTracker", back_populates="pomodoro", cascade="all, delete-orphan")

class PauseTracker(Base):
    __tablename__ = 'tbl_pause_tracking' 
    
    id_pause = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_pomodoro_detail = Column(Integer, ForeignKey('tbl_pomodoro_details.id_pomodoro_detail', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    pause_start = Column(DateTime(timezone=True), nullable=False)
    pause_end = Column(DateTime(timezone=True), nullable=True)
    total_pause_seconds = Column(Integer, default=0)
    created_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relación 
    pomodoro = relationship("Pomodoro", back_populates="pauses")

class PomodoroCreateRequest(BaseModel):
    id_session: int
    id_pomodoro_rule: int
    id_pomodoro_type: int
    event_type: str 
    planned_duration: int
    is_completed: bool = False
    notes: Optional[str] = None

class PomodoroUpdateRequest(BaseModel):
    is_completed: bool
    notes: str
    focus_seconds: int = 0
    break_seconds: int = 0