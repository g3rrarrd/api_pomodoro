from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timezone, timedelta

from utils.database import get_db
from models.models import Usuario, Sesion, Pomodoro, PomodoroRule, PomodoroType, PauseTracker
from utils.auth_utils import (
    generate_verification_code, create_verification_token,
    verify_verification_token, send_verification_email,
    verification_cache, VERIFICATION_EXPIRE_MINUTES, send_recovery_email,
    send_username_reminder_email
)

router = APIRouter()

# ============================================================
# ENDPOINTS PARA USUARIOS
# ============================================================

@router.get("/usuarios/")
def listar_usuarios(db: Session = Depends(get_db)):
    try:
        usuarios = db.query(Usuario).all()
        return [{
            "id_user": u.id_user,
            "email": u.email,
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
            "email" : usuario.email,
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
            "email" : usuario.email,
            "nickname": usuario.nickname,
            "created_date": usuario.created_date
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

@router.get("/usuarios/email/{email}")
def obtener_usuario_por_email(email: str, db: Session = Depends(get_db)):
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return {
            "id_user": usuario.id_user,
            "email": usuario.email,
            "nickname": usuario.nickname,
            "created_date": usuario.created_date
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")

# ============================================================
# ENDPOINTS DE VERIFICACION
# ============================================================

@router.post("/auth/start-registration")
def iniciar_registro(
    request: Request,
    email: str,
    nickname: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Inicia el proceso de registro enviando código de verificación"""
    try:
        # Validaciones básicas
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Email inválido")
        
        if not nickname or len(nickname) < 2:
            raise HTTPException(status_code=400, detail="Nickname debe tener al menos 2 caracteres")

        # Verificar si el email ya está registrado
        usuario_existente = db.query(Usuario).filter(Usuario.email == email).first()
        if usuario_existente:
            raise HTTPException(status_code=400, detail="El email ya está registrado")

        # Verificar si el nickname ya está en uso
        nickname_existente = db.query(Usuario).filter(Usuario.nickname == nickname).first()
        if nickname_existente:
            raise HTTPException(status_code=400, detail="El nickname ya está en uso")

        # Generar código de verificación
        verification_code = generate_verification_code()
        
        # Crear JWT temporal con los datos del usuario
        verification_data = {
            "email": email,
            "nickname": nickname,
            "code": verification_code,
            "type": "registration"
        }
        
        verification_token = create_verification_token(verification_data)
        
        # Guardar en cache para verificación rápida
        verification_cache[email] = {
            "token": verification_token,
            "code": verification_code,
            "nickname": nickname,
            "created_at": datetime.now(timezone.utc),
            "attempts": 0
        }

        # Enviar código por email (en background)
        background_tasks.add_task(send_verification_email, email, verification_code)

        return {
            "message": "Código de verificación enviado a tu email",
            "email": email,
            "expires_in_minutes": VERIFICATION_EXPIRE_MINUTES,
            "note": "Usa este código para completar el registro en /auth/verify"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar registro: {str(e)}")

@router.post("/auth/verify")
def verificar_y_registrar(
    email: str,
    code: str,
    db: Session = Depends(get_db)
):
    """Verifica el código y crea el usuario"""
    try:
        # Buscar en cache
        cached_data = verification_cache.get(email)
        
        if not cached_data:
            raise HTTPException(status_code=400, detail="Código no encontrado o expirado. Inicia el registro nuevamente.")

        # Verificar intentos
        if cached_data["attempts"] >= 3:
            del verification_cache[email]
            raise HTTPException(status_code=400, detail="Demasiados intentos fallidos. Inicia el registro nuevamente.")

        # Verificar código
        if cached_data["code"] != code:
            cached_data["attempts"] += 1
            remaining_attempts = 3 - cached_data["attempts"]
            raise HTTPException(
                status_code=400, 
                detail=f"Código incorrecto. Te quedan {remaining_attempts} intentos."
            )

        # Verificar JWT
        token_data = verify_verification_token(cached_data["token"])
        if not token_data:
            del verification_cache[email]
            raise HTTPException(status_code=400, detail="Token expirado. Inicia el registro nuevamente.")

        # Verificar que los datos coincidan
        if token_data["email"] != email or token_data["code"] != code:
            del verification_cache[email]
            raise HTTPException(status_code=400, detail="Datos de verificación inválidos.")

        # Crear usuario
        nuevo_usuario = Usuario(
            email=email,
            nickname=cached_data["nickname"]
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)

        # Limpiar cache
        del verification_cache[email]

        return {
            "message": "Registro completado exitosamente",
            "usuario": {
                "id_user": nuevo_usuario.id_user,
                "email": nuevo_usuario.email,
                "nickname": nuevo_usuario.nickname,
                "created_date": nuevo_usuario.created_date
            },
            "next_steps": [
                "Puedes iniciar sesiones directamente",
                "Usa tu nickname para identificar tus actividades"
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al completar el registro: {str(e)}")

@router.post("/auth/resend-code")
def reenviar_codigo(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Reenvía el código de verificación"""
    try:
        cached_data = verification_cache.get(email)
        
        if not cached_data:
            raise HTTPException(status_code=400, detail="No hay registro en progreso para este email.")

        # Verificar si el JWT aún es válido
        token_data = verify_verification_token(cached_data["token"])
        if not token_data:
            del verification_cache[email]
            raise HTTPException(status_code=400, detail="Registro expirado. Inicia el proceso nuevamente.")

        # Generar nuevo código
        new_code = generate_verification_code()
        
        # Actualizar cache
        cached_data["code"] = new_code
        cached_data["attempts"] = 0
        cached_data["created_at"] = datetime.now(timezone.utc)

        # Reenviar email
        background_tasks.add_task(send_verification_email, email, new_code)

        return {
            "message": "Nuevo código de verificación enviado",
            "email": email,
            "expires_in_minutes": VERIFICATION_EXPIRE_MINUTES
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reenviar código: {str(e)}")

@router.get("/auth/registration-status/{email}")
def estado_registro(email: str):
    """Consulta el estado del registro en progreso"""
    cached_data = verification_cache.get(email)
    
    if not cached_data:
        return {"status": "no_registration", "message": "No hay registro en progreso"}
    
    # Verificar si aún es válido
    token_data = verify_verification_token(cached_data["token"])
    if not token_data:
        del verification_cache[email]
        return {"status": "expired", "message": "Registro expirado"}
    
    expires_at = datetime.fromtimestamp(token_data["exp"], timezone.utc)
    time_remaining = expires_at - datetime.now(timezone.utc)
    minutes_remaining = max(0, int(time_remaining.total_seconds() / 60))
    
    return {
        "status": "in_progress",
        "email": email,
        "nickname": cached_data["nickname"],
        "attempts": cached_data["attempts"],
        "minutes_remaining": minutes_remaining,
        "expires_at": expires_at
    }

@router.post("/auth/forgot-username")
def solicitar_recuperacion_usuario(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Solicita la recuperación del username enviando un código de verificación"""
    try:
        # Verificar si el email existe en la base de datos
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        if not usuario:
            # Por seguridad, no revelar si el email existe o no
            return {
                "message": "Si el email existe, se ha enviado un código de verificación",
                "email": email
            }

        # Generar código de verificación
        recovery_code = generate_verification_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        # Guardar en cache
        verification_cache[f"recovery_{email}"] = {
            "code": recovery_code,
            "expires_at": expires_at,
            "user_id": usuario.id_user,
            "attempts": 0,
            "type": "username_recovery"
        }

        # Enviar código por email
        background_tasks.add_task(send_recovery_email, email, recovery_code, usuario.nickname)

        return {
            "message": "Si el email existe, se ha enviado un código de verificación",
            "email": email,
            "expires_in_minutes": 10
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar solicitud: {str(e)}")

@router.post("/auth/verify-recovery")
def verificar_recuperacion_usuario(
    email: str,
    code: str,
    db: Session = Depends(get_db)
):
    """Verifica el código de recuperación y devuelve el username"""
    try:
        cache_key = f"recovery_{email}"
        cached_data = verification_cache.get(cache_key)
        
        if not cached_data:
            raise HTTPException(status_code=400, detail="Código no encontrado o expirado")

        # Verificar tipo
        if cached_data.get("type") != "username_recovery":
            raise HTTPException(status_code=400, detail="Solicitud inválida")

        # Verificar intentos
        if cached_data["attempts"] >= 3:
            del verification_cache[cache_key]
            raise HTTPException(status_code=400, detail="Demasiados intentos fallidos")

        # Verificar expiración
        if datetime.now(timezone.utc) > cached_data["expires_at"]:
            del verification_cache[cache_key]
            raise HTTPException(status_code=400, detail="Código expirado")

        # Verificar código
        if cached_data["code"] != code:
            cached_data["attempts"] += 1
            remaining_attempts = 3 - cached_data["attempts"]
            raise HTTPException(
                status_code=400, 
                detail=f"Código incorrecto. Te quedan {remaining_attempts} intentos."
            )

        usuario = db.query(Usuario).filter(Usuario.id_user == cached_data["user_id"]).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        send_username_reminder_email(email, usuario.nickname)

        del verification_cache[cache_key]

        return {
            "message": "Se ha enviado un recordatorio de tu username a tu email",
            "email": email
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar recuperación: {str(e)}")

@router.get("/auth/recovery-status/{email}")
def estado_recuperacion(email: str):
    """Consulta el estado de la recuperación"""
    cache_key = f"recovery_{email}"
    cached_data = verification_cache.get(cache_key)
    
    if not cached_data:
        return {"status": "no_recovery", "message": "No hay recuperación en progreso"}
    
    if datetime.now(timezone.utc) > cached_data["expires_at"]:
        del verification_cache[cache_key]
        return {"status": "expired", "message": "Recuperación expirada"}
    
    expires_at = cached_data["expires_at"]
    time_remaining = expires_at - datetime.now(timezone.utc)
    minutes_remaining = max(0, int(time_remaining.total_seconds() / 60))
    
    return {
        "status": "in_progress",
        "email": email,
        "type": cached_data.get("type", "unknown"),
        "attempts": cached_data["attempts"],
        "minutes_remaining": minutes_remaining
    }

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
            "message": "Total de minutos de focus actualizado exitosamente",
            "id_session": sesion.id_session,
            "total_focus_minutes": sesion.total_focus_minutes
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar total de focus: {str(e)}")

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
# ENDPOINTS PARA POMODOROS
# ============================================================

@router.post("/pomodoros/")
def iniciar_pomodoro(
    pomodoro_data: dict,
    db: Session = Depends(get_db)
):
    try:
        # Extraer datos del JSON
        id_session = pomodoro_data.get("id_session")
        id_pomodoro_rule = pomodoro_data.get("id_pomodoro_rule")
        id_pomodoro_type = pomodoro_data.get("id_pomodoro_type")
        event_type = pomodoro_data.get("event_type", "focus")
        planned_duration = pomodoro_data.get("planned_duration", 25)
        notes = pomodoro_data.get("notes")
        
        # Validar campos requeridos
        if not id_session:
            raise HTTPException(status_code=400, detail="id_session es requerido")
        if not id_pomodoro_rule:
            raise HTTPException(status_code=400, detail="id_pomodoro_rule es requerido")
        if not id_pomodoro_type:
            raise HTTPException(status_code=400, detail="id_pomodoro_type es requerido")
        
        # Verificar sesión
        sesion = db.query(Sesion).filter(Sesion.id_session == id_session).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Verificar regla
        regla = db.query(PomodoroRule).filter(PomodoroRule.id_pomodoro_rule == id_pomodoro_rule).first()
        if not regla:
            raise HTTPException(status_code=404, detail="Regla de pomodoro no encontrada")
        
        # Verificar tipo
        tipo = db.query(PomodoroType).filter(PomodoroType.id_pomodoro_type == id_pomodoro_type).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de pomodoro no encontrado")
        
        # Validar event_type según el constraint de la base de datos
        if event_type not in ["focus", "break"]:
            raise HTTPException(status_code=400, detail="Event type debe ser 'focus' o 'break'")
        
        nuevo_pomodoro = Pomodoro(
            id_session=id_session,
            id_pomodoro_rule=id_pomodoro_rule,
            id_pomodoro_type=id_pomodoro_type,
            event_type=event_type,
            planned_duration=planned_duration,
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
                "is_completed": nuevo_pomodoro.is_completed,
                "notes": nuevo_pomodoro.notes,
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
        
        pomodoro.is_completed = True
        
        # Actualizar estadísticas de la sesión
        sesion = db.query(Sesion).filter(Sesion.id_session == pomodoro.id_session).first()
        if pomodoro.event_type == "focus":
            sesion.total_focus_minutes += pomodoro.planned_duration
        elif pomodoro.event_type == "break":
            sesion.total_break_minutes += pomodoro.planned_duration
        
        db.commit()
        
        return {
            "message": "Pomodoro completado exitosamente",
            "pomodoro": {
                "id_pomodoro_detail": pomodoro.id_pomodoro_detail,
                "event_type": pomodoro.event_type,
                "planned_duration": pomodoro.planned_duration,
                "is_completed": pomodoro.is_completed,
                "notes": pomodoro.notes
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
            "is_completed": p.is_completed,
            "notes": p.notes,
            "created_date": p.created_date
        } for p in pomodoros]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pomodoros: {str(e)}")

@router.get("/pomodoros/sesion/{id_session}/completo")
def listar_pomodoros_sesion_completo(id_session: int, db: Session = Depends(get_db)):
    """
    Retorna todos los pomodoros de una sesión con información completa
    incluyendo datos de reglas y tipos
    """
    try:
        # Verificar que la sesión existe
        sesion = db.query(Sesion).filter(Sesion.id_session == id_session).first()
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Obtener pomodoros con joins para incluir reglas y tipos
        pomodoros = db.query(
            Pomodoro,
            PomodoroRule,
            PomodoroType
        ).join(
            PomodoroRule, Pomodoro.id_pomodoro_rule == PomodoroRule.id_pomodoro_rule
        ).join(
            PomodoroType, Pomodoro.id_pomodoro_type == PomodoroType.id_pomodoro_type
        ).filter(
            Pomodoro.id_session == id_session
        ).all()
        
        resultado = []
        for pomodoro, regla, tipo in pomodoros:
            pomodoro_data = {
                # Información básica del pomodoro
                "id_pomodoro_detail": pomodoro.id_pomodoro_detail,
                "id_session": pomodoro.id_session,
                "event_type": pomodoro.event_type,
                "planned_duration": pomodoro.planned_duration,
                "is_completed": pomodoro.is_completed,
                "notes": pomodoro.notes,
                "created_date": pomodoro.created_date,
                
                # Información completa de la regla
                "regla": {
                    "id_pomodoro_rule": regla.id_pomodoro_rule,
                    "difficulty_level": regla.difficulty_level,
                    "focus_duration": regla.focus_duration,
                    "break_duration": regla.break_duration,
                    "description": regla.description,
                    "created_date": regla.created_date
                },
                
                # Información completa del tipo
                "tipo": {
                    "id_pomodoro_type": tipo.id_pomodoro_type,
                    "name_type": tipo.name_type
                },
                
                # Información calculada
                "tipo_evento": "Focus" if pomodoro.event_type == "focus" else "Break",
                "duracion_real": pomodoro.planned_duration,
                "estado": "Completado" if pomodoro.is_completed else "En progreso"
            }
            resultado.append(pomodoro_data)
        
        return {
            "sesion": {
                "id_session": sesion.id_session,
                "session_name": sesion.session_name,
                "total_focus_minutes": sesion.total_focus_minutes,
                "total_break_minutes": sesion.total_break_minutes,
                "total_pause_minutes": sesion.total_pause_minutes
            },
            "total_pomodoros": len(resultado),
            "pomodoros": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pomodoros completos: {str(e)}")

@router.get("/pomodoros/{id_pomodoro_detail}/completo")
def obtener_pomodoro_completo(id_pomodoro_detail: int, db: Session = Depends(get_db)):
    """
    Retorna un pomodoro específico con información completa
    incluyendo datos de reglas, tipos y pausas asociadas
    """
    try:
        # Obtener pomodoro con joins
        resultado = db.query(
            Pomodoro,
            PomodoroRule,
            PomodoroType,
            Sesion
        ).join(
            PomodoroRule, Pomodoro.id_pomodoro_rule == PomodoroRule.id_pomodoro_rule
        ).join(
            PomodoroType, Pomodoro.id_pomodoro_type == PomodoroType.id_pomodoro_type
        ).join(
            Sesion, Pomodoro.id_session == Sesion.id_session
        ).filter(
            Pomodoro.id_pomodoro_detail == id_pomodoro_detail
        ).first()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Pomodoro no encontrado")
        
        pomodoro, regla, tipo, sesion = resultado
        
        # Obtener pausas asociadas a este pomodoro
        pausas = db.query(PauseTracker).filter(
            PauseTracker.id_pomodoro_detail == id_pomodoro_detail
        ).all()
        
        pomodoro_data = {
            # Información básica del pomodoro
            "id_pomodoro_detail": pomodoro.id_pomodoro_detail,
            "event_type": pomodoro.event_type,
            "planned_duration": pomodoro.planned_duration,
            "is_completed": pomodoro.is_completed,
            "notes": pomodoro.notes,
            "created_date": pomodoro.created_date,
            
            # Información de la sesión
            "sesion": {
                "id_session": sesion.id_session,
                "session_name": sesion.session_name,
                "id_user": sesion.id_user
            },
            
            # Información completa de la regla
            "regla": {
                "id_pomodoro_rule": regla.id_pomodoro_rule,
                "difficulty_level": regla.difficulty_level,
                "focus_duration": regla.focus_duration,
                "break_duration": regla.break_duration,
                "description": regla.description
            },
            
            # Información completa del tipo
            "tipo": {
                "id_pomodoro_type": tipo.id_pomodoro_type,
                "name_type": tipo.name_type
            },
            
            # Pausas asociadas
            "pausas": [{
                "id_pause": p.id_pause,
                "pause_start": p.pause_start,
                "pause_end": p.pause_end,
                "total_pause_minutes": p.total_pause_minutes
            } for p in pausas],
            
            # Información calculada
            "total_pausas": len(pausas),
            "total_minutos_pausa": sum(p.total_pause_minutes for p in pausas),
            "tipo_evento": "Focus" if pomodoro.event_type == "focus" else "Break",
            "estado": "Completado" if pomodoro.is_completed else "En progreso"
        }
        
        return pomodoro_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener pomodoro completo: {str(e)}")

# ============================================================
# ENDPOINTS PARA PAUSAS
# ============================================================

@router.post("/pausas/")
def iniciar_pausa(pausa_data: dict, db: Session = Depends(get_db)):
    try:
        id_pomodoro_detail = pausa_data.get("id_pomodoro_detail")
        
        if not id_pomodoro_detail:
            raise HTTPException(status_code=400, detail="id_pomodoro_detail es requerido")
        
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
        
        # Actualizar estadísticas de la sesión
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
        # Verificar que el usuario existe
        usuario = db.query(Usuario).filter(Usuario.id_user == id_user).first()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Calcular estadísticas
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")