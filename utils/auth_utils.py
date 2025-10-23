import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jose import JWTError, jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import random
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Configuración SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
ALGORITHM = "HS256"
VERIFICATION_EXPIRE_MINUTES = int(os.getenv("VERIFICATION_EXPIRE_MINUTES", "10"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cache en memoria
verification_cache = {}

def generate_verification_code() -> str:
    """Genera un código de 6 dígitos"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def create_verification_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None):
    """Crea un JWT temporal para verificación"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_verification_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica y decodifica un JWT de verificación"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def send_verification_email(email: str, code: str) -> bool:
    """Envía código de verificación"""
    try:
        return send_email(email, code, "verificación")
    except Exception as e:
        print(f"Error enviando email de verificación: {str(e)}")
        return fallback_to_console(email, code, "verificación")

def send_recovery_email(email: str, code: str, username: str = None):
    """Envía email de recuperación"""
    try:
        return send_email(email, code, "recuperación", username)
    except Exception as e:
        print(f"Error enviando email de recuperación: {str(e)}")
        return fallback_to_console(email, code, "recuperación", username)

def send_username_reminder_email(email: str, username: str):
    """Envía recordatorio de username"""
    try:
        return send_username_email(email, username)
    except Exception as e:
        print(f"Error enviando recordatorio: {str(e)}")
        return fallback_username_to_console(email, username)

def send_email(email: str, code: str, tipo: str, username: str = None) -> bool:
    """Envía email usando SMTP con HTML profesional"""
    try:
        # Verificar configuración
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            print("Configuración SMTP incompleta")
            return False

        # Crear mensaje
        msg = MIMEMultipart("alternative")
        
        if tipo == "verificación":
            subject = "Tu Código de Verificación - Pomodoro App"
            html_content = create_verification_html(code)
            text_content = create_verification_text(code)
        else:  # recuperación
            subject = "Recuperación de Usuario - Pomodoro App"
            html_content = create_recovery_html(code)
            text_content = create_recovery_text(code)

        msg["Subject"] = subject
        msg["From"] = f"Pomodoro App <{SMTP_EMAIL}>"
        msg["To"] = email
        
        # Adjuntar ambas versiones
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Enviar email
        print(f"Enviando email {tipo} a {email}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        password_clean = SMTP_PASSWORD.replace(" ", "") if " " in SMTP_PASSWORD else SMTP_PASSWORD
        server.login(SMTP_EMAIL, password_clean)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())
        server.quit()
        
        print(f"Email de {tipo} enviado EXITOSAMENTE a {email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"ERROR DE AUTENTICACIÓN: {e}")
        return False
        
    except Exception as e:
        print(f"Error SMTP: {str(e)}")
        return False

def send_username_email(email: str, username: str) -> bool:
    """Envía recordatorio de username con HTML profesional"""
    try:
        # Verificar configuración
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            print("Configuración SMTP incompleta")
            return False

        # Crear mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Tu Usuario - Pomodoro App"
        msg["From"] = f"Pomodoro App <{SMTP_EMAIL}>"
        msg["To"] = email
        
        # Contenido
        html_content = create_username_html(username)
        text_content = create_username_text(username)
        
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        # Enviar email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.starttls()
        password_clean = SMTP_PASSWORD.replace(" ", "") if " " in SMTP_PASSWORD else SMTP_PASSWORD
        server.login(SMTP_EMAIL, password_clean)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())
        server.quit()
        
        print(f"Recordatorio de usuario enviado a {email}")
        return True
        
    except Exception as e:
        print(f"Error enviando recordatorio: {str(e)}")
        return False

# ============================================================
# TEMPLATES HTML PROFESIONALES
# ============================================================

def create_verification_html(code: str) -> str:
    """Crea HTML profesional para email de verificación"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verificación de Cuenta</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .header::before {{
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
                background-size: 20px 20px;
                animation: float 20s linear infinite;
            }}
            
            @keyframes float {{
                0% {{ transform: translate(0, 0) rotate(0deg); }}
                100% {{ transform: translate(-20px, -20px) rotate(360deg); }}
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
                position: relative;
            }}
            
            .header p {{
                font-size: 1.2em;
                opacity: 0.9;
                position: relative;
            }}
            
            .content {{
                padding: 50px 40px;
                text-align: center;
            }}
            
            .welcome {{
                font-size: 1.4em;
                color: #4F46E5;
                margin-bottom: 30px;
                font-weight: 600;
            }}
            
            .code-container {{
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 2px solid #e2e8f0;
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
                position: relative;
            }}
            
            .code {{
                font-size: 3.5em;
                font-weight: 800;
                color: #1e293b;
                letter-spacing: 10px;
                font-family: 'Courier New', monospace;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .instructions {{
                background: #f0f9ff;
                border-left: 4px solid #0ea5e9;
                padding: 20px;
                margin: 25px 0;
                border-radius: 10px;
                text-align: left;
            }}
            
            .instructions h3 {{
                color: #0369a1;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            
            .instructions ul {{
                list-style: none;
                padding-left: 0;
            }}
            
            .instructions li {{
                padding: 5px 0;
                position: relative;
                padding-left: 25px;
            }}
            
            .instructions li::before {{
                content: '✓';
                position: absolute;
                left: 0;
                color: #10b981;
                font-weight: bold;
            }}
            
            .expiry {{
                background: #fff7ed;
                border: 1px solid #fed7aa;
                border-radius: 10px;
                padding: 15px;
                margin: 20px 0;
                color: #ea580c;
                font-weight: 600;
            }}
            
            .footer {{
                background: #f8fafc;
                padding: 30px;
                text-align: center;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
            }}
            
            .social-links {{
                margin: 20px 0;
            }}
            
            .social-links a {{
                display: inline-block;
                margin: 0 10px;
                color: #4F46E5;
                text-decoration: none;
                font-weight: 600;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                
                .header {{
                    padding: 30px 20px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .code {{
                    font-size: 2.5em;
                    letter-spacing: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Pomodoro App</h1>
                <p>Tu compañero para una productividad efectiva</p>
            </div>
            
            <div class="content">
                <div class="welcome">¡Bienvenido a bordo!</div>
                
                <p>Estás a un paso de comenzar tu journey de productividad. Usa el siguiente código para verificar tu cuenta:</p>
                
                <div class="code-container">
                    <div class="code">{code}</div>
                </div>
                
                <div class="expiry">
                    Este código expirará en {VERIFICATION_EXPIRE_MINUTES} minutos
                </div>
                
                <div class="instructions">
                    <h3>Instrucciones rápidas:</h3>
                    <ul>
                        <li>Copia el código de arriba</li>
                        <li>Regresa a la aplicación Pomodoro</li>
                        <li>Pega el código en el campo de verificación</li>
                        <li>¡Comienza a ser más productivo!</li>
                    </ul>
                </div>
                
                <p style="color: #64748b; margin-top: 25px;">
                    Si no solicitaste crear una cuenta, puedes ignorar este mensaje de forma segura.
                </p>
            </div>
            
            <div class="footer">
                <div class="social-links">
                    <a href="#">Website</a>
                    <a href="#">App</a>
                    <a href="#">Soporte</a>
                </div>
                <p>© 2024 Pomodoro App. Todos los derechos reservados.</p>
                <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.7;">
                    Este es un email automático, por favor no respondas a este mensaje.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def create_recovery_html(code: str) -> str:
    """Crea HTML profesional para email de recuperación"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recuperación de Usuario</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #dc2626 0%, #ea580c 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .content {{
                padding: 50px 40px;
                text-align: center;
            }}
            
            .icon {{
                font-size: 4em;
                margin-bottom: 20px;
            }}
            
            .code-container {{
                background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
                border: 2px solid #fca5a5;
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }}
            
            .code {{
                font-size: 3.5em;
                font-weight: 800;
                color: #dc2626;
                letter-spacing: 10px;
                font-family: 'Courier New', monospace;
            }}
            
            .security-note {{
                background: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 10px;
                padding: 20px;
                margin: 25px 0;
                text-align: left;
            }}
            
            .security-note h3 {{
                color: #d97706;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .footer {{
                background: #f8fafc;
                padding: 30px;
                text-align: center;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .code {{
                    font-size: 2.5em;
                    letter-spacing: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Pomodoro App</h1>
                <p>Recuperación de Usuario</p>
            </div>
            
            <div class="content">
                <div class="icon">🔐</div>
                
                <h2 style="color: #dc2626; margin-bottom: 20px;">¿Olvidaste tu usuario?</h2>
                
                <p>No te preocupes, estamos aquí para ayudarte. Usa el siguiente código para verificar tu identidad y recuperar tu usuario:</p>
                
                <div class="code-container">
                    <div class="code">{code}</div>
                </div>
                
                <div class="security-note">
                    <h3>Nota de Seguridad</h3>
                    <p>Este código es personal e intransferible. No lo compartas con nadie y asegúrate de que solo tú tienes acceso a este email.</p>
                </div>
                
                <p style="color: #64748b; margin-top: 20px;">
                    Este código expirará en {VERIFICATION_EXPIRE_MINUTES} minutos
                </p>
                
                <p style="color: #64748b; margin-top: 25px;">
                    Si no solicitaste recuperar tu usuario, por favor ignora este mensaje o contacta a soporte.
                </p>
            </div>
            
            <div class="footer">
                <p>© 2024 Pomodoro App. Todos los derechos reservados.</p>
                <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.7;">
                    Protegiendo tu productividad y seguridad
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def create_username_html(username: str) -> str:
    """Crea HTML profesional para recordatorio de username"""
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tu Usuario - Pomodoro App</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }}
            
            .header {{
                background: linear-gradient(135deg, #059669 0%, #047857 100%);
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 700;
            }}
            
            .content {{
                padding: 50px 40px;
                text-align: center;
            }}
            
            .success-icon {{
                font-size: 4em;
                margin-bottom: 20px;
            }}
            
            .username-container {{
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border: 2px solid #10b981;
                border-radius: 15px;
                padding: 40px 30px;
                margin: 30px 0;
            }}
            
            .username-label {{
                font-size: 1.2em;
                color: #065f46;
                margin-bottom: 15px;
                font-weight: 600;
            }}
            
            .username {{
                font-size: 3em;
                font-weight: 800;
                color: #065f46;
                font-family: 'Courier New', monospace;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            }}
            
            .next-steps {{
                background: #f0f9ff;
                border-radius: 10px;
                padding: 25px;
                margin: 25px 0;
                text-align: left;
            }}
            
            .next-steps h3 {{
                color: #0369a1;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .next-steps ul {{
                list-style: none;
                padding-left: 0;
            }}
            
            .next-steps li {{
                padding: 8px 0;
                position: relative;
                padding-left: 30px;
            }}
            
            .next-steps li::before {{
                content: '🚀';
                position: absolute;
                left: 0;
            }}
            
            .footer {{
                background: #f8fafc;
                padding: 30px;
                text-align: center;
                color: #64748b;
                border-top: 1px solid #e2e8f0;
            }}
            
            @media (max-width: 600px) {{
                .container {{
                    margin: 10px;
                    border-radius: 15px;
                }}
                
                .header h1 {{
                    font-size: 2em;
                }}
                
                .content {{
                    padding: 30px 20px;
                }}
                
                .username {{
                    font-size: 2.2em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Pomodoro App</h1>
                <p>Tu Información de Usuario</p>
            </div>
            
            <div class="content">
                <div class="success-icon">✅</div>
                
                <h2 style="color: #059669; margin-bottom: 20px;">¡Aquí está tu usuario!</h2>
                
                <p>Según tu solicitud, aquí tienes tu información de usuario. Ya puedes iniciar sesión y continuar tu journey de productividad.</p>
                
                <div class="username-container">
                    <div class="username-label">Tu usuario es:</div>
                    <div class="username">{username}</div>
                </div>
                
                <div class="next-steps">
                    <h3>Próximos Pasos</h3>
                    <ul>
                        <li>Inicia sesión en la aplicación con tu usuario</li>
                        <li>Configura tu primera sesión de Pomodoro</li>
                        <li>Comienza a trackear tu productividad</li>
                        <li>Descubre insights sobre tus hábitos de trabajo</li>
                    </ul>
                </div>
                
                <p style="color: #64748b; margin-top: 20px;">
                    Si no solicitaste esta información, por favor contacta a nuestro equipo de soporte inmediatamente.
                </p>
            </div>
            
            <div class="footer">
                <p>© 2024 Pomodoro App. Todos los derechos reservados.</p>
                <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.7;">
                    Ayudándote a alcanzar tus metas, un Pomodoro a la vez
                </p>
            </div>
        </div>
    </body>
    </html>
    """

# ============================================================
# VERSIONES DE TEXTO PLANO (como fallback)
# ============================================================

def create_verification_text(code: str) -> str:
    return f"""
    POMODORO APP - VERIFICACIÓN DE CUENTA
    
    ¡Bienvenido a Pomodoro App!
    
    Tu código de verificación es: {code}
    
    Este código expirará en {VERIFICATION_EXPIRE_MINUTES} minutos.
    
    Instrucciones:
    1. Copia el código de arriba
    2. Regresa a la aplicación Pomodoro
    3. Pega el código en el campo de verificación
    4. ¡Comienza a ser más productivo!
    
    Si no solicitaste crear una cuenta, ignora este mensaje.
    
    --
    Pomodoro App
    Tu compañero para una productividad efectiva
    """

def create_recovery_text(code: str) -> str:
    return f"""
    POMODORO APP - RECUPERACIÓN DE USUARIO
    
    ¿Olvidaste tu usuario?
    
    Usa el siguiente código para verificar tu identidad:
    Código: {code}
    
    Este código expirará en {VERIFICATION_EXPIRE_MINUTES} minutos.
    
    Nota de seguridad: Este código es personal e intransferible.
    No lo compartas con nadie.
    
    Si no solicitaste recuperar tu usuario, ignora este mensaje.
    
    --
    Pomodoro App
    Protegiendo tu productividad y seguridad
    """

def create_username_text(username: str) -> str:
    return f"""
    POMODORO APP - TU USUARIO
    
    ¡Aquí está tu usuario!
    
    Tu usuario es: {username}
    
    Ya puedes iniciar sesión en la aplicación con este usuario.
    
    Próximos pasos:
    - Inicia sesión en la aplicación
    - Configura tu primera sesión de Pomodoro
    - Comienza a trackear tu productividad
    
    Si no solicitaste esta información, contacta a soporte.
    
    --
    Pomodoro App
    Ayudándote a alcanzar tus metas
    """

def fallback_to_console(email: str, code: str, tipo: str, username: str = None) -> bool:
    """Muestra código en consola como fallback"""
    print(f"\n=================================")
    print(f"{'VERIFICACIÓN' if tipo == 'verificación' else 'RECUPERACIÓN'}")
    print(f"Para: {email}")
    print(f"Código: {code}")
    if username:
        print(f"Usuario asociado: {username}")
    print(f"Expira en: {VERIFICATION_EXPIRE_MINUTES} minutos")
    print(f"=================================\n")
    return True

def fallback_username_to_console(email: str, username: str) -> bool:
    """Muestra username en consola"""
    print(f"\n=================================")
    print(f"RECORDATORIO DE USUARIO")
    print(f"Para: {email}")
    print(f"Tu usuario es: {username}")
    print(f"=================================\n")
    return True