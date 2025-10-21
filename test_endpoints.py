import requests
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, params=None, json_data=None):
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", params=params, json=json_data)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", params=params, json=json_data)
        
        print(f"\n🔹 {method} {endpoint}")
        print(f"📊 Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success!")
            print(f"📦 Response: {response.json()}")
        else:
            print("❌ Error!")
            print(f"💬 Message: {response.text}")
        
        return response.json() if response.status_code == 200 else None
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

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
    
    # Extraer IDs de las reglas y tipos
    regla_facil_id = reglas[0]['id_pomodoro_rule'] if reglas else 1
    tipo_estudio_id = next((t['id_pomodoro_type'] for t in tipos if t['name_type'] == 'Estudio'), 1) if tipos else 1
    
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
        "session_name": "Lectura - Don Quijote"
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
    
    # 13. Iniciar pomodoro de focus
    pomodoro_response = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_facil_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "focus",
        "planned_duration": 25,
        "notes": "Lectura capítulos 1-3"
    })
    pomodoro_id = pomodoro_response['pomodoro']['id_pomodoro_detail'] if pomodoro_response else 1

    print("⏳ Esperando 2 minutos para simular trabajo real...")
    time.sleep(120)  # Esperar 2 minutos para simular trabajo real

    # 14. Completar pomodoro (ahora calculará duración real automáticamente)
    completar_response = test_endpoint("PUT", f"/pomodoros/{pomodoro_id}/completar")
    if completar_response:
        print(f"⏱️  Duración planeada: {completar_response['pomodoro']['planned_duration']} min")
        print(f"⏱️  Duración real: {completar_response['pomodoro']['actual_duration']} min")
    
    print("⏳ Esperando 1 minuto antes del descanso...")
    time.sleep(60)
    
    # 15. Iniciar pomodoro de break
    break_response = test_endpoint("POST", "/pomodoros/", {
        "id_session": sesion_id,
        "id_pomodoro_rule": regla_facil_id,
        "id_pomodoro_type": tipo_estudio_id,
        "event_type": "break",
        "planned_duration": 5,
        "notes": "Descanso después de lectura"
    })
    break_id = break_response['pomodoro']['id_pomodoro_detail'] if break_response else 1

    print("⏳ Esperando 1 minuto de descanso...")
    time.sleep(60)
    
    # 16. Completar pomodoro de break
    test_endpoint("PUT", f"/pomodoros/{break_id}/completar")
    
    # 17. Iniciar pausa durante un pomodoro
    pausa_response = test_endpoint("POST", "/pausas/", {
        "id_pomodoro_detail": pomodoro_id
    })
    pausa_id = pausa_response['pausa']['id_pause'] if pausa_response else 1
    
    print("⏳ Esperando 30 segundos de pausa...")
    time.sleep(30)
    
    # 18. Finalizar pausa
    test_endpoint("PUT", f"/pausas/{pausa_id}/finalizar")
    
    # 19. Listar pomodoros de la sesión
    test_endpoint("GET", f"/pomodoros/sesion/{sesion_id}")
    
    # 20. Ver sesiones actualizadas
    test_endpoint("GET", f"/sesiones/usuario/{usuario_id}")
    
    # 21. Estadísticas del usuario
    test_endpoint("GET", f"/estadisticas/usuario/{usuario_id}")
    
    # 22. Información del sistema
    test_endpoint("GET", "/info")
    
    print("\n🎉 Pruebas completadas!")

def test_advanced_scenarios():
    print("\n🔥 Iniciando pruebas avanzadas...")
    
    # Crear otro usuario para pruebas adicionales
    usuario2_response = test_endpoint("POST", "/usuarios/", {"nickname": "Maria"})
    if usuario2_response:
        usuario2_id = usuario2_response['usuario']['id_user']
        usuario2_nickname = usuario2_response['usuario']['nickname']
        
        # Obtener usuario por nickname
        test_endpoint("GET", f"/usuarios/nickname/{usuario2_nickname}")
        
        # Crear múltiples sesiones
        sesion1_response = test_endpoint("POST", "/sesiones/", {
            "id_user": usuario2_id,
            "session_name": "Trabajo - Proyecto API"
        })
        
        sesion2_response = test_endpoint("POST", "/sesiones/", {
            "id_user": usuario2_id, 
            "session_name": "Estudio - Matemáticas"
        })
        
        # Actualizar minutos en ambas sesiones
        if sesion1_response:
            sesion1_id = sesion1_response['sesion']['id_session']
            test_endpoint("PUT", f"/sesiones/{sesion1_id}/total_focus", {"minutos": 45})
            test_endpoint("PUT", f"/sesiones/{sesion1_id}/total_break", {"minutos": 10})
        
        if sesion2_response:
            sesion2_id = sesion2_response['sesion']['id_session']
            test_endpoint("PUT", f"/sesiones/{sesion2_id}/total_focus", {"minutos": 30})
            test_endpoint("PUT", f"/sesiones/{sesion2_id}/total_pause", {"minutos": 5})
        
        # Listar todas las sesiones del usuario
        test_endpoint("GET", f"/sesiones/usuario/{usuario2_id}")
        
        # Ver estadísticas del segundo usuario
        test_endpoint("GET", f"/estadisticas/usuario/{usuario2_id}")

def test_error_scenarios():
    print("\n🚨 Probando escenarios de error...")
    
    # Usuario no existente
    test_endpoint("GET", "/usuarios/999")
    test_endpoint("GET", "/usuarios/nickname/usuario_inexistente")
    
    # Sesión no existente
    test_endpoint("GET", "/sesiones/usuario/999")
    test_endpoint("PUT", "/sesiones/999/total_focus", {"minutos": 10})
    
    # Pomodoro no existente
    test_endpoint("PUT", "/pomodoros/999/completar")
    
    # Pausa no existente
    test_endpoint("PUT", "/pausas/999/finalizar")
    
    # Crear usuario con nickname duplicado
    test_endpoint("POST", "/usuarios/", {"nickname": "Julian"})
    
    # Event type inválido
    test_endpoint("POST", "/pomodoros/", {
        "id_session": 1,
        "id_pomodoro_rule": 1,
        "id_pomodoro_type": 1,
        "event_type": "invalid_type",
        "planned_duration": 25
    })

if __name__ == "__main__":
    run_tests()
    test_advanced_scenarios()
    test_error_scenarios()