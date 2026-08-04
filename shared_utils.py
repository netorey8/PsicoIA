"""
shared_utils.py — Funciones y configuraciones compartidas para PsicoAI Pro (Escritorio y Web).
"""

import os
import json
import re

# Nombre de la aplicación y directorio base
APP_NAME = "PsicoAIPro"

# Términos de privacidad predeterminados
PRIVACY_TERMS_TEXT = (
    "Bienvenido a PsicoAI Pro.\n\n"
    "Por favor, lea con atención la siguiente información sobre el uso de esta aplicación:\n\n"
    "1. NATURALEZA DEL SERVICIO\n"
    "Esta aplicación es un asistente de apoyo emocional y acompañamiento psicoeducativo basado en inteligencia artificial y libros de autores en psicología y salud mental.\n"
    "NO ES un psicólogo clínico, no es un terapeuta y no reemplaza la terapia, consulta o tratamiento psicológico o médico humano. "
    "Si usted está experimentando una crisis de salud mental severa o pensamientos de autolesión, por favor busque ayuda profesional presencial de inmediato.\n\n"
    "2. PROCESAMIENTO DE DATOS POR TERCEROS\n"
    "La aplicación utiliza la API de Groq para procesar las respuestas del chat. Sus mensajes se envían de forma cifrada a través de internet a sus servidores para generar las respuestas. No envíe información de identificación personal altamente sensible.\n\n"
    "3. PRIVACIDAD Y REGISTRO LOCAL\n"
    "Esta aplicación no almacena el historial de chat de forma permanente. Las notas clínicas y el perfil conductual temporal se guardan en la memoria únicamente durante su sesión actual. Al presionar 'Nueva Sesión' o cerrar la aplicación, esta información se reiniciará.\n\n"
    "Al continuar, usted declara que comprende estas limitaciones y acepta el uso del servicio bajo estos términos."
)

DISCLAIMER_EXPORT_TEXT = (
    "⚠️ ADVERTENCIA DE USO RESPONSABLE:\n"
    "Este resumen ha sido generado automáticamente por un asistente de Inteligencia Artificial "
    "con fines exclusivamente psicoeducativos y de auto-reflexión. NO constituye un diagnóstico "
    "clínico, evaluación psicológica oficial ni prescripción médica. Maneje esta información con cautela y "
    "consulte a un profesional de la salud mental certificado para cualquier valoración clínica.\n"
    "=========================================================================\n\n"
)

def get_appdata_dir() -> str:
    """Devuelve la ruta del directorio base de datos de la app."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    path = os.path.join(appdata, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path

def get_settings_path() -> str:
    """Ruta al archivo de configuraciones settings.json."""
    return os.path.join(get_appdata_dir(), "settings.json")

def get_books_dir() -> str:
    """Devuelve el directorio de libros (local o en appdata)."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        # En entornos Linux/Cloud, usar la carpeta local 'books'
        repo_books = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books")
        os.makedirs(repo_books, exist_ok=True)
        return repo_books
    bdir = os.path.join(get_appdata_dir(), "books")
    os.makedirs(bdir, exist_ok=True)
    return bdir

def mask_api_key(key: str) -> str:
    """Muestra solo los últimos 4 caracteres de la API Key para mayor seguridad visual."""
    if not key or len(key) < 8:
        return ""
    return f"gsk_...{key[-4:]}"

def load_saved_settings() -> dict:
    """Carga configuraciones guardadas de settings.json sin exponer valores nulos."""
    path = get_settings_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"consent_granted": False, "api_key": ""}

def save_settings(consent_granted: bool, api_key: str):
    """Guarda configuraciones en settings.json."""
    path = get_settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"consent_granted": consent_granted, "api_key": api_key}, f)
    except Exception as e:
        print(f"Error guardando settings: {e}")
