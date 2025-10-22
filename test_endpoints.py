import requests
import time
import random

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
        
        return response.json() if response.status_code == 200 else None
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

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

def run_tests():
    print("🚀 Iniciando pruebas de endpoints...\n")
    
    # 1. Health check
    test_endpoint("GET", "/health")
    
    # 2. Root
    test_endpoint("GET", "/")
    
    # 3. Obtener reglas y tipos disponibles
    print("\n📋 Obteniendo reglas y tipos disponibles...")
    reglas = test_endpoint("GET", "/reglas-pomodoro/")
    tipos = test_endpoint("GET", "/tipos-pomodoro/")
    
    # Usar nombres reales de las reglas
    regla_paso_bebe_id = encontrar_regla_por_nombre(reglas, "Paso de bebe")
    regla_popular_id = encontrar_regla_por_nombre(reglas, "Popular")
    regla_medio_id = encontrar_regla_por_nombre(reglas, "Medio")
    
    tipo_estudio_id = encontrar_tipo_por_nombre(tipos, "Estudio")
    tipo_trabajo_id = encontrar_tipo_por_nombre(tipos, "Trabajo")
    tipo_descanso_id = encontrar_tipo_por_nombre(tipos, "Descanso Activo")
    
    # 4. Crear usuario
    usuario_response = test_endpoint("POST", "/usuarios/", {"nickname": "Julian"})
    usuario_id = usuario_response['usuario']['id_user'] if usuario_response else 1
    usuario_nickname = usuario_response['usuario']['nickname'] if usuario_response else "Julian"
    
    # 5. Listar usuarios
    test_endpoint("GET", "/usuarios/")
    
    # 6. Obtener usuario por ID
    test_endpoint("GET", f"/usuarios/{usuario_id}")
    
    # 7. Obtener usuario por nickname
    test_endpoint("GET", f"/usuarios/nickname/{usuario_nickname}")
    
    # 8. Crear sesión
    sesion_response = test_endpoint("POST", "/sesiones/", {
        "id_user": usuario_id,
        "session_name": "Estudio - Matemáticas Avanzadas"
    })
    sesion_id = sesion_response['sesion']['id_session'] if sesion_response else 1
    
    # 9. Listar sesiones del usuario
    test_endpoint("GET", f"/sesiones/usuario/{usuario_id}")
    
    # 10. Actualizar minutos de foco manualmente
    test_endpoint("PUT", f"/sesiones/{sesion_id}/total_focus", {"minutos": 10})
    
    # 11. Actualizar minutos de descanso manualmente
    test_endpoint("PUT", f"/sesiones/{sesion_id}/total_break", {"minutos": 3})
    
    # 12. Actualizar minutos de pausa manualmente
    test_endpoint("PUT", f"/sesiones/{sesion_id}/total_pause", {"minutos": 2})
    
    # 13. Iniciar pomodoro de focus (Paso de bebe - 10 minutos)
    pomodoro_response = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_paso_bebe_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 10,
        "notes": "Álgebra básica - Calentamiento"
    }, descripcion="Iniciando Pomodoro Focus (Paso de bebe)")
    pomodoro_id = pomodoro_response['pomodoro']['id_pomodoro_detail'] if pomodoro_response else 1

    # 14. Completar pomodoro inmediatamente (sin esperar tiempo real)
    completar_response = test_endpoint("PUT", f"/pomodoros/{pomodoro_id}/completar")
    if completar_response:
        print(f"⏱️  Duración planeada: {completar_response['pomodoro']['planned_duration']} min")
        print("✅ Pomodoro completado inmediatamente (sin tiempo real)")
    
    # 15. Iniciar pomodoro de break (Popular - 5 minutos)
    break_response = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_popular_id,
        "id_pomodoro_type": tipo_descanso_id,
        "event_type": "break",
        "planned_duration": 5,
        "notes": "Descanso corto después de estudio"
    }, descripcion="Iniciando Pomodoro Break (Popular)")
    break_id = break_response['pomodoro']['id_pomodoro_detail'] if break_response else 1
    
    # 16. Completar pomodoro de break inmediatamente
    test_endpoint("PUT", f"/pomodoros/{break_id}/completar", descripcion="Completando break")
    
    # 17. Iniciar pomodoro de focus más largo (Medio - 40 minutos)
    p2_response = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_medio_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 40,
        "notes": "Cálculo avanzado - Derivadas complejas"
    }, descripcion="Iniciando Pomodoro Focus Largo (Medio)")
    p2_id = p2_response['pomodoro']['id_pomodoro_detail'] if p2_response else 1
    
    # 18. Iniciar pausa durante el pomodoro
    pausa_response = test_endpoint("POST", "/pausas/", {
        "id_pomodoro_detail": p2_id
    }, descripcion="Iniciando pausa durante pomodoro")
    pausa_id = pausa_response['pausa']['id_pause'] if pausa_response else 1
    
    # 19. Finalizar pausa inmediatamente
    test_endpoint("PUT", f"/pausas/{pausa_id}/finalizar", descripcion="Finalizando pausa")
    
    # 20. Completar el pomodoro largo
    test_endpoint("PUT", f"/pomodoros/{p2_id}/completar", descripcion="Completando pomodoro largo")
    
    # 21. Listar pomodoros de la sesión
    test_endpoint("GET", f"/pomodoros/sesion/{sesion_id}", descripcion="Listando todos los pomodoros")
    
    # 22. Ver sesiones actualizadas
    test_endpoint("GET", f"/sesiones/usuario/{usuario_id}", descripcion="Sesiones actualizadas")
    
    # 23. Estadísticas del usuario
    estadisticas = test_endpoint("GET", f"/estadisticas/usuario/{usuario_id}", descripcion="Estadísticas del usuario")
    if estadisticas:
        print(f"\n📊 RESUMEN ESTADÍSTICAS:")
        print(f"   Focus total: {estadisticas['total_focus_minutes']} min")
        print(f"   Break total: {estadisticas['total_break_minutes']} min")
        print(f"   Pause total: {estadisticas['total_pause_minutes']} min")
        print(f"   Sesiones: {estadisticas['total_sesiones']}")
        print(f"   Pomodoros completados: {estadisticas['total_pomodoros_completados']}")
    
    # 24. Información del sistema
    test_endpoint("GET", "/info")
    
    print("\n🎉 Pruebas completadas!")

def test_advanced_scenarios():
    print("\n🔥 Iniciando pruebas avanzadas...")
    
    # Crear otro usuario para pruebas adicionales
    usuario2_response = test_endpoint("POST", "/usuarios/", {"nickname": "Maria_Programadora"})
    if usuario2_response:
        usuario2_id = usuario2_response['usuario']['id_user']
        usuario2_nickname = usuario2_response['usuario']['nickname']
        
        # Obtener usuario por nickname
        test_endpoint("GET", f"/usuarios/nickname/{usuario2_nickname}")
        
        # Obtener reglas y tipos nuevamente
        reglas = test_endpoint("GET", "/reglas-pomodoro/")
        tipos = test_endpoint("GET", "/tipos-pomodoro/")
        
        regla_intenso_id = encontrar_regla_por_nombre(reglas, "Intenso")
        regla_extendido_id = encontrar_regla_por_nombre(reglas, "Extendido")
        tipo_trabajo_id = encontrar_tipo_por_nombre(tipos, "Trabajo")
        tipo_desarrollo_id = encontrar_tipo_por_nombre(tipos, "Desarrollo de Habilidades")
        
        # Crear múltiples sesiones
        sesion1_response = test_endpoint("POST", "/sesiones/", {
            "id_user": usuario2_id,
            "session_name": "Desarrollo API - Sprint Actual"
        })
        
        sesion2_response = test_endpoint("POST", "/sesiones/", {
            "id_user": usuario2_id, 
            "session_name": "Estudio - Nuevas Tecnologías"
        })
        
        # Crear pomodoros en la primera sesión
        if sesion1_response:
            sesion1_id = sesion1_response['sesion']['id_session']
            
            # Pomodoro intenso de desarrollo
            p_intenso = test_endpoint("POST", "/pomodoros/", {
                "id_session": sesion1_id,
                "id_pomodoro_rule": regla_intenso_id,
                "id_pomodoro_type": tipo_desarrollo_id,
                "event_type": "focus",
                "planned_duration": 60,
                "notes": "Desarrollo de feature crítica"
            })
            if p_intenso:
                test_endpoint("PUT", f"/pomodoros/{p_intenso['pomodoro']['id_pomodoro_detail']}/completar")
            
            # Pomodoro extendido de trabajo
            p_extendido = test_endpoint("POST", "/pomodoros/", {
                "id_session": sesion1_id,
                "id_pomodoro_rule": regla_extendido_id,
                "id_pomodoro_type": tipo_trabajo_id,
                "event_type": "focus",
                "planned_duration": 80,
                "notes": "Revisión de código extensa"
            })
            if p_extendido:
                test_endpoint("PUT", f"/pomodoros/{p_extendido['pomodoro']['id_pomodoro_detail']}/completar")
        
        # Listar todas las sesiones del usuario
        test_endpoint("GET", f"/sesiones/usuario/{usuario2_id}")
        
        # Ver estadísticas del segundo usuario
        test_endpoint("GET", f"/estadisticas/usuario/{usuario2_id}")

def test_error_scenarios():
    print("\n🚨 Probando escenarios de error...")
    
    # Usuario no existente
    test_endpoint("GET", "/usuarios/999", descripcion="Usuario no existente")
    test_endpoint("GET", "/usuarios/nickname/usuario_inexistente", descripcion="Nickname no existente")
    
    # Sesión no existente
    test_endpoint("GET", "/sesiones/usuario/999", descripcion="Sesiones de usuario no existente")
    test_endpoint("PUT", "/sesiones/999/total_focus", {"minutos": 10}, descripcion="Actualizar sesión no existente")
    
    # Pomodoro no existente
    test_endpoint("PUT", "/pomodoros/999/completar", descripcion="Completar pomodoro no existente")
    
    # Pausa no existente
    test_endpoint("PUT", "/pausas/999/finalizar", descripcion="Finalizar pausa no existente")
    
    # Crear usuario con nickname duplicado
    test_endpoint("POST", "/usuarios/", {"nickname": "Julian"}, descripcion="Nickname duplicado")
    
    # Event type inválido
    test_endpoint("POST", "/pomodoros/", {
        "id_session": 1,
        "id_pomodoro_rule": 1,
        "id_pomodoro_type": 1,
        "event_type": "invalid_type",
        "planned_duration": 25
    }, descripcion="Event type inválido")
    
    # Regla y tipo no existentes
    test_endpoint("POST", "/pomodoros/", {
        "id_session": 1,
        "id_pomodoro_rule": 999,
        "id_pomodoro_type": 999,
        "event_type": "focus",
        "planned_duration": 25
    }, descripcion="Regla y tipo no existentes")

if __name__ == "__main__":
    run_tests()
    test_advanced_scenarios()
    test_error_scenarios()