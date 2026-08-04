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

# Asegurar importaciones locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from psychologist import PsychologistBot

from shared_utils import (
    get_appdata_dir,
    get_settings_path,
    get_books_dir,
    load_saved_settings,
    save_settings,
    mask_api_key,
    PRIVACY_TERMS_TEXT,
    DISCLAIMER_EXPORT_TEXT
)
from emotional_test import QUESTIONS, analyze_test_results

def migrate_default_books():
    """Solo necesario en Windows (escritorio). En la nube, los libros ya están en el repo."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return  # En Streamlit Cloud, no se necesita migración
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
    saved = load_saved_settings()
    st.session_state.consent_granted = saved.get("consent_granted", False)
    st.session_state.api_key = saved.get("api_key", os.environ.get("GROQ_API_KEY", ""))

if "bot" not in st.session_state:
    try:
        migrate_default_books()
        st.session_state.bot = PsychologistBot(books_dir=get_books_dir(), api_key=st.session_state.api_key)
        st.session_state.init_error = None
    except Exception as e:
        st.session_state.init_error = str(e)
        # Crear un bot minimo sin libros para no bloquear la app
        try:
            import tempfile
            empty_dir = tempfile.mkdtemp()
            st.session_state.bot = PsychologistBot(books_dir=empty_dir, api_key=st.session_state.api_key)
        except Exception:
            st.error(f"Error critico al iniciar: {e}")
            st.stop()


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
    st.text_area("Términos de Privacidad", value=PRIVACY_TERMS_TEXT, height=320, disabled=True)
    
    st.warning("⚠️ **Nota importante sobre el navegador:** Si utilizas el traductor automático de Google Chrome (u otro navegador), esto puede causar errores inesperados en la aplicación (como `removeChild`). Por favor, desactiva la traducción automática para esta página o selecciona **'No traducir nunca este sitio'** para asegurar un funcionamiento correcto.")
    
    st.markdown("---")
    
    col_acc, col_dec = st.columns([1, 1])
    
    if col_acc.button("Aceptar y Continuar", type="primary", use_container_width=True):
        st.session_state.consent_granted = True
        st.session_state.bot.api_key = st.session_state.api_key
        save_settings(True, st.session_state.api_key)
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
            
    # 2. Medidor de Emociones (Estimación Psicoeducativa)
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h4 style='color: #d4c4b0;'>📊 Estado Emocional (Estimación)</h4>", unsafe_allow_html=True)
    st.sidebar.caption("ℹ️ *Estimación conversacional basada en el diálogo, no constituye una medición clínica ni diagnóstico.*")
    
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

    tab_chat, tab_test, tab_summary = st.tabs(["💬 Sesión de Acompañamiento", "📊 Test de Patrones Emocionales", "📋 Resumen del Caso"])
    
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

    # ──── PESTAÑA 2: TEST DE PATRONES PSICOANALÍTICOS ────
    with tab_test:
        st.markdown("<h3 style='color: #7fa99b;'>🧬 Diagnosticador de Patrones Inconscientes e Heridas de la Infancia</h3>", unsafe_allow_html=True)
        st.markdown("""
        <p style='color: #aaaaaa; font-size: 14px;'>
        Este test explora los <strong>patrones emocionales programados en la infancia</strong> —heridas de abandono, 
        rechazo, humillación, parentificación y lealtades familiares— que suelen operar de forma inconsciente 
        en las relaciones y decisiones de la vida adulta. No evalúa tu estado de ánimo actual, sino tu 
        <strong>historia psicodinámica profunda</strong>.
        </p>
        """, unsafe_allow_html=True)
        st.caption("Responde con honestidad reflexiva. No hay respuestas correctas o incorrectas.")
        st.markdown("---")

        test_answers = {}
        for q in QUESTIONS:
            st.markdown(f"**{q['id']}. {q['pregunta']}**")
            opciones_text = [op[0] for op in q["opciones"]]
            selected_op_text = st.radio(
                f"q{q['id']}",
                opciones_text,
                key=f"q_{q['id']}",
                label_visibility="collapsed"
            )
            for text, pts in q["opciones"]:
                if text == selected_op_text:
                    test_answers[q["id"]] = pts
            st.markdown("---")

        if st.button("🔍 Analizar mi Patrón Profundo", type="primary", use_container_width=True):
            resultado = analyze_test_results(test_answers)
            st.session_state.test_result = resultado
            patron_name = resultado["patron"]
            if patron_name not in st.session_state.bot.profile.patrones_identificados:
                st.session_state.bot.profile.patrones_identificados.append(patron_name)
            nota_test = (
                f"TEST PSICOANALÍTICO: Patrón principal '{patron_name}'. "
                f"Patrón secundario: '{resultado.get('patron_secundario', 'N/A')}'. "
                f"Enfoque sugerido: {resultado['enfoque_sugerido']}."
            )
            st.session_state.bot.profile.agregar_nota(nota_test)
            st.rerun()

        if "test_result" in st.session_state and st.session_state.test_result:
            res = st.session_state.test_result
            certeza = res.get("certeza", 85)
            icono = res.get("icono", "🎯")

            # Resultado principal con % de certeza
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a2a2a 0%, #1e2d2d 100%);
                        border: 1px solid #7fa99b; border-radius: 12px; padding: 20px; margin-bottom: 16px;'>
                <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                    <div>
                        <h4 style='color: #7fa99b; margin: 0 0 8px 0;'>🎯 Patrón Principal Detectado</h4>
                        <h3 style='color: #ffffff; margin: 0 0 12px 0;'>{icono} {res['patron']}</h3>
                    </div>
                    <div style='background: #7fa99b; color: #0d1117; border-radius: 8px;
                                padding: 6px 14px; font-size: 18px; font-weight: bold; white-space: nowrap;'>
                        {certeza}% certeza
                    </div>
                </div>
                <p style='color: #cccccc; margin: 0;'>{res['descripcion']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Patrón secundario
            if res.get("patron_secundario"):
                ic2 = res.get("icono_secundario", "🔗")
                st.info(f"{ic2} **Patrón Secundario Presente:** {res['patron_secundario']}")

            # Manifestaciones
            if res.get("manifestaciones"):
                st.markdown("#### 🔎 Cómo suele manifestarse este patrón en tu vida:")
                for m in res["manifestaciones"]:
                    st.markdown(f"- {m}")

            st.markdown("---")

            # Enfoque recomendado
            st.markdown(f"""
            <div style='background: #1a2126; border: 1px solid #4a7a6a;
                        border-radius: 10px; padding: 16px; margin-bottom: 16px;'>
                <h4 style='color: #4cd137; margin: 0 0 6px 0;'>✨ Enfoque Terapéutico Recomendado</h4>
                <p style='color: #ffffff; font-size: 16px; font-weight: bold; margin: 0 0 10px 0;'>{res['enfoque_sugerido']}</p>
                <p style='color: #aaaaaa; margin: 0;'>💡 {res['recomendacion']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Mapear enfoque sugerido a los enfoques disponibles en el bot
            enfoque_map = {
                "Psicoanálisis (Teoría del Apego — John Bowlby / Donald Winnicott)": "Psicoanálisis (Sigmund Freud)",
                "Terapia Humanista (Carl Rogers) / Psicoanálisis del Self": "Terapia Humanista (Carl Rogers)",
                "Logoterapia (Viktor Frankl) / Psicoanálisis (Sigmund Freud)": "Logoterapia (Viktor Frankl)",
                "Terapia Cognitivo-Conductual (TCC) / Psicoanálisis Relacional": "Terapia Cognitivo-Conductual (TCC)",
                "Psicoanálisis Transgeneracional / Constelaciones Familiares (Bert Hellinger)": "Psicoanálisis (Sigmund Freud)"
            }
            enfoque_bot = enfoque_map.get(res["enfoque_sugerido"], "Terapia Cognitivo-Conductual (TCC)")

            if st.button(f"⚙️ Ajustar sesión al enfoque: '{enfoque_bot}'", use_container_width=True):
                st.session_state.bot.set_approach(enfoque_bot)
                patron = res["patron"]
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": (
                        f"He revisado los resultados de tu test de patrones psicoanalíticos. "
                        f"Según lo que exploraste, hay indicios de un patrón relacionado con: **{patron}**. "
                        f"He ajustado nuestra sesión al enfoque de **{enfoque_bot}** para acompañarte "
                        f"desde ese lugar más profundo. ¿Hay algún momento o recuerdo de tu historia "
                        f"que quieras empezar a explorar hoy?"
                    ),
                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                })
                st.success(f"✅ Sesión ajustada a: {enfoque_bot}. Regresa a la pestaña de chat.")
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
        summary_lines = [DISCLAIMER_EXPORT_TEXT]
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
        st.warning("⚠️ **Aviso:** Este resumen es generado automáticamente por Inteligencia Artificial de forma psicoeducativa. No constituye un diagnóstico ni evaluación psicológica formal.")
        st.download_button(
            label="📥 Descargar Reporte Clínico Completo (.txt)",
            data=export_text,
            file_name=f"Reporte_Clinico_PsicoAI_{datetime.date.today().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
