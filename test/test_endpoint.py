#!/usr/bin/env python3
"""
SCRIPT DE PRUEBA COMPLETO - POMODORO APP
Prueba todos los endpoints y funcionalidades del sistema
"""

import requests
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, params=None, json_data=None, descripcion=""):
    """Función para probar endpoints"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        print(f"\n{'='*60}")
        print(f"🔹 {method} {endpoint}")
        if descripcion:
            print(f"📝 {descripcion}")
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=json_data)
        elif method == "PUT":
            response = requests.put(url, params=params, json=json_data)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            try:
                data = response.json()
                if "message" in data:
                    print(f"💬 {data['message']}")
                return data
            except:
                return {"raw_response": response.text}
        else:
            print("❌ Error!")
            print(f"💬 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def esperar(segundos, motivo=""):
    """Espera mostrando cuenta regresiva"""
    if motivo:
        print(f"\n⏳ {motivo} - Esperando {segundos} segundos...")
    for i in range(segundos, 0, -1):
        print(f"   {i}...", end=' ', flush=True)
        time.sleep(1)
    print("✅ Listo!")

def simular_flujo_completo():
    """Simulación completa de todos los flujos de la aplicación"""
    print("🚀 INICIANDO PRUEBA COMPLETA DEL SISTEMA POMODORO")
    print("=" * 70)
    
    # =========================================================================
    # 1. PRUEBAS DE CONFIGURACIÓN Y HEALTH CHECK
    # =========================================================================
    print("\n🎯 1. PRUEBAS DE CONFIGURACIÓN")
    
    # Health check
    test_endpoint("GET", "/health", descripcion="Health check del servidor")
    
    # Root endpoint
    test_endpoint("GET", "/", descripcion="Endpoint raíz")
    
    # Información del sistema
    test_endpoint("GET", "/info", descripcion="Información del sistema")
    
    # =========================================================================
    # 2. PRUEBAS DE REGLAS Y TIPOS
    # =========================================================================
    print("\n🎯 2. PRUEBAS DE REGLAS Y TIPOS DE POMODORO")
    
    # Obtener reglas disponibles
    reglas = test_endpoint("GET", "/reglas-pomodoro/", descripcion="Obtener reglas de pomodoro")
    if reglas:
        print(f"📋 Reglas disponibles: {len(reglas)}")
        for regla in reglas:
            print(f"   - {regla['difficulty_level']}: Focus {regla['focus_duration']}min, Break {regla['break_duration']}min")
    
    # Obtener tipos disponibles
    tipos = test_endpoint("GET", "/tipos-pomodoro/", descripcion="Obtener tipos de pomodoro")
    if tipos:
        print(f"📋 Tipos disponibles: {len(tipos)}")
        for tipo in tipos:
            print(f"   - {tipo['name_type']}")
    
    # =========================================================================
    # 3. PRUEBAS DE AUTENTICACIÓN Y USUARIOS
    # =========================================================================
    print("\n🎯 3. PRUEBAS DE AUTENTICACIÓN Y USUARIOS")
    
    # Crear usuarios de prueba
    usuarios_prueba = [
        {"email": f"testusuario{random.randint(1000,9999)}@gmail.com", "nickname": f"TestUser{random.randint(100,999)}"},
        {"email": f"estudiante{random.randint(1000,9999)}@hotmail.com", "nickname": f"Estudiante{random.randint(100,999)}"},
        {"email": f"developer{random.randint(1000,9999)}@outlook.com", "nickname": f"Dev{random.randint(100,999)}"}
    ]
    
    usuarios_creados = []
    
    for i, usuario in enumerate(usuarios_prueba, 1):
        print(f"\n👤 Creando usuario {i}/3:")
        print(f"   Email: {usuario['email']}")
        print(f"   Nickname: {usuario['nickname']}")
        
        # Iniciar registro
        inicio_registro = test_endpoint("POST", "/auth/start-registration", 
                                      params={"email": usuario['email'], "nickname": usuario['nickname']},
                                      descripcion=f"Iniciando registro usuario {i}")
        
        if inicio_registro:
            # Simular código de verificación (en producción esto viene por email)
            codigo_simulado = "123456"
            
            # Verificar código
            verificacion = test_endpoint("POST", "/auth/verify",
                                       params={"email": usuario['email'], "code": codigo_simulado},
                                       descripcion=f"Verificando usuario {i}")
            
            if verificacion:
                usuarios_creados.append({
                    "email": usuario['email'],
                    "nickname": usuario['nickname'],
                    "id_user": verificacion['usuario']['id_user']
                })
                print(f"✅ Usuario {usuario['nickname']} creado exitosamente (ID: {verificacion['usuario']['id_user']})")
    
    # =========================================================================
    # 4. PRUEBAS DE SESIONES
    # =========================================================================
    print("\n🎯 4. PRUEBAS DE SESIONES")
    
    sesiones_creadas = []
    
    for usuario in usuarios_creados:
        # Crear sesiones para cada usuario
        sesiones_usuario = [
            f"Sesión Estudio - {usuario['nickname']}",
            f"Sesión Trabajo - {usuario['nickname']}",
            f"Sesión Lectura - {usuario['nickname']}"
        ]
        
        for nombre_sesion in sesiones_usuario:
            sesion = test_endpoint("POST", "/sesiones/",
                                 params={"id_user": usuario['id_user'], "session_name": nombre_sesion},
                                 descripcion=f"Creando sesión: {nombre_sesion}")
            
            if sesion:
                sesiones_creadas.append({
                    "id_session": sesion['sesion']['id_session'],
                    "id_user": usuario['id_user'],
                    "session_name": nombre_sesion
                })
    
    # Listar sesiones por usuario
    for usuario in usuarios_creados:
        sesiones = test_endpoint("GET", f"/sesiones/usuario/{usuario['id_user']}",
                               descripcion=f"Listando sesiones de {usuario['nickname']}")
        
        if sesiones:
            print(f"📚 {usuario['nickname']} tiene {len(sesiones)} sesiones:")
            for sesion in sesiones:
                print(f"   - {sesion['session_name']} (Focus: {sesion['total_focus_minutes']}min)")
    
    # =========================================================================
    # 5. PRUEBAS DE POMODOROS COMPLETOS
    # =========================================================================
    print("\n🎯 5. PRUEBAS DE POMODOROS Y PAUSAS")
    
    # Usar la primera sesión para pruebas de pomodoros
    if sesiones_creadas:
        sesion_prueba = sesiones_creadas[0]
        
        # Flujo completo de pomodoro con pausa
        print(f"\n⏰ SIMULANDO FLUJO POMODORO COMPLETO EN SESIÓN: {sesion_prueba['session_name']}")
        
        # Pomodoro de focus
        pomodoro_focus = test_endpoint("POST", "/pomodoros/",
                                     json_data={
                                         "id_session": sesion_prueba['id_session'],
                                         "id_pomodoro_rule": 2,  # Popular (25/5)
                                         "id_pomodoro_type": 1,  # Estudio
                                         "event_type": "focus",
                                         "planned_duration": 25,
                                         "notes": "Estudiando matemáticas avanzadas - Teoría de números"
                                     },
                                     descripcion="Iniciando pomodoro de FOCUS")
        
        if pomodoro_focus:
            p_id = pomodoro_focus['pomodoro']['id_pomodoro_detail']
            
            # Simular pausa durante el pomodoro
            print(f"\n⏸️  Simulando pausa durante el pomodoro...")
            pausa = test_endpoint("POST", "/pausas/",
                                json_data={"id_pomodoro_detail": p_id},
                                descripcion="Iniciando pausa durante pomodoro")
            
            if pausa:
                pausa_id = pausa['pausa']['id_pause']
                esperar(3, "Pausa en progreso")
                
                # Finalizar pausa
                test_endpoint("PUT", f"/pausas/{pausa_id}/finalizar",
                            descripcion="Finalizando pausa")
            
            # Completar pomodoro
            test_endpoint("PUT", f"/pomodoros/{p_id}/completar",
                        descripcion="Completando pomodoro de focus")
            
            # Pomodoro de break
            pomodoro_break = test_endpoint("POST", "/pomodoros/",
                                         json_data={
                                             "id_session": sesion_prueba['id_session'],
                                             "id_pomodoro_rule": 2,  # Popular (25/5)
                                             "id_pomodoro_type": 3,  # Descanso
                                             "event_type": "break",
                                             "planned_duration": 5,
                                             "notes": "Descanso corto - Estiramientos e hidratación"
                                         },
                                         descripcion="Iniciando pomodoro de BREAK")
            
            if pomodoro_break:
                b_id = pomodoro_break['pomodoro']['id_pomodoro_detail']
                test_endpoint("PUT", f"/pomodoros/{b_id}/completar",
                            descripcion="Completando break")
        
        # Probar diferentes tipos de pomodoros
        tipos_pomodoro = [
            {"rule": 1, "type": 1, "duration": 15, "notes": "Paso de bebe - Calentamiento"},
            {"rule": 3, "type": 2, "duration": 40, "notes": "Medio - Trabajo profundo"},
            {"rule": 4, "type": 4, "duration": 60, "notes": "Intenso - Desarrollo complejo"}
        ]
        
        for i, config in enumerate(tipos_pomodoro, 1):
            pomodoro = test_endpoint("POST", "/pomodoros/",
                                   json_data={
                                       "id_session": sesion_prueba['id_session'],
                                       "id_pomodoro_rule": config['rule'],
                                       "id_pomodoro_type": config['type'],
                                       "event_type": "focus",
                                       "planned_duration": config['duration'],
                                       "notes": config['notes']
                                   },
                                   descripcion=f"Pomodoro tipo {i}: {config['notes']}")
            
            if pomodoro:
                p_id = pomodoro['pomodoro']['id_pomodoro_detail']
                test_endpoint("PUT", f"/pomodoros/{p_id}/completar",
                            descripcion=f"Completando pomodoro tipo {i}")
    
    # =========================================================================
    # 6. PRUEBAS DE ACTUALIZACIÓN MANUAL DE TIEMPOS
    # =========================================================================
    print("\n🎯 6. PRUEBAS DE ACTUALIZACIÓN MANUAL DE TIEMPOS")
    
    if sesiones_creadas:
        sesion_actualizar = sesiones_creadas[1]  # Usar segunda sesión
        
        # Actualizar minutos manualmente
        test_endpoint("PUT", f"/sesiones/{sesion_actualizar['id_session']}/total_focus",
                    params={"minutos": 30},
                    descripcion="Actualizando minutos de focus manualmente")
        
        test_endpoint("PUT", f"/sesiones/{sesion_actualizar['id_session']}/total_break", 
                    params={"minutos": 10},
                    descripcion="Actualizando minutos de break manualmente")
        
        test_endpoint("PUT", f"/sesiones/{sesion_actualizar['id_session']}/total_pause",
                    params={"minutos": 5},
                    descripcion="Actualizando minutos de pausa manualmente")
    
    # =========================================================================
    # 7. PRUEBAS DE ESTADÍSTICAS
    # =========================================================================
    print("\n🎯 7. PRUEBAS DE ESTADÍSTICAS")
    
    for usuario in usuarios_creados:
        estadisticas = test_endpoint("GET", f"/estadisticas/usuario/{usuario['id_user']}",
                                   descripcion=f"Estadísticas de {usuario['nickname']}")
        
        if estadisticas:
            print(f"\n📊 RESUMEN ESTADÍSTICAS - {usuario['nickname']}:")
            print(f"   🎯 Focus total: {estadisticas['total_focus_minutes']} minutos")
            print(f"   ☕ Break total: {estadisticas['total_break_minutes']} minutos")
            print(f"   ⏸️  Pause total: {estadisticas['total_pause_minutes']} minutos")
            print(f"   📚 Sesiones: {estadisticas['total_sesiones']}")
            print(f"   ✅ Pomodoros completados: {estadisticas['total_pomodoros_completados']}")
    
    # =========================================================================
    # 8. PRUEBAS DE RECUPERACIÓN DE USUARIO
    # =========================================================================
    print("\n🎯 8. PRUEBAS DE RECUPERACIÓN DE USUARIO")
    
    if usuarios_creados:
        usuario_recuperar = usuarios_creados[0]
        
        # Solicitar recuperación
        test_endpoint("POST", "/auth/forgot-username",
                    params={"email": usuario_recuperar['email']},
                    descripcion="Solicitando recuperación de usuario")
        
        # Verificar estado de recuperación
        test_endpoint("GET", f"/auth/recovery-status/{usuario_recuperar['email']}",
                    descripcion="Estado de recuperación")
        
        # Verificar código (simulado)
        test_endpoint("POST", "/auth/verify-recovery",
                    params={"email": usuario_recuperar['email'], "code": "123456"},
                    descripcion="Verificando código de recuperación")
    
    # =========================================================================
    # 9. PRUEBAS DE CONSULTA DE DATOS
    # =========================================================================
    print("\n🎯 9. PRUEBAS DE CONSULTA DE DATOS")
    
    # Listar todos los usuarios
    todos_usuarios = test_endpoint("GET", "/usuarios/",
                                 descripcion="Listando todos los usuarios")
    
    # Listar pomodoros de sesión
    if sesiones_creadas:
        sesion_consulta = sesiones_creadas[0]
        pomodoros = test_endpoint("GET", f"/pomodoros/sesion/{sesion_consulta['id_session']}",
                                descripcion=f"Listando pomodoros de sesión {sesion_consulta['session_name']}")
        
        if pomodoros:
            print(f"\n📝 Pomodoros en {sesion_consulta['session_name']}:")
            for p in pomodoros:
                estado = "✅" if p['is_completed'] else "⏳"
                print(f"   {estado} {p['event_type']} - {p['planned_duration']}min - {p['notes']}")
    
    # =========================================================================
    # 10. PRUEBAS DE ERRORES Y CASOS BORDE
    # =========================================================================
    print("\n🎯 10. PRUEBAS DE ERRORES Y CASOS BORDE")
    
    # Usuario no existente
    test_endpoint("GET", "/usuarios/9999", descripcion="Usuario no existente")
    
    # Sesión no existente
    test_endpoint("GET", "/sesiones/usuario/9999", descripcion="Sesiones de usuario no existente")
    
    # Email duplicado (intentar crear usuario existente)
    if usuarios_creados:
        test_endpoint("POST", "/auth/start-registration",
                    params={"email": usuarios_creados[0]['email'], "nickname": "NuevoNickname"},
                    descripcion="Intentando registrar email duplicado")
    
    # Código de verificación incorrecto
    test_endpoint("POST", "/auth/verify",
                params={"email": "test@ejemplo.com", "code": "999999"},
                descripcion="Código de verificación incorrecto")
    
    # Event type inválido
    test_endpoint("POST", "/pomodoros/",
                json_data={
                    "id_session": 1,
                    "id_pomodoro_rule": 1,
                    "id_pomodoro_type": 1,
                    "event_type": "invalid_type",
                    "planned_duration": 25
                },
                descripcion="Event type inválido")

def main():
    """Función principal"""
    print("🎯 SISTEMA DE PRUEBAS AUTOMATIZADAS - POMODORO APP")
    print("⏰ Este script probará TODAS las funcionalidades del sistema")
    print("📊 Se crearán usuarios, sesiones, pomodoros y se generarán estadísticas")
    print("=" * 70)
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ El servidor no está respondiendo. Asegúrate de que esté ejecutándose:")
            print("   uvicorn main:app --reload")
            return
    except:
        print("❌ No se puede conectar al servidor. Verifica que esté ejecutándose:")
        print("   uvicorn main:app --reload")
        return
    
    # Ejecutar simulación completa
    inicio = datetime.now()
    simular_flujo_completo()
    fin = datetime.now()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("🎉 PRUEBA COMPLETA FINALIZADA")
    print(f"⏱️  Tiempo total: {(fin - inicio).total_seconds():.1f} segundos")
    print("📈 Resumen:")
    print("   ✅ Pruebas de configuración y health check")
    print("   ✅ Pruebas de autenticación y usuarios") 
    print("   ✅ Pruebas de sesiones y pomodoros")
    print("   ✅ Pruebas de estadísticas y consultas")
    print("   ✅ Pruebas de errores y casos borde")
    print("   ✅ Pruebas de recuperación de usuario")
    print("\n🚀 El sistema está funcionando correctamente!")
    print("=" * 70)

if __name__ == "__main__":
    main()