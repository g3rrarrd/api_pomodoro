from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone

from utils.database import get_db
from models.models import Usuario, Sesion, Pomodoro, PomodoroRule, PomodoroType, PauseTracker

router = APIRouter()

# ============================================================
# ENDPOINTS PARA USUARIOS
# ============================================================

@router.post("/usuarios/")
def crear_usuario(nickname: str, db: Session = Depends(get_db)):
    try:
        
        usuario_existente = db.query(Usuario).filter(Usuario.nickname == nickname).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="El nickname ya está registrado")
        
        nuevo_usuario = Usuario(nickname=nickname)
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        return {
            "message": "Usuario creado exitosamente",
            "usuario": {
                "id_user": nuevo_usuario.id_user,
                "nickname": nuevo_usuario.nickname,
                "created_date": nuevo_usuario.created_date
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")

@router.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db)):
    try:
        usuarios = db.query(Usuario).all()
        return [{
            "id_user": u.id_user,
            "nickname": u.nickname,
            "created_date": u.created_date
        } for u in usuarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")
    
@router.get("/usuarios/{id_user}")
def obtener_usuario(id_user: int, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.id_user == id_user).first()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id_user": usuario.id_user,
            "nickname": usuario.nickname,
            "created_date": usuario.created_date
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

@router.get("/usuarios/nickname/{nickname}")
def obtener_usuario_por_nickname(nickname: str, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.nickname == nickname).first()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id_user": usuario.id_user,
            "nickname": usuario.nickname,
            "created_date": usuario.created_date
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

# ============================================================
# ENDPOINTS PARA SESIONES
# ============================================================

@router.post("/sesiones/")
def crear_sesion(id_user: int, session_name: str, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.id_user == id_user).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        nueva_sesion = Sesion(
            id_user=id_user,
            session_name=session_name
        )
        db.add(nueva_sesion)
        db.commit()
        db.refresh(nueva_sesion)
        
        return {
            "message": "Sesión creada exitosamente",
            "sesion": {
                "id_session": nueva_sesion.id_session,
                "id_user": nueva_sesion.id_user,
                "session_name": nueva_sesion.session_name,
                "created_date": nueva_sesion.created_date
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear sesión: {str(e)}")

@router.get("/sesiones/usuario/{id_user}")
def listar_sesiones_usuario(id_user: int, db: Session = Depends(get_db)):
    try:
        sesiones = db.query(Sesion).filter(Sesion.id_user == id_user).all()
        return [{
            "id_session": s.id_session,
            "session_name": s.session_name,
            "total_focus_minutes": s.total_focus_minutes,
            "total_break_minutes": s.total_break_minutes,
            "total_pause_minutes": s.total_pause_minutes,
            "created_date": s.created_date
        } for s in sesiones]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sesiones: {str(e)}")

@router.put("/sesiones/{id_session}/total_focus")
def actualizar_total_focus(id_session: int, minutos: int, db: Session = Depends(get_db)):
    try:
        sesion = db.query(Sesion).filter(Sesion.id_session == id_session).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        sesion.total_focus_minutes += minutos
        db.commit()
        
        return {
            "message": "Total de minutos de foco actualizado exitosamente",
            "id_session": sesion.id_session,
            "total_focus_minutes": sesion.total_focus_minutes
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar total de foco: {str(e)}")

@router.put("/sesiones/{id_session}/total_break")
def actualizar_total_break(id_session: int, minutos: int, db: Session = Depends(get_db)):
    try:
        sesion = db.query(Sesion).filter(Sesion.id_session == id_session).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        sesion.total_break_minutes += minutos
        db.commit()
        
        return {
            "message": "Total de minutos de descanso actualizado exitosamente",
            "id_session": sesion.id_session,
            "total_break_minutes": sesion.total_break_minutes
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar total de descanso: {str(e)}")

# ============================================================
# ENDPOINTS PARA POMODOROS
# ============================================================

@router.post("/pomodoros/")
def iniciar_pomodoro(
    id_session: int, 
    id_pomodoro_rule: int,
    id_pomodoro_type: int,
    event_type: str = "focus",
    planned_duration: int = 25,
    notes: str = None,
    db: Session = Depends(get_db)):
    try:
        
        sesion = db.query(Sesion).filter(Sesion.id_session == id_session).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        
        regla = db.query(PomodoroRule).filter(PomodoroRule.id_pomodoro_rule == id_pomodoro_rule).first()
        if not regla:
            raise HTTPException(status_code=404, detail="Regla de pomodoro no encontrada")
        
        
        tipo = db.query(PomodoroType).filter(PomodoroType.id_pomodoro_type == id_pomodoro_type).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de pomodoro no encontrado")
        
        
        if event_type not in ["focus", "break", "pause"]:
            raise HTTPException(status_code=400, detail="Event type debe ser 'focus', 'break' o 'pause'")
        
        nuevo_pomodoro = Pomodoro(
            id_session=id_session,
            id_pomodoro_rule=id_pomodoro_rule,
            id_pomodoro_type=id_pomodoro_type,
            event_type=event_type,
            planned_duration=planned_duration,
            pomodoro_start=datetime.now(timezone.utc),
            notes=notes,
            is_completed=False
        )
        db.add(nuevo_pomodoro)
        db.commit()
        db.refresh(nuevo_pomodoro)
        
        return {
            "message": "Pomodoro iniciado exitosamente",
            "pomodoro": {
                "id_pomodoro_detail": nuevo_pomodoro.id_pomodoro_detail,
                "id_session": nuevo_pomodoro.id_session,
                "event_type": nuevo_pomodoro.event_type,
                "planned_duration": nuevo_pomodoro.planned_duration,
                "pomodoro_start": nuevo_pomodoro.pomodoro_start,
                "is_completed": nuevo_pomodoro.is_completed,
                "created_date": nuevo_pomodoro.created_date
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al iniciar pomodoro: {str(e)}")

@router.put("/pomodoros/{id_pomodoro_detail}/completar")
def completar_pomodoro(id_pomodoro_detail: int, db: Session = Depends(get_db)):
    try:
        pomodoro = db.query(Pomodoro).filter(Pomodoro.id_pomodoro_detail == id_pomodoro_detail).first()
        if not pomodoro:
            raise HTTPException(status_code=404, detail="Pomodoro no encontrado")
        
        if pomodoro.is_completed:
            raise HTTPException(status_code=400, detail="El pomodoro ya está completado")
        
        tiempo_actual = datetime.now(timezone.utc)
        tiempo_transcurrido = tiempo_actual - pomodoro.pomodoro_start
        duracion_real = int(tiempo_transcurrido.total_seconds() / 60)
        
        pomodoro.is_completed = True
        pomodoro.pomodoro_end = tiempo_actual
        pomodoro.duration = duracion_real
        
        sesion = db.query(Sesion).filter(Sesion.id_session == pomodoro.id_session).first()
        if pomodoro.event_type == "focus":
            sesion.total_focus_minutes += duracion_real
        elif pomodoro.event_type == "break":
            sesion.total_break_minutes += duracion_real
        elif pomodoro.event_type == "pause":
            sesion.total_pause_minutes += duracion_real
        
        db.commit()
        
        return {
            "message": "Pomodoro completado exitosamente",
            "pomodoro": {
                "id_pomodoro_detail": pomodoro.id_pomodoro_detail,
                "event_type": pomodoro.event_type,
                "planned_duration": pomodoro.planned_duration,
                "actual_duration": pomodoro.duration,
                "pomodoro_start": pomodoro.pomodoro_start,
                "pomodoro_end": pomodoro.pomodoro_end,
                "is_completed": pomodoro.is_completed
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar pomodoro: {str(e)}")

@router.get("/pomodoros/sesion/{id_session}")
def listar_pomodoros_sesion(id_session: int, db: Session = Depends(get_db)):
    try:
        pomodoros = db.query(Pomodoro).filter(Pomodoro.id_session == id_session).all()
        return [{
            "id_pomodoro_detail": p.id_pomodoro_detail,
            "id_pomodoro_rule": p.id_pomodoro_rule,
            "id_pomodoro_type": p.id_pomodoro_type,
            "event_type": p.event_type,
            "planned_duration": p.planned_duration,
            "actual_duration": p.duration,
            "pomodoro_start": p.pomodoro_start,
            "pomodoro_end": p.pomodoro_end,
            "is_completed": p.is_completed,
            "notes": p.notes,
            "created_date": p.created_date
        } for p in pomodoros]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pomodoros: {str(e)}")

@router.put("/sesiones/{id_session}/total_pause")
def actualizar_total_pause(id_session: int, minutos: int, db: Session = Depends(get_db)):
    try:
        sesion = db.query(Sesion).filter(Sesion.id_session == id_session).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        sesion.total_pause_minutes += minutos
        db.commit()
        
        return {
            "message": "Total de minutos de pausa actualizado exitosamente",
            "id_session": sesion.id_session,
            "total_pause_minutes": sesion.total_pause_minutes
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar total de pausa: {str(e)}")

# ============================================================
# ENDPOINTS PARA PAUSAS
# ============================================================

@router.post("/pausas/")
def iniciar_pausa(id_pomodoro_detail: int, db: Session = Depends(get_db)):
    try:
        
        pomodoro = db.query(Pomodoro).filter(Pomodoro.id_pomodoro_detail == id_pomodoro_detail).first()
        if not pomodoro:
            raise HTTPException(status_code=404, detail="Pomodoro no encontrado")
        
        nueva_pausa = PauseTracker(
            id_pomodoro_detail=id_pomodoro_detail,
            pause_start=datetime.now(timezone.utc)
        )
        db.add(nueva_pausa)
        db.commit()
        db.refresh(nueva_pausa)
        
        return {
            "message": "Pausa iniciada exitosamente",
            "pausa": {
                "id_pause": nueva_pausa.id_pause,
                "id_pomodoro_detail": nueva_pausa.id_pomodoro_detail,
                "pause_start": nueva_pausa.pause_start
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al iniciar pausa: {str(e)}")

@router.put("/pausas/{id_pause}/finalizar")
def finalizar_pausa(id_pause: int, db: Session = Depends(get_db)):
    try:
        pausa = db.query(PauseTracker).filter(PauseTracker.id_pause == id_pause).first()
        if not pausa:
            raise HTTPException(status_code=404, detail="Pausa no encontrada")
        
        if pausa.pause_end:
            raise HTTPException(status_code=400, detail="La pausa ya está finalizada")
        
        tiempo_actual = datetime.now(timezone.utc)
        tiempo_transcurrido = tiempo_actual - pausa.pause_start
        minutos_pausa = int(tiempo_transcurrido.total_seconds() / 60)
        
        pausa.pause_end = tiempo_actual
        pausa.total_pause_minutes = minutos_pausa
        
        pomodoro = db.query(Pomodoro).filter(Pomodoro.id_pomodoro_detail == pausa.id_pomodoro_detail).first()
        sesion = db.query(Sesion).filter(Sesion.id_session == pomodoro.id_session).first()
        sesion.total_pause_minutes += minutos_pausa
        
        db.commit()
        
        return {
            "message": "Pausa finalizada exitosamente",
            "pausa": {
                "id_pause": pausa.id_pause,
                "total_pause_minutes": pausa.total_pause_minutes,
                "pause_start": pausa.pause_start,
                "pause_end": pausa.pause_end
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al finalizar pausa: {str(e)}")

# ============================================================
# ENDPOINTS PARA REGLAS Y TIPOS
# ============================================================

@router.get("/reglas-pomodoro/")
def listar_reglas_pomodoro(db: Session = Depends(get_db)):
    try:
        reglas = db.query(PomodoroRule).all()
        return [{
            "id_pomodoro_rule": r.id_pomodoro_rule,
            "difficulty_level": r.difficulty_level,
            "focus_duration": r.focus_duration,
            "break_duration": r.break_duration,
            "description": r.description
        } for r in reglas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener reglas: {str(e)}")

@router.get("/tipos-pomodoro/")
def listar_tipos_pomodoro(db: Session = Depends(get_db)):
    try:
        tipos = db.query(PomodoroType).all()
        return [{
            "id_pomodoro_type": t.id_pomodoro_type,
            "name_type": t.name_type
        } for t in tipos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tipos: {str(e)}")

# ============================================================
# ENDPOINTS PARA ESTADÍSTICAS
# ============================================================

@router.get("/estadisticas/usuario/{id_user}")
def obtener_estadisticas_usuario(id_user: int, db: Session = Depends(get_db)):
    try:
        
        total_focus = db.query(
            func.sum(Sesion.total_focus_minutes).label('total_focus')
        ).filter(
            Sesion.id_user == id_user
        ).scalar() or 0
        
        total_break = db.query(
            func.sum(Sesion.total_break_minutes).label('total_break')
        ).filter(
            Sesion.id_user == id_user
        ).scalar() or 0
        
        total_pause = db.query(
            func.sum(Sesion.total_pause_minutes).label('total_pause')
        ).filter(
            Sesion.id_user == id_user
        ).scalar() or 0
        
        total_sesiones = db.query(Sesion).filter(
            Sesion.id_user == id_user
        ).count()
        
        total_pomodoros = db.query(Pomodoro).join(Sesion).filter(
            Sesion.id_user == id_user,
            Pomodoro.is_completed == True
        ).count()
        
        return {
            "id_user": id_user,
            "total_focus_minutes": total_focus,
            "total_break_minutes": total_break,
            "total_pause_minutes": total_pause,
            "total_sesiones": total_sesiones,
            "total_pomodoros_completados": total_pomodoros
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")