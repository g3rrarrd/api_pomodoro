import requests
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, params=None, json_data=None):
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}", params=params)
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", params=params)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", params=params)
        
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
    
    # 3. Crear usuario
    test_endpoint("POST", "/usuarios/", {"nickname": "Julian"})
    
    # 4. Listar usuarios
    test_endpoint("GET", "/usuarios/")
    
    # 5. Crear sesión
    test_endpoint("POST", "/sesiones/", {
        "id_usuario": 3,
        "nombre_sesion": "Lectura",
        "descripcion": "Don quijote"
    })
    
    # 6. Listar sesiones del usuario
    test_endpoint("GET", "/sesiones/usuario/3")
    
    # 7. Iniciar pomodoro
    test_endpoint("POST", "/pomodoros/", {
        "id_sesion": 6,
        "duracion_actividad": 20,
        "duracion_descanso": 5
    })
    
    time.sleep(2)  # Esperar un poco
   
    
    # 9. Listar pomodoros
    test_endpoint("GET", "/pomodoros/sesion/3")
    
    # 10. Estadísticas
    test_endpoint("GET", "/estadisticas/usuario/3")
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    run_tests()