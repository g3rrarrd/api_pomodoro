
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from utils.database import get_db
from models.models import Usuario, Sesion, Pomodoro

router = APIRouter()

# ============================================================
# ENDPOINTS PARA USUARIOS
# ============================================================

@router.post("/usuarios/")
def crear_usuario(nickname: str, db: Session = Depends(get_db)):
    try:
        # Verificar si el nickname ya existe
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
                "id_usuario": nuevo_usuario.id_usuario,
                "nickname": nuevo_usuario.nickname,
                "fecha_creacion": nuevo_usuario.fecha_creacion
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
            "id_usuario": u.id_usuario,
            "nickname": u.nickname,
            "fecha_creacion": u.fecha_creacion
        } for u in usuarios]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

# ============================================================
# ENDPOINTS PARA SESIONES
# ============================================================

@router.post("/sesiones/")
def crear_sesion(id_usuario: int, nombre_sesion: str, descripcion: str = None, db: Session = Depends(get_db)):
    try:
        # Verificar que el usuario existe
        usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        nueva_sesion = Sesion(
            id_usuario=id_usuario,
            nombre_sesion=nombre_sesion,
            descripcion=descripcion
        )
        db.add(nueva_sesion)
        db.commit()
        db.refresh(nueva_sesion)
        
        return {
            "message": "Sesión creada exitosamente",
            "sesion": {
                "id_sesion": nueva_sesion.id_sesion,
                "id_usuario": nueva_sesion.id_usuario,
                "nombre_sesion": nueva_sesion.nombre_sesion,
                "descripcion": nueva_sesion.descripcion,
                "fecha_creacion": nueva_sesion.fecha_creacion
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear sesión: {str(e)}")

@router.get("/sesiones/usuario/{id_usuario}")
def listar_sesiones_usuario(id_usuario: int, db: Session = Depends(get_db)):
    try:
        sesiones = db.query(Sesion).filter(Sesion.id_usuario == id_usuario).all()
        return [{
            "id_sesion": s.id_sesion,
            "nombre_sesion": s.nombre_sesion,
            "descripcion": s.descripcion,
            "fecha_creacion": s.fecha_creacion,
            "total_minutos_acumulados": s.total_minutos_acumulados
        } for s in sesiones]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sesiones: {str(e)}")

# ============================================================
# ENDPOINTS PARA POMODOROS
# ============================================================

@router.post("/pomodoros/")
def iniciar_pomodoro(
    id_sesion: int, 
    duracion_actividad: int = 25, 
    duracion_descanso: int = 5, 
    db: Session = Depends(get_db)
):
    try:
        # Verificar que la sesión existe
        sesion = db.query(Sesion).filter(Sesion.id_sesion == id_sesion).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        nuevo_pomodoro = Pomodoro(
            id_sesion=id_sesion,
            duracion_actividad=duracion_actividad,
            duracion_descanso=duracion_descanso,
            inicio=datetime.now(timezone.utc),  # Usar UTC para consistencia
            estado='en_progreso'
        )
        db.add(nuevo_pomodoro)
        db.commit()
        db.refresh(nuevo_pomodoro)
        
        return {
            "message": "Pomodoro iniciado exitosamente",
            "pomodoro": {
                "id_pomodoro": nuevo_pomodoro.id_pomodoro,
                "id_sesion": nuevo_pomodoro.id_sesion,
                "duracion_actividad": nuevo_pomodoro.duracion_actividad,
                "duracion_descanso": nuevo_pomodoro.duracion_descanso,
                "inicio": nuevo_pomodoro.inicio,
                "estado": nuevo_pomodoro.estado
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al iniciar pomodoro: {str(e)}")

@router.put("/pomodoros/{id_pomodoro}/completar")
def completar_pomodoro(id_pomodoro: int, db: Session = Depends(get_db)):
    try:
        pomodoro = db.query(Pomodoro).filter(Pomodoro.id_pomodoro == id_pomodoro).first()
        if not pomodoro:
            raise HTTPException(status_code=404, detail="Pomodoro no encontrado")
        
        if pomodoro.estado != 'en_progreso':
            raise HTTPException(status_code=400, detail="El pomodoro no está en progreso")
        
        # Obtener el tiempo actual en UTC para consistencia
        tiempo_actual = datetime.now(timezone.utc)
        
        # Asegurarnos de que ambos datetime tengan timezone
        inicio_con_timezone = pomodoro.inicio
        if inicio_con_timezone.tzinfo is None:
            inicio_con_timezone = inicio_con_timezone.replace(tzinfo=timezone.utc)
        
        # Calcular minutos completados automáticamente
        tiempo_transcurrido = tiempo_actual - inicio_con_timezone
        minutos_completados = int(tiempo_transcurrido.total_seconds() / 60)
        
        # Si el tiempo excede la duración planeada, usar la duración planeada
        if minutos_completados > pomodoro.duracion_actividad:
            minutos_completados = pomodoro.duracion_actividad
        
        # Asegurarnos de que al menos se cuente 1 minuto
        if minutos_completados < 1:
            minutos_completados = 1
        
        # Actualizar pomodoro
        pomodoro.estado = 'completado'
        pomodoro.minutos_completados = minutos_completados
        pomodoro.fin = tiempo_actual
        
        # Actualizar minutos acumulados en la sesión
        sesion = db.query(Sesion).filter(Sesion.id_sesion == pomodoro.id_sesion).first()
        sesion.total_minutos_acumulados += minutos_completados
        
        db.commit()
        
        return {
            "message": "Pomodoro completado exitosamente",
            "pomodoro": {
                "id_pomodoro": pomodoro.id_pomodoro,
                "minutos_completados": pomodoro.minutos_completados,
                "tiempo_transcurrido_minutos": minutos_completados,
                "estado": pomodoro.estado,
                "fin": pomodoro.fin
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar pomodoro: {str(e)}")

@router.put("/pomodoros/{id_pomodoro}/cancelar")
def cancelar_pomodoro(id_pomodoro: int, db: Session = Depends(get_db)):
    try:
        pomodoro = db.query(Pomodoro).filter(Pomodoro.id_pomodoro == id_pomodoro).first()
        if not pomodoro:
            raise HTTPException(status_code=404, detail="Pomodoro no encontrado")
        
        if pomodoro.estado != 'en_progreso':
            raise HTTPException(status_code=400, detail="El pomodoro no está en progreso")
        
        # Obtener el tiempo actual en UTC para consistencia
        tiempo_actual = datetime.now(timezone.utc)
        
        # Asegurarnos de que ambos datetime tengan timezone
        inicio_con_timezone = pomodoro.inicio
        if inicio_con_timezone.tzinfo is None:
            inicio_con_timezone = inicio_con_timezone.replace(tzinfo=timezone.utc)
        
        # Calcular minutos completados hasta el momento de cancelación
        tiempo_transcurrido = tiempo_actual - inicio_con_timezone
        minutos_completados = int(tiempo_transcurrido.total_seconds() / 60)
        
        # Asegurarnos de que al menos se cuente 1 minuto
        if minutos_completados < 1:
            minutos_completados = 1
        
        # Actualizar pomodoro como cancelado
        pomodoro.estado = 'cancelado'
        pomodoro.minutos_completados = minutos_completados
        pomodoro.fin = tiempo_actual
        
        # También actualizar minutos acumulados en la sesión (opcional)
        sesion = db.query(Sesion).filter(Sesion.id_sesion == pomodoro.id_sesion).first()
        sesion.total_minutos_acumulados += minutos_completados
        
        db.commit()
        
        return {
            "message": "Pomodoro cancelado exitosamente",
            "pomodoro": {
                "id_pomodoro": pomodoro.id_pomodoro,
                "minutos_completados": pomodoro.minutos_completados,
                "tiempo_transcurrido_minutos": minutos_completados,
                "estado": pomodoro.estado,
                "fin": pomodoro.fin
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al cancelar pomodoro: {str(e)}")
@router.get("/pomodoros/sesion/{id_sesion}")
def listar_pomodoros_sesion(id_sesion: int, db: Session = Depends(get_db)):
    try:
        pomodoros = db.query(Pomodoro).filter(Pomodoro.id_sesion == id_sesion).all()
        return [{
            "id_pomodoro": p.id_pomodoro,
            "duracion_actividad": p.duracion_actividad,
            "duracion_descanso": p.duracion_descanso,
            "inicio": p.inicio,
            "fin": p.fin,
            "estado": p.estado,
            "minutos_completados": p.minutos_completados
        } for p in pomodoros]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pomodoros: {str(e)}")

# ============================================================
# ENDPOINTS PARA ESTADÍSTICAS
# ============================================================

@router.get("/estadisticas/usuario/{id_usuario}")
def obtener_estadisticas_usuario(id_usuario: int, db: Session = Depends(get_db)):
    try:
        from sqlalchemy import func 
        
        # Total de minutos por usuario
        total_minutos = db.query(
            func.sum(Sesion.total_minutos_acumulados).label('total_minutos')
        ).filter(
            Sesion.id_usuario == id_usuario
        ).scalar() or 0
        
        # Total de sesiones
        total_sesiones = db.query(Sesion).filter(
            Sesion.id_usuario == id_usuario
        ).count()
        
        # Total de pomodoros completados
        total_pomodoros = db.query(Pomodoro).join(Sesion).filter(
            Sesion.id_usuario == id_usuario,
            Pomodoro.estado == 'completado'
        ).count()
        
        return {
            "id_usuario": id_usuario,
            "total_minutos": total_minutos,
            "total_sesiones": total_sesiones,
            "total_pomodoros_completados": total_pomodoros
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")