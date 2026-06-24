import streamlit as st
import os
import json
import datetime
import asyncio
import base64
import shutil
import re
import sys

# Importar edge_tts de forma segura (puede fallar en algunos entornos)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Make sure imports from current directory work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from psychologist import PsychologistBot

DEFAULT_API_KEY = "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"

# ─────────────────────────────────────────────────────────────
# PATHS Y MIGRACIÓN A %APPDATA%
# ─────────────────────────────────────────────────────────────
def get_appdata_dir():
    # En la nube de Streamlit (Linux), APPDATA es None, por lo que usará la carpeta del usuario
    appdata = os.environ.get("APPDATA")
    if not appdata:
        appdata = os.path.expanduser("~")
    path = os.path.join(appdata, "PsicoAIPro")
    os.makedirs(path, exist_ok=True)
    return path

def get_settings_path():
    return os.path.join(get_appdata_dir(), "settings.json")

def get_books_dir():
    bdir = os.path.join(get_appdata_dir(), "books")
    os.makedirs(bdir, exist_ok=True)
    return bdir

def migrate_default_books():
    dest_books_dir = get_books_dir()
    src_books_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books")
    if os.path.exists(src_books_dir):
        for fname in os.listdir(src_books_dir):
            src_file = os.path.join(src_books_dir, fname)
            dest_file = os.path.join(dest_books_dir, fname)
            if os.path.isfile(src_file) and not os.path.exists(dest_file):
                try:
                    shutil.copy2(src_file, dest_file)
                except Exception as e:
                    print(f"Error migrating book {fname}: {e}")

# ─────────────────────────────────────────────────────────────
# TEXT TO SPEECH (edge-tts)
# ─────────────────────────────────────────────────────────────
async def get_voice_bytes(text, voice="es-MX-JorgeNeural"):
    import tempfile
    # Limpiar formato de markdown
    clean = re.sub(r"[\*\#\_\-\`]", "", text)
    clean = clean.replace('"', '""').replace('\n', ' ')
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_path = temp_file.name
    temp_file.close()
    try:
        communicate = edge_tts.Communicate(clean, voice)
        await communicate.save(temp_path)
        with open(temp_path, "rb") as f:
            data = f.read()
        return data
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def render_autoplay_audio(audio_bytes):
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio autoplay="true" style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN E INICIALIZACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="PsicoAI Pro", page_icon="🌿", layout="wide")

# Inicializar sesión y configuraciones
if "consent_granted" not in st.session_state:
    settings_path = get_settings_path()
    consent = False
    key = ""
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                consent = data.get("consent_granted", False)
                key = data.get("api_key", "")
        except Exception:
            pass
    st.session_state.consent_granted = consent
    st.session_state.api_key = key or DEFAULT_API_KEY

if "bot" not in st.session_state:
    migrate_default_books()
    st.session_state.bot = PsychologistBot(books_dir=get_books_dir(), api_key=st.session_state.api_key)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Hola, bienvenido a PsicoAI Pro. Estoy aquí para escucharte y acompañarte hoy en tu proceso de manera psicoeducativa y emocional. ¿Qué te gustaría compartir conmigo en esta sesión?",
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        }
    ]

if "emotions" not in st.session_state:
    st.session_state.emotions = {
        "calma": 45, "ansiedad": 15, "tristeza": 15, "ira": 10, "alegria": 15
    }

if "current_citation" not in st.session_state:
    st.session_state.current_citation = None

if "suggested_options" not in st.session_state:
    st.session_state.suggested_options = ["Me siento ansioso/a", "Tengo problemas para dormir", "Quiero hablar de una relación", "No sé por dónde empezar"]

if "play_audio_bytes" not in st.session_state:
    st.session_state.play_audio_bytes = None

if "save_profile" not in st.session_state:
    st.session_state.save_profile = True

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = False

# ─────────────────────────────────────────────────────────────
# FLUJO 1: PANTALLA DE CONSENTIMIENTO
# ─────────────────────────────────────────────────────────────
if not st.session_state.consent_granted:
    st.markdown("<h2 style='text-align: center; color: #7fa99b;'>🌿 Aviso de Privacidad y Consentimiento</h2>", unsafe_allow_html=True)
    
    # Contenedor centralizado para los términos
    terms_text = (
        "Bienvenido a PsicoAI Pro.\n\n"
        "Por favor, lea con atención la siguiente información sobre el uso de esta aplicación:\n\n"
        "1. NATURALEZA DEL SERVICIO\n"
        "Esta aplicación es un asistente de apoyo emocional y acompañamiento psicoeducativo basado en inteligencia artificial. "
        "NO ES un psicólogo clínico, no es un terapeuta y no reemplaza la terapia, consulta o tratamiento psicológico o médico humano. "
        "Si usted está experimentando una crisis de salud mental severa o pensamientos de autolesión, por favor busque ayuda profesional presencial de inmediato.\n\n"
        "2. PROCESAMIENTO DE DATOS POR TERCEROS\n"
        "La aplicación utiliza la API externa de Groq para procesar las respuestas del chat. Sus mensajes se envían de forma cifrada a través de internet a sus servidores para generar las respuestas. No envíe información de identificación personal altamente sensible (como nombres completos, direcciones o números de cuenta).\n\n"
        "3. PRIVACIDAD Y REGISTRO LOCAL\n"
        "Esta aplicación no almacena el historial de chat de forma permanente en archivos de texto. Las notas clínicas y el perfil conductual temporal se guardan en la memoria RAM únicamente durante su sesión actual. Al presionar 'Nueva Sesión' o cerrar la aplicación, toda esta información se destruirá por completo.\n\n"
        "Usted puede optar por desactivar el perfil temporal de sesión marcando la casilla correspondiente en el panel principal.\n\n"
        "Al hacer clic en 'Aceptar', usted declara que comprende estas limitaciones y acepta el uso del servicio bajo estos términos."
    )
    
    st.text_area("Términos de Privacidad", value=terms_text, height=320, disabled=True)
    
    st.warning("⚠️ **Nota importante sobre el navegador:** Si utilizas el traductor automático de Google Chrome (u otro navegador), esto puede causar errores inesperados en la aplicación (como `removeChild`). Por favor, desactiva la traducción automática para esta página o selecciona **'No traducir nunca este sitio'** para asegurar un funcionamiento correcto.")
    
    st.markdown("---")
    
    col_acc, col_dec = st.columns([1, 1])
    
    if col_acc.button("Aceptar y Continuar", type="primary", use_container_width=True):
        st.session_state.consent_granted = True
        st.session_state.bot.api_key = st.session_state.api_key
        
        # Guardar en settings.json
        settings_path = get_settings_path()
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump({"consent_granted": True, "api_key": st.session_state.api_key}, f)
        except Exception:
            pass
        st.rerun()
        
    if col_dec.button("Declinar y Salir", use_container_width=True):
        st.error("Has declinado los términos de uso. No es posible iniciar la aplicación.")
        st.stop()

# ─────────────────────────────────────────────────────────────
# FLUJO 2: INTERFAZ DE APLICACIÓN WEB PRINCIPAL
# ─────────────────────────────────────────────────────────────
else:
    # Lógica de procesamiento de inputs
    def process_chat_message(text):
        # 1. Agregar mensaje del usuario
        st.session_state.chat_history.append({
            "role": "user",
            "content": text,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })
        
        # 2. Consultar al Bot de IA
        res = st.session_state.bot.chat(text, save_profile=st.session_state.save_profile)
        
        # 3. Procesar y guardar respuesta del asistente
        respuesta = res.get("respuesta", "")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": respuesta,
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })
        
        # Actualizar variables de la sesión
        st.session_state.emotions = st.session_state.bot.emotions.copy()
        st.session_state.current_citation = res.get("cita_libro", None)
        st.session_state.suggested_options = res.get("opciones_respuesta", [])
        
        # Generar audio si está habilitado
        if st.session_state.voice_enabled and EDGE_TTS_AVAILABLE:
            try:
                # Ejecutar de forma segura la función asincrónica en streamlit
                audio_bytes = asyncio.run(get_voice_bytes(respuesta))
                st.session_state.play_audio_bytes = audio_bytes
            except Exception as e:
                print(f"Error generando audio en web app: {e}")

    # ─────────────────────────────────────────────────────────
    # BARRA LATERAL (SIDEBAR DE CONTROLES)
    # ─────────────────────────────────────────────────────────
    # Logo
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, use_container_width=True)
    else:
        st.sidebar.markdown("<h2 style='color: #7fa99b; margin-top:0;'>🌿 PsicoAI Pro</h2>", unsafe_allow_html=True)
        st.sidebar.caption("Acompañamiento Emocional & Psicoeducación")
    
    # 1. Selectores y Parámetros
    st.sidebar.markdown("---")
    
    # Enfoque Clínico
    approach_list = ["Terapia Cognitivo-Conductual (TCC)", "Logoterapia (Viktor Frankl)", "Terapia Humanista (Carl Rogers)", "Psicoanálisis (Sigmund Freud)"]
    selected_approach = st.sidebar.selectbox("Enfoque Clínico", options=approach_list, index=approach_list.index(st.session_state.bot.approach))
    if selected_approach != st.session_state.bot.approach:
        st.session_state.bot.set_approach(selected_approach)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"He ajustado el enfoque de nuestra sesión a: {selected_approach}. Cuéntame, ¿cómo quieres continuar?",
            "timestamp": datetime.datetime.now().strftime("%H:%M")
        })
        st.rerun()

    # Toggles de Perfil y Audio
    st.session_state.save_profile = st.sidebar.checkbox("Guardar perfil de sesión", value=st.session_state.save_profile, help="Permite a la IA recordar detalles clínicos del paciente en RAM de forma temporal.")
    st.session_state.voice_enabled = st.sidebar.checkbox("🔊 Habilitar voz de Alejandro", value=st.session_state.voice_enabled, help="La IA generará y reproducirá sus respuestas con una voz neuronal.")

    # Carga de Libros (dentro de un expander para ahorrar espacio vertical)
    st.sidebar.markdown("---")
    with st.sidebar.expander("📂 Añadir Libro a la Biblioteca"):
        # IMPORTANTE: usar st.file_uploader (sin prefijo sidebar) dentro de un expander de sidebar
        uploaded_file = st.file_uploader("Subir PDF/TXT", type=["pdf", "txt"])
        if uploaded_file is not None:
            books_dir = get_books_dir()
            dest_path = os.path.join(books_dir, uploaded_file.name)
            if not os.path.exists(dest_path):
                with open(dest_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                with st.spinner("Indexando libro..."):
                    st.session_state.bot.db.load_all_books()
                st.success(f"Libro '{uploaded_file.name}' indexado con éxito.")
            
    # 2. Medidor de Emociones
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h4 style='color: #d4c4b0;'>📊 Perfil Emocional Actual</h4>", unsafe_allow_html=True)
    
    emotions_config = [
        ("Calma", "calma", "#4cd137"),
        ("Ansiedad", "ansiedad", "#e1b12c"),
        ("Tristeza", "tristeza", "#00a8ff"),
        ("Ira", "ira", "#e84118"),
        ("Alegría", "alegria", "#fbc531")
    ]
    
    for name, key, color in emotions_config:
        val = st.session_state.emotions.get(key, 10)
        st.sidebar.progress(val / 100.0, text=f"{name}: {val}%")

    # 3. Respiración Guiada Interactiva (HTML/CSS)
    st.sidebar.markdown("---")
    breathing_html = """
    <style>
    .breathing-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: #1a2126;
        border: 1px solid #2c353d;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
    .circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 3px solid #7fa99b;
        animation: breathe 16s infinite ease-in-out;
    }
    .breathing-text {
        margin-top: 10px;
        font-size: 12px;
        color: #aaaaaa;
        font-style: italic;
        text-align: center;
        height: 20px;
    }
    .breathing-text::after {
        content: "💨 INHALA profundamente...";
        animation: text-content 16s infinite steps(1);
    }
    @keyframes breathe {
        0%, 100% { transform: scale(0.7); border-color: #7fa99b; }   /* Inhala inicio */
        25% { transform: scale(1.4); border-color: #e1b12c; }        /* Mantén lleno */
        50% { transform: scale(1.4); border-color: #00a8ff; }        /* Exhala inicio */
        75% { transform: scale(0.7); border-color: #e84118; }        /* Mantén vacío */
    }
    @keyframes text-content {
        0%, 100% { content: "💨 INHALA profundamente..."; color: #7fa99b; }
        25% { content: "🛑 MANTÉN el aire..."; color: #e1b12c; }
        50% { content: "🌬️ EXHALA despacio..."; color: #00a8ff; }
        75% { content: "🛑 MANTÉN vacío..."; color: #e84118; }
    }
    </style>
    <div class="breathing-container">
        <h5 style="color:#d4c4b0; margin:0 0 15px 0; font-family:sans-serif; font-size: 13px;">🧘 Respiración Guiada (4-4-4-4)</h5>
        <div class="circle"></div>
        <div class="breathing-text"></div>
    </div>
    """
    st.sidebar.markdown(breathing_html, unsafe_allow_html=True)
    
    # 4. Configurar API Key Expandible
    st.sidebar.markdown("---")
    with st.sidebar.expander("🔑 Configuración de API Key"):
        new_key = st.text_input("Groq API Key", value=st.session_state.api_key, type="password")
        if st.button("Guardar Clave", use_container_width=True):
            st.session_state.api_key = new_key
            st.session_state.bot.api_key = new_key
            settings_path = get_settings_path()
            try:
                with open(settings_path, "w", encoding="utf-8") as f:
                    json.dump({"consent_granted": True, "api_key": new_key}, f)
                st.success("Clave de API guardada correctamente.")
            except Exception:
                st.error("Error al guardar en settings.json.")

    # 5. Reiniciar Sesión
    if st.sidebar.button("🔄 Nueva Sesión", type="primary", use_container_width=True):
        st.session_state.bot.clear_session()
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "Sesión reiniciada. Estoy listo para escucharte. ¿De qué te gustaría hablar hoy?",
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            }
        ]
        st.session_state.emotions = {
            "calma": 45, "ansiedad": 15, "tristeza": 15, "ira": 10, "alegria": 15
        }
        st.session_state.current_citation = None
        st.session_state.suggested_options = ["Me siento ansioso/a", "Tengo problemas para dormir", "Quiero hablar de una relación", "No sé por dónde empezar"]
        st.session_state.play_audio_bytes = None
        st.rerun()

    # Nota de ayuda sobre traducción automática
    st.sidebar.markdown("---")
    st.sidebar.caption("⚠️ **¿Problemas de visualización?** Si la app se detiene con un error 'removeChild', desactiva la traducción automática de Google Chrome u otro navegador para este sitio.")

    # ─────────────────────────────────────────────────────────
    # ÁREA PRINCIPAL DE CONTENIDO (CHAT Y NOTAS CLÍNICAS)
    # ─────────────────────────────────────────────────────────
    tab_chat, tab_summary = st.tabs(["💬 Sesión de Acompañamiento", "📋 Resumen del Caso"])
    
    # ──── PESTAÑA 1: CHAT INTERACTIVO ────
    with tab_chat:
        # Renderizar historial de chat
        for msg in st.session_state.chat_history:
            avatar_style = "🌿" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar_style):
                st.write(msg["content"])
                st.caption(f"Enviado a las {msg['timestamp']}")

        # Reproducir audio asíncronamente si está en caché
        if st.session_state.play_audio_bytes:
            render_autoplay_audio(st.session_state.play_audio_bytes)
            st.session_state.play_audio_bytes = None # Consumir el audio

        # Opciones sugeridas interactivas
        if st.session_state.suggested_options:
            st.markdown("<p style='font-size:12px; color:#aaaaaa; margin-bottom:5px;'>Respuestas rápidas sugeridas:</p>", unsafe_allow_html=True)
            cols = st.columns(len(st.session_state.suggested_options))
            for idx, opt in enumerate(st.session_state.suggested_options):
                if cols[idx].button(opt, key=f"opt_{idx}", use_container_width=True):
                    process_chat_message(opt)
                    st.rerun()

        # Tarjeta de soporte de libros clínico (Citas RAG)
        if st.session_state.current_citation:
            cit = st.session_state.current_citation
            st.info(f"📖 **Soporte Teórico:** {cit.get('libro')} — {cit.get('autor')}\n\n*\"{cit.get('texto')}\"*")

        # Entrada de mensaje de usuario
        if prompt := st.chat_input("Escribe aquí cómo te sientes o qué pasa por tu mente..."):
            process_chat_message(prompt)
            st.rerun()

    # ──── PESTAÑA 2: RESUMEN CLÍNICO (EXPEDIENTE) ────
    with tab_summary:
        st.markdown("<h3 style='color: #7fa99b;'>📋 Expediente Psicoeducativo del Caso</h3>", unsafe_allow_html=True)
        st.caption(f"Resumen analítico recopilado bajo el enfoque: **{st.session_state.bot.approach}**")
        
        profile = st.session_state.bot.profile
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Temas Recurrentes")
            if profile.temas_recurrentes:
                for t in profile.temas_recurrentes:
                    st.markdown(f"- {t}")
            else:
                st.info("Sin temas detectados en esta sesión.")
                
            st.markdown("#### 🧠 Patrones Conductuales / Distorsiones")
            if profile.patrones_identificados:
                for p in profile.patrones_identificados:
                    st.markdown(f"- {p}")
            else:
                st.info("Sin patrones identificados aún.")
                
        with col2:
            st.markdown("#### 💪 Recursos y Fortalezas")
            if profile.recursos_personales:
                for r in profile.recursos_personales:
                    st.markdown(f"- {r}")
            else:
                st.info("Sin fortalezas registradas aún.")
                
            st.markdown("#### 👥 Vínculos Importantes")
            if profile.vinculos_importantes:
                for v in profile.vinculos_importantes:
                    st.markdown(f"- {v}")
            else:
                st.info("Sin vínculos registrados en el diálogo.")

        st.markdown("---")
        st.markdown("#### 📝 Registro de Notas Clínicas Consolidadas")
        if profile.notas_sesion:
            for idx, nota in enumerate(profile.notas_sesion, 1):
                st.text_area(f"Nota de Turno [{idx}]", value=nota, height=80, disabled=True, key=f"note_area_{idx}")
        else:
            st.info("No hay notas clínicas disponibles. Inicia una conversación activa para acumular observaciones.")

        # Lógica de formateo y descarga del archivo de texto
        summary_lines = []
        summary_lines.append("=========================================")
        summary_lines.append("         PSICOAI PRO - RESUMEN CLÍNICO")
        summary_lines.append("=========================================\n")
        summary_lines.append(f"Fecha de sesión: {datetime.date.today().strftime('%d/%m/%Y')}")
        summary_lines.append(f"Enfoque actual: {st.session_state.bot.approach}\n")
        
        summary_lines.append("🔍 TEMAS RECURRENTES:")
        if profile.temas_recurrentes:
            for t in profile.temas_recurrentes:
                summary_lines.append(f"  • {t}")
        else:
            summary_lines.append("  (Ninguno)")
            
        summary_lines.append("\n🧠 PATRONES CONDUCTUALES / DISTORSIONES:")
        if profile.patrones_identificados:
            for p in profile.patrones_identificados:
                summary_lines.append(f"  • {p}")
        else:
            summary_lines.append("  (Ninguno)")
            
        summary_lines.append("\n💪 RECURSOS Y FORTALEZAS:")
        if profile.recursos_personales:
            for r in profile.recursos_personales:
                summary_lines.append(f"  • {r}")
        else:
            summary_lines.append("  (Ninguno)")
            
        summary_lines.append("\n👥 VÍNCULOS IMPORTANTES:")
        if profile.vinculos_importantes:
            for v in profile.vinculos_importantes:
                summary_lines.append(f"  • {v}")
        else:
            summary_lines.append("  (Ninguno)")
            
        summary_lines.append("\n📝 HISTORIAL COMPLETO DE NOTAS CLÍNICAS:")
        if profile.notas_sesion:
            for idx, nota in enumerate(profile.notas_sesion, 1):
                summary_lines.append(f"  [{idx}] {nota}")
        else:
            summary_lines.append("  (Sin notas registradas)")
            
        export_text = "\n".join(summary_lines)
        
        st.markdown("---")
        st.download_button(
            label="📥 Descargar Reporte Clínico Completo (.txt)",
            data=export_text,
            file_name=f"Reporte_Clinico_PsicoAI_{datetime.date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
