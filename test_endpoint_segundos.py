import requests
import time
import random
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, params=None, json_data=None, descripcion=""):
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", params=params, json=json_data)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", params=params, json=json_data)
        
        print(f"\n🔹 {method} {endpoint}")
        if descripcion:
            print(f"📝 {descripcion}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success!")
            if "message" in response.json():
                print(f"💬 {response.json()['message']}")
            return response.json()
        else:
            print("❌ Error!")
            print(f"💬 Message: {response.text}")
            return None
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def esperar_y_mostrar(segundos, actividad):
    """Espera mostrando una cuenta regresiva"""
    print(f"\n⏳ {actividad} - Esperando {segundos} segundos...")
    for i in range(segundos, 0, -1):
        print(f"   {i}...", end=' ', flush=True)
        time.sleep(1)
    print("✅ Listo!")

def encontrar_regla_por_nombre(reglas, nombre):
    """Encuentra una regla por su nombre de dificultad"""
    for regla in reglas:
        if regla['difficulty_level'].lower() == nombre.lower():
            return regla['id_pomodoro_rule']
    return reglas[0]['id_pomodoro_rule'] if reglas else 1

def encontrar_tipo_por_nombre(tipos, nombre):
    """Encuentra un tipo por su nombre"""
    for tipo in tipos:
        if tipo['name_type'].lower() == nombre.lower():
            return tipo['id_pomodoro_type']
    return tipos[0]['id_pomodoro_type'] if tipos else 1

def simular_dia_estudio():
    """Simula un día completo de estudio de un usuario"""
    print("\n" + "="*60)
    print("🎓 SIMULACIÓN: DÍA DE ESTUDIO - USUARIO: Carlos")
    print("="*60)
    
    # Obtener reglas y tipos disponibles
    reglas = test_endpoint("GET", "/reglas-pomodoro/", descripcion="Obteniendo reglas disponibles")
    tipos = test_endpoint("GET", "/tipos-pomodoro/", descripcion="Obteniendo tipos disponibles")
    
    # Usar las reglas reales que tienes en la base de datos
    regla_paso_bebe_id = encontrar_regla_por_nombre(reglas, "Paso de bebe")
    regla_popular_id = encontrar_regla_por_nombre(reglas, "Popular")
    regla_medio_id = encontrar_regla_por_nombre(reglas, "Medio")
    
    tipo_estudio_id = encontrar_tipo_por_nombre(tipos, "Estudio")
    tipo_lectura_id = encontrar_tipo_por_nombre(tipos, "Lectura")
    tipo_descanso_id = encontrar_tipo_por_nombre(tipos, "Descanso Activo")
    
    # Crear usuario de estudio
    usuario = test_endpoint("POST", "/usuarios/", {"nickname": "Carlos_Estudiante"}, 
                           descripcion="Creando usuario Carlos")
    usuario_id = usuario['usuario']['id_user']
    
    # Crear sesión de estudio
    sesion = test_endpoint("POST", "/sesiones/", {
        "id_user": usuario_id,
        "session_name": "Estudio para Examen Final - Matemáticas"
    }, descripcion="Creando sesión de estudio")
    sesion_id = sesion['sesion']['id_session']
    
    print(f"\n📚 INICIANDO SESIÓN DE ESTUDIO - {datetime.now().strftime('%H:%M')}")
    
    # ===== BLOQUE 1: Estudio matutino =====
    print(f"\n🌅 BLOQUE 1: Estudio Matutino (3 Pomodoros)")
    
    # Pomodoro 1: Álgebra (Paso de bebe para calentar)
    p1 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_paso_bebe_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 10,
        "notes": "Álgebra - Calentamiento con ecuaciones lineales"
    }, descripcion="Iniciando Pomodoro 1: Álgebra (Paso de bebe)")
    p1_id = p1['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(10, "Pomodoro 1: Estudiando Álgebra")  # 10 min reales
    test_endpoint("PUT", f"/pomodoros/{p1_id}/completar", descripcion="Completando Pomodoro 1")
    
    # BREAK 1: Descanso corto
    print(f"\n☕ BREAK 1: Descanso de 5 minutos")
    b1 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_paso_bebe_id,
        "id_pomodoro_type": tipo_descanso_id,
        "event_type": "break",
        "planned_duration": 5,
        "notes": "Descanso - Café y estiramientos"
    }, descripcion="Iniciando break 1")
    b1_id = b1['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(5, "Break 1: Descansando")  # 5 min reales
    test_endpoint("PUT", f"/pomodoros/{b1_id}/completar", descripcion="Finalizando break 1")
    
    # Pomodoro 2: Cálculo (Popular - 25/5)
    p2 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_popular_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 25,
        "notes": "Cálculo - Derivadas e integrales"
    }, descripcion="Iniciando Pomodoro 2: Cálculo (Popular)")
    p2_id = p2['pomodoro']['id_pomodoro_detail']
    
    # PAUSA CORTA dentro del pomodoro
    esperar_y_mostrar(15, "Pomodoro 2: Estudiando Cálculo")  # 15 min reales
    
    pausa1 = test_endpoint("POST", "/pausas/", {
        "id_pomodoro_detail": p2_id
    }, descripcion="Pausa corta para estiramientos")
    pausa1_id = pausa1['pausa']['id_pause']
    
    esperar_y_mostrar(2, "Pausa corta")  # 2 min reales
    test_endpoint("PUT", f"/pausas/{pausa1_id}/finalizar", descripcion="Finalizando pausa")
    
    esperar_y_mostrar(10, "Pomodoro 2: Continuando Cálculo")  # 10 min reales
    test_endpoint("PUT", f"/pomodoros/{p2_id}/completar", descripcion="Completando Pomodoro 2")
    
    # BREAK 2: Descanso de 5 minutos (Popular)
    b2 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_popular_id,
        "id_pomodoro_type": tipo_descanso_id,
        "event_type": "break",
        "planned_duration": 5,
        "notes": "Descanso - Hidratación"
    }, descripcion="Iniciando break 2")
    b2_id = b2['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(5, "Break 2: Descansando")  # 5 min reales
    test_endpoint("PUT", f"/pomodoros/{b2_id}/completar", descripcion="Finalizando break 2")
    
    # Pomodoro 3: Estadística (Medio - 40/8)
    p3 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_medio_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 40,
        "notes": "Estadística - Probabilidad y distribuciones"
    }, descripcion="Iniciando Pomodoro 3: Estadística (Medio)")
    p3_id = p3['pomodoro']['id_pomodoro_detail']
    
    # PAUSA LARGA por interrupción
    esperar_y_mostrar(25, "Pomodoro 3: Estudiando Estadística")  # 25 min reales
    
    pausa2 = test_endpoint("POST", "/pausas/", {
        "id_pomodoro_detail": p3_id
    }, descripcion="Pausa larga - Llamada telefónica")
    pausa2_id = pausa2['pausa']['id_pause']
    
    esperar_y_mostrar(8, "Pausa larga - Interrupción")  # 8 min reales
    test_endpoint("PUT", f"/pausas/{pausa2_id}/finalizar", descripcion="Finalizando pausa larga")
    
    # Continuar pomodoro después de pausa
    esperar_y_mostrar(15, "Pomodoro 3: Continuando Estadística")  # 15 min reales
    test_endpoint("PUT", f"/pomodoros/{p3_id}/completar", descripcion="Completando Pomodoro 3")
    
    # BREAK 3: Descanso largo (Medio - 8 minutos)
    print(f"\n🌳 BREAK 3: Descanso largo de 8 minutos")
    b3 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_medio_id,
        "id_pomodoro_type": tipo_descanso_id,
        "event_type": "break",
        "planned_duration": 8,
        "notes": "Descanso largo - Caminata breve"
    }, descripcion="Iniciando break 3")
    b3_id = b3['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(8, "Break 3: Descanso largo")  # 8 min reales
    test_endpoint("PUT", f"/pomodoros/{b3_id}/completar", descripcion="Finalizando break 3")
    
    # ===== ALMUERZO =====
    print(f"\n🍽️  ALMUERZO: Descanso prolongado")
    # Usar regla personalizada para almuerzo largo
    almuerzo = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_popular_id,  # Usar Popular como base
        "id_pomodoro_type": tipo_descanso_id,
        "event_type": "break",
        "planned_duration": 45,
        "notes": "Almuerzo y descanso prolongado"
    }, descripcion="Iniciando descanso de almuerzo")
    almuerzo_id = almuerzo['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(45, "Almuerzo y descanso")  # 45 min reales
    test_endpoint("PUT", f"/pomodoros/{almuerzo_id}/completar", descripcion="Finalizando almuerzo")
    
    # ===== BLOQUE 2: Estudio vespertino =====
    print(f"\n🌇 BLOQUE 2: Estudio Vespertino (2 Pomodoros)")
    
    # Pomodoro 4: Lectura complementaria (Popular)
    p4 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_popular_id,
        "id_pomodoro_type": tipo_lectura_id,
        "event_type": "focus",
        "planned_duration": 25,
        "notes": "Lectura - Material complementario de matemáticas"
    }, descripcion="Iniciando Pomodoro 4: Lectura")
    p4_id = p4['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(25, "Pomodoro 4: Lectura complementaria")  # 25 min reales
    test_endpoint("PUT", f"/pomodoros/{p4_id}/completar", descripcion="Completando Pomodoro 4")
    
    # BREAK 4: Descanso final
    b4 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_popular_id,
        "id_pomodoro_type": tipo_descanso_id,
        "event_type": "break",
        "planned_duration": 5,
        "notes": "Descanso final - Reflexión del día"
    }, descripcion="Iniciando break final")
    b4_id = b4['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(5, "Break 4: Descanso final")  # 5 min reales
    test_endpoint("PUT", f"/pomodoros/{b4_id}/completar", descripcion="Finalizando break final")
    
    # Pomodoro 5: Ejercicios prácticos (Medio)
    p5 = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_medio_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 40,
        "notes": "Ejercicios prácticos - Problemas aplicados de todos los temas"
    }, descripcion="Iniciando Pomodoro 5: Ejercicios (Medio)")
    p5_id = p5['pomodoro']['id_pomodoro_detail']
    
    esperar_y_mostrar(40, "Pomodoro 5: Ejercicios prácticos")  # 40 min reales
    test_endpoint("PUT", f"/pomodoros/{p5_id}/completar", descripcion="Completando Pomodoro 5")
    
    # ===== FINALIZAR SESIÓN =====
    print(f"\n🎯 RESUMEN FINAL DE LA SESIÓN")
    test_endpoint("GET", f"/pomodoros/sesion/{sesion_id}", descripcion="Listando todos los pomodoros")
    test_endpoint("GET", f"/estadisticas/usuario/{usuario_id}", descripcion="Estadísticas finales")
    
    print(f"\n✅ SIMULACIÓN COMPLETADA - {datetime.now().strftime('%H:%M')}")

def simular_dia_trabajo():
    """Simula un día de trabajo de un desarrollador"""
    print("\n" + "="*60)
    print("💼 SIMULACIÓN: DÍA DE TRABAJO - USUARIO: Ana_Desarrolladora")
    print("="*60)
    
    reglas = test_endpoint("GET", "/reglas-pomodoro/")
    tipos = test_endpoint("GET", "/tipos-pomodoro/")
    
    regla_popular_id = encontrar_regla_por_nombre(reglas, "Popular")
    regla_medio_id = encontrar_regla_por_nombre(reglas, "Medio")
    regla_intenso_id = encontrar_regla_por_nombre(reglas, "Intenso")
    
    tipo_trabajo_id = encontrar_tipo_por_nombre(tipos, "Trabajo")
    tipo_desarrollo_id = encontrar_tipo_por_nombre(tipos, "Desarrollo de Habilidades")
    tipo_planificacion_id = encontrar_tipo_por_nombre(tipos, "Planificación y Organización")
    tipo_descanso_id = encontrar_tipo_por_nombre(tipos, "Descanso Activo")
    
    usuario = test_endpoint("POST", "/usuarios/", {"nickname": "Ana_Desarrolladora"})
    usuario_id = usuario['usuario']['id_user']
    
    sesion = test_endpoint("POST", "/sesiones/", {
        "id_user": usuario_id,
        "session_name": "Desarrollo API - Sprint Actual"
    })
    sesion_id = sesion['sesion']['id_session']
    
    # Flujo de trabajo típico usando las reglas reales
    actividades = [
        ("Revisión de código", 25, "Revisando PRs del equipo", regla_popular_id, tipo_trabajo_id),
        ("Reunión diaria", 15, "Daily stand-up meeting", regla_paso_bebe_id, tipo_planificacion_id),
        ("Desarrollo feature A", 60, "Implementando nueva funcionalidad", regla_intenso_id, tipo_desarrollo_id),
        ("Break café", 10, "Descanso y networking", regla_medio_id, tipo_descanso_id),
        ("Debugging issues", 40, "Resolviendo bugs críticos", regla_medio_id, tipo_trabajo_id),
        ("Reunión de planning", 40, "Planning del siguiente sprint", regla_medio_id, tipo_planificacion_id),
        ("Documentación", 25, "Documentando APIs", regla_popular_id, tipo_trabajo_id)
    ]
    
    for i, (actividad, duracion, notas, regla_id, tipo_id) in enumerate(actividades, 1):
        event_type = "break" if "break" in actividad.lower() or "reunión" in actividad.lower() else "focus"
        
        pomodoro = test_endpoint("POST", "/pomodoros/", {
            "id_session": sesion_id,
            "id_pomodoro_rule": regla_id,
            "id_pomodoro_type": tipo_id,
            "event_type": event_type,
            "planned_duration": duracion,
            "notes": notas
        }, descripcion=f"Iniciando actividad {i}: {actividad}")
        
        if pomodoro:
            p_id = pomodoro['pomodoro']['id_pomodoro_detail']
            esperar_y_mostrar(duracion, f"Actividad {i}: {actividad}")
            test_endpoint("PUT", f"/pomodoros/{p_id}/completar")
    
    # Resumen final
    test_endpoint("GET", f"/estadisticas/usuario/{usuario_id}", descripcion="Estadísticas de trabajo")

def main():
    print("🚀 INICIANDO SIMULACIONES REALES DE USUARIOS")
    print("⏰ NOTA: Estas simulaciones usan tiempos REALES")
    print("   Puedes reducir los tiempos en desarrollo cambiando esperar_y_mostrar()")
    
    # Simulación 1: Día de estudio
    simular_dia_estudio()
    
    # Simulación 2: Día de trabajo
    simular_dia_trabajo()
    
    print("\n🎉 TODAS LAS SIMULACIONES COMPLETADAS!")
    print("\n📊 RESUMEN GLOBAL:")
    test_endpoint("GET", "/usuarios/", descripcion="Todos los usuarios creados")

if __name__ == "__main__":
    main()