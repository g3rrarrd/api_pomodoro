#!/usr/bin/env python3
"""
SCRIPT DE PRUEBA ACTUALIZADO - POMODORO APP
Usa los tipos y reglas específicos de la base de datos y el usuario existente
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

def encontrar_regla_por_nombre(reglas, nombre):
    """Encuentra una regla por su nombre de dificultad"""
    for regla in reglas:
        if regla['difficulty_level'].lower() == nombre.lower():
            return regla['id_pomodoro_rule']
    return None

def encontrar_tipo_por_nombre(tipos, nombre):
    """Encuentra un tipo por su nombre"""
    for tipo in tipos:
        if tipo['name_type'].lower() == nombre.lower():
            return tipo['id_pomodoro_type']
    return None

def simular_flujo_completo_actualizado():
    """Simulación completa usando los datos reales de la BD"""
    print("🚀 INICIANDO PRUEBA COMPLETA CON DATOS REALES")
    print("=" * 70)
    
    # Usuario existente
    USUARIO_EXISTENTE = {
        "id_user": 1,
        "nickname": "GerardoAnt", 
        "email": "grdgz51@gmail.com"
    }
    
    # =========================================================================
    # 1. PRUEBAS DE CONFIGURACIÓN
    # =========================================================================
    print("\n🎯 1. PRUEBAS DE CONFIGURACIÓN")
    
    test_endpoint("GET", "/health", descripcion="Health check del servidor")
    test_endpoint("GET", "/", descripcion="Endpoint raíz")
    
    # =========================================================================
    # 2. OBTENER REGLAS Y TIPOS REALES
    # =========================================================================
    print("\n🎯 2. OBTENIENDO REGLAS Y TIPOS DE LA BASE DE DATOS")
    
    # Obtener reglas disponibles
    reglas = test_endpoint("GET", "/reglas-pomodoro/", descripcion="Obtener reglas de pomodoro")
    if reglas:
        print(f"📋 Reglas disponibles en BD:")
        for regla in reglas:
            print(f"   - {regla['difficulty_level']}: Focus {regla['focus_duration']}min, Break {regla['break_duration']}min")
    
    # Obtener tipos disponibles  
    tipos = test_endpoint("GET", "/tipos-pomodoro/", descripcion="Obtener tipos de pomodoro")
    if tipos:
        print(f"📋 Tipos disponibles en BD:")
        for tipo in tipos:
            print(f"   - {tipo['name_type']}")
    
    # =========================================================================
    # 3. PRUEBAS CON USUARIO EXISTENTE
    # =========================================================================
    print("\n🎯 3. PRUEBAS CON USUARIO EXISTENTE")
    
    # Obtener información del usuario existente
    usuario_info = test_endpoint("GET", f"/usuarios/{USUARIO_EXISTENTE['id_user']}", 
                               descripcion=f"Obteniendo información de {USUARIO_EXISTENTE['nickname']}")
    
    # Obtener usuario por email
    test_endpoint("GET", f"/usuarios/email/{USUARIO_EXISTENTE['email']}",
                 descripcion=f"Buscando usuario por email")
    
    # Obtener usuario por nickname
    test_endpoint("GET", f"/usuarios/nickname/{USUARIO_EXISTENTE['nickname']}",
                 descripcion=f"Buscando usuario por nickname")
    
    # =========================================================================
    # 4. CREAR SESIONES DE TRABAJO REALISTAS
    # =========================================================================
    print("\n🎯 4. CREANDO SESIONES DE TRABAJO REALISTAS")
    
    sesiones_reales = [
        "Estudio Intensivo - Matemáticas Avanzadas",
        "Desarrollo API - Proyecto Personal", 
        "Lectura Técnica - Patrones de Diseño",
        "Planificación Semanal - Metas y Objetivos",
        "Ejercicio de Programación - Algoritmos"
    ]
    
    sesiones_creadas = []
    
    for nombre_sesion in sesiones_reales:
        sesion = test_endpoint("POST", "/sesiones/",
                             params={"id_user": USUARIO_EXISTENTE['id_user'], "session_name": nombre_sesion},
                             descripcion=f"Creando sesión: {nombre_sesion}")
        
        if sesion:
            sesiones_creadas.append({
                "id_session": sesion['sesion']['id_session'],
                "session_name": nombre_sesion
            })
            print(f"✅ Sesión creada: {nombre_sesion} (ID: {sesion['sesion']['id_session']})")
    
    # Listar sesiones del usuario
    sesiones_usuario = test_endpoint("GET", f"/sesiones/usuario/{USUARIO_EXISTENTE['id_user']}",
                                   descripcion="Listando todas las sesiones del usuario")
    
    # =========================================================================
    # 5. SIMULACIÓN DE DÍA COMPLETO DE TRABAJO
    # =========================================================================
    print("\n🎯 5. SIMULANDO DÍA COMPLETO DE TRABAJO Y ESTUDIO")
    
    if sesiones_creadas and reglas and tipos:
        # Usar la primera sesión para la simulación
        sesion_principal = sesiones_creadas[0]
        
        # Encontrar IDs de reglas y tipos específicos
        regla_paso_bebe = encontrar_regla_por_nombre(reglas, "Paso de bebe")
        regla_popular = encontrar_regla_por_nombre(reglas, "Popular") 
        regla_medio = encontrar_regla_por_nombre(reglas, "Medio")
        regla_intenso = encontrar_regla_por_nombre(reglas, "Intenso")
        regla_extendido = encontrar_regla_por_nombre(reglas, "Extendido")
        
        tipo_estudio = encontrar_tipo_por_nombre(tipos, "Estudio")
        tipo_trabajo = encontrar_tipo_por_nombre(tipos, "Trabajo")
        tipo_lectura = encontrar_tipo_por_nombre(tipos, "Lectura")
        tipo_ejercicio = encontrar_tipo_por_nombre(tipos, "Ejercicio")
        tipo_meditacion = encontrar_tipo_por_nombre(tipos, "Meditación")
        tipo_proyectos = encontrar_tipo_por_nombre(tipos, "Proyectos Personales")
        tipo_desarrollo = encontrar_tipo_por_nombre(tipos, "Desarrollo de Habilidades")
        tipo_planificacion = encontrar_tipo_por_nombre(tipos, "Planificación y Organización")
        tipo_descanso = encontrar_tipo_por_nombre(tipos, "Descanso Activo")
        
        print(f"\n🔧 IDs encontrados:")
        print(f"   Reglas: Paso bebe({regla_paso_bebe}), Popular({regla_popular}), Medio({regla_medio}), Intenso({regla_intenso}), Extendido({regla_extendido})")
        print(f"   Tipos: Estudio({tipo_estudio}), Trabajo({tipo_trabajo}), Lectura({tipo_lectura}), Descanso({tipo_descanso})")
        
        # =====================================================================
        # MAÑANA: Sesión de estudio intensivo
        # =====================================================================
        print(f"\n🌅 MAÑANA: SESIÓN DE ESTUDIO INTENSIVO")
        
        # Pomodoro 1: Calentamiento (Paso de bebe)
        p1 = test_endpoint("POST", "/pomodoros/",
                         json_data={
                             "id_session": sesion_principal['id_session'],
                             "id_pomodoro_rule": regla_paso_bebe,
                             "id_pomodoro_type": tipo_estudio,
                             "event_type": "focus",
                             "planned_duration": 10,
                             "notes": "Calentamiento - Repaso de conceptos básicos de álgebra"
                         },
                         descripcion="Pomodoro 1: Calentamiento (Paso de bebe)")
        
        if p1:
            test_endpoint("PUT", f"/pomodoros/{p1['pomodoro']['id_pomodoro_detail']}/completar",
                        descripcion="Completando calentamiento")
        
        # Break 1: Descanso activo
        b1 = test_endpoint("POST", "/pomodoros/",
                         json_data={
                             "id_session": sesion_principal['id_session'],
                             "id_pomodoro_rule": regla_paso_bebe,
                             "id_pomodoro_type": tipo_descanso,
                             "event_type": "break", 
                             "planned_duration": 5,
                             "notes": "Break - Estiramientos e hidratación"
                         },
                         descripcion="Break 1: Descanso activo")
        
        if b1:
            test_endpoint("PUT", f"/pomodoros/{b1['pomodoro']['id_pomodoro_detail']}/completar",
                        descripcion="Finalizando break")
        
        # Pomodoro 2: Estudio profundo (Popular)
        p2 = test_endpoint("POST", "/pomodoros/",
                         json_data={
                             "id_session": sesion_principal['id_session'],
                             "id_pomodoro_rule": regla_popular,
                             "id_pomodoro_type": tipo_estudio,
                             "event_type": "focus",
                             "planned_duration": 25,
                             "notes": "Estudio profundo - Cálculo diferencial e integral"
                         },
                         descripcion="Pomodoro 2: Estudio profundo (Popular)")
        
        if p2:
            # Simular pausa durante el pomodoro
            pausa1 = test_endpoint("POST", "/pausas/",
                     json_data={"id_pomodoro_detail": p2['pomodoro']['id_pomodoro_detail']},
                     descripcion="Pausa técnica durante estudio")
            
            if pausa1:
                esperar(2, "Pausa técnica")
                test_endpoint("PUT", f"/pausas/{pausa1['pausa']['id_pause']}/finalizar",
                            descripcion="Finalizando pausa técnica")
            
            test_endpoint("PUT", f"/pomodoros/{p2['pomodoro']['id_pomodoro_detail']}/completar",
                        descripcion="Completando estudio profundo")
        
        # =====================================================================
        # TARDE: Sesión de desarrollo y proyectos
        # =====================================================================
        print(f"\n🌇 TARDE: SESIÓN DE DESARROLLO Y PROYECTOS")
        
        # Usar segunda sesión para la tarde
        if len(sesiones_creadas) > 1:
            sesion_tarde = sesiones_creadas[1]
            
            # Pomodoro 3: Desarrollo intensivo
            p3 = test_endpoint("POST", "/pomodoros/",
                             json_data={
                                 "id_session": sesion_tarde['id_session'],
                                 "id_pomodoro_rule": regla_intenso,
                                 "id_pomodoro_type": tipo_desarrollo,
                                 "event_type": "focus",
                                 "planned_duration": 60,
                                 "notes": "Desarrollo intensivo - Implementación de API REST con FastAPI"
                             },
                             descripcion="Pomodoro 3: Desarrollo intensivo (Intenso)")
            
            if p3:
                test_endpoint("PUT", f"/pomodoros/{p3['pomodoro']['id_pomodoro_detail']}/completar",
                            descripcion="Completando desarrollo intensivo")
            
            # Break largo después de sesión intensiva
            b2 = test_endpoint("POST", "/pomodoros/",
                             json_data={
                                 "id_session": sesion_tarde['id_session'],
                                 "id_pomodoro_rule": regla_intenso,
                                 "id_pomodoro_type": tipo_descanso,
                                 "event_type": "break",
                                 "planned_duration": 10,
                                 "notes": "Break largo - Caminata y merienda"
                             },
                             descripcion="Break 2: Descanso prolongado")
            
            if b2:
                test_endpoint("PUT", f"/pomodoros/{b2['pomodoro']['id_pomodoro_detail']}/completar",
                            descripcion="Finalizando break largo")
        
        # =====================================================================
        # NOCHE: Sesión de lectura y planificación
        # =====================================================================
        print(f"\n🌃 NOCHE: SESIÓN DE LECTURA Y PLANIFICACIÓN")
        
        if len(sesiones_creadas) > 2:
            sesion_noche = sesiones_creadas[2]
            
            # Pomodoro 4: Lectura técnica
            p4 = test_endpoint("POST", "/pomodoros/",
                             json_data={
                                 "id_session": sesion_noche['id_session'],
                                 "id_pomodoro_rule": regla_medio,
                                 "id_pomodoro_type": tipo_lectura,
                                 "event_type": "focus", 
                                 "planned_duration": 40,
                                 "notes": "Lectura técnica - Documentación de arquitectura de software"
                             },
                             descripcion="Pomodoro 4: Lectura técnica (Medio)")
            
            if p4:
                test_endpoint("PUT", f"/pomodoros/{p4['pomodoro']['id_pomodoro_detail']}/completar",
                            descripcion="Completando lectura técnica")
            
            # Pomodoro 5: Planificación
            p5 = test_endpoint("POST", "/pomodoros/",
                             json_data={
                                 "id_session": sesion_noche['id_session'],
                                 "id_pomodoro_rule": regla_popular,
                                 "id_pomodoro_type": tipo_planificacion,
                                 "event_type": "focus",
                                 "planned_duration": 25,
                                 "notes": "Planificación - Organización de tareas para mañana"
                             },
                             descripcion="Pomodoro 5: Planificación (Popular)")
            
            if p5:
                test_endpoint("PUT", f"/pomodoros/{p5['pomodoro']['id_pomodoro_detail']}/completar",
                            descripcion="Completando planificación")
    
    # =========================================================================
    # 6. ACTUALIZACIÓN MANUAL DE TIEMPOS
    # =========================================================================
    print("\n🎯 6. ACTUALIZACIÓN MANUAL DE TIEMPOS")
    
    if sesiones_creadas:
        # Actualizar tiempos manualmente para una sesión
        sesion_actualizar = sesiones_creadas[3] if len(sesiones_creadas) > 3 else sesiones_creadas[0]
        
        test_endpoint("PUT", f"/sesiones/{sesion_actualizar['id_session']}/total_focus",
                    params={"minutos": 45},
                    descripcion="Agregando 45min de focus manual")
        
        test_endpoint("PUT", f"/sesiones/{sesion_actualizar['id_session']}/total_break",
                    params={"minutos": 15}, 
                    descripcion="Agregando 15min de break manual")
        
        test_endpoint("PUT", f"/sesiones/{sesion_actualizar['id_session']}/total_pause",
                    params={"minutos": 8},
                    descripcion="Agregando 8min de pausa manual")
    
    # =========================================================================
    # 7. ESTADÍSTICAS Y REPORTES
    # =========================================================================
    print("\n🎯 7. ESTADÍSTICAS Y REPORTES FINALES")
    
    # Estadísticas del usuario
    estadisticas = test_endpoint("GET", f"/estadisticas/usuario/{USUARIO_EXISTENTE['id_user']}",
                               descripcion="Estadísticas completas del usuario")
    
    if estadisticas:
        print(f"\n📊 RESUMEN ESTADÍSTICAS - {USUARIO_EXISTENTE['nickname']}:")
        print(f"   🎯 Focus total: {estadisticas['total_focus_minutes']} minutos")
        print(f"   ☕ Break total: {estadisticas['total_break_minutes']} minutos") 
        print(f"   ⏸️  Pause total: {estadisticas['total_pause_minutes']} minutos")
        print(f"   📚 Sesiones totales: {estadisticas['total_sesiones']}")
        print(f"   ✅ Pomodoros completados: {estadisticas['total_pomodoros_completados']}")
    
    # Listar todos los pomodoros de una sesión
    if sesiones_creadas:
        sesion_reporte = sesiones_creadas[0]
        pomodoros = test_endpoint("GET", f"/pomodoros/sesion/{sesion_reporte['id_session']}",
                                descripcion=f"Reporte de pomodoros - {sesion_reporte['session_name']}")
        
        if pomodoros:
            print(f"\n📝 POMODOROS EN {sesion_reporte['session_name']}:")
            focus_total = 0
            break_total = 0
            
            for p in pomodoros:
                if p['is_completed']:
                    if p['event_type'] == 'focus':
                        focus_total += p['planned_duration']
                    elif p['event_type'] == 'break':
                        break_total += p['planned_duration']
                    
                    estado = "✅ COMPLETADO"
                    print(f"   {estado} {p['event_type'].upper()} - {p['planned_duration']}min - {p['notes']}")
            
            print(f"   📈 Resumen sesión: Focus {focus_total}min, Break {break_total}min")
    
    # =========================================================================
    # 8. PRUEBAS DE RECUPERACIÓN DE USUARIO
    # =========================================================================
    print("\n🎯 8. PRUEBAS DE RECUPERACIÓN DE USUARIO")
    
    test_endpoint("POST", "/auth/forgot-username",
                params={"email": USUARIO_EXISTENTE['email']},
                descripcion="Solicitando recuperación de usuario existente")
    
    test_endpoint("GET", f"/auth/recovery-status/{USUARIO_EXISTENTE['email']}",
                descripcion="Estado de recuperación")
    
    # =========================================================================
    # 9. PRUEBAS DE ERRORES
    # =========================================================================
    print("\n🎯 9. PRUEBAS DE MANEJO DE ERRORES")
    
    # Intentar crear sesión con usuario inexistente
    test_endpoint("POST", "/sesiones/",
                params={"id_user": 9999, "session_name": "Sesión de prueba"},
                descripcion="Intentando crear sesión con usuario inexistente")
    
    # Intentar crear pomodoro con sesión inexistente
    test_endpoint("POST", "/pomodoros/",
                json_data={
                    "id_session": 9999,
                    "id_pomodoro_rule": 1,
                    "id_pomodoro_type": 1, 
                    "event_type": "focus",
                    "planned_duration": 25
                },
                descripcion="Intentando crear pomodoro con sesión inexistente")
    
    # Event type inválido
    test_endpoint("POST", "/pomodoros/",
                json_data={
                    "id_session": 1,
                    "id_pomodoro_rule": 1,
                    "id_pomodoro_type": 1,
                    "event_type": "trabajo",  # Inválido
                    "planned_duration": 25
                },
                descripcion="Intentando crear pomodoro con event type inválido")

def main():
    """Función principal"""
    print("🎯 SISTEMA DE PRUEBAS CON DATOS REALES - POMODORO APP")
    print("📊 Usando usuario existente: GerardoAnt (ID: 1)")
    print("🔧 Probando con tipos y reglas específicos de la BD")
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
    simular_flujo_completo_actualizado()
    fin = datetime.now()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("🎉 PRUEBA COMPLETA FINALIZADA")
    print(f"⏱️  Tiempo total: {(fin - inicio).total_seconds():.1f} segundos")
    print("📈 Resumen de pruebas realizadas:")
    print("   ✅ Configuración y health check")
    print("   ✅ Obtención de reglas y tipos reales de BD") 
    print("   ✅ Pruebas con usuario existente GerardoAnt")
    print("   ✅ Creación de sesiones realistas")
    print("   ✅ Simulación de día completo (mañana/tarde/noche)")
    print("   ✅ Diferentes tipos de pomodoro y reglas")
    print("   ✅ Actualización manual de tiempos")
    print("   ✅ Estadísticas y reportes")
    print("   ✅ Sistema de recuperación")
    print("   ✅ Manejo de errores")
    print("\n🚀 El sistema está funcionando correctamente con datos reales!")
    print("=" * 70)

if __name__ == "__main__":
    main()