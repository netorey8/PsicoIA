import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import threading
from PIL import Image
import sys
import shutil
import json
import datetime
import tempfile
import uuid
import subprocess
import asyncio
import edge_tts
import ctypes

# Make sure imports from current directory work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from psychologist import PsychologistBot

# Global Styling
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_API_KEY = "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"

# ─────────────────────────────────────────────────────────────
# PATHS Y MIGRACIÓN A %APPDATA%
# ─────────────────────────────────────────────────────────────
def get_appdata_dir():
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
# DIÁLOGOS Y COMPONENTES DE CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────
class ConsentFrame(ctk.CTkFrame):
    def __init__(self, parent, on_accept, on_decline):
        super().__init__(parent, fg_color="#12161a")
        self.on_accept = on_accept
        self.on_decline = on_decline
        
        # Center container
        container = ctk.CTkFrame(self, fg_color="#1a2126", border_width=1, border_color="#2c353d", corner_radius=15)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.8)
        
        ctk.CTkLabel(container, text="Aviso de Privacidad y Consentimiento", font=("Segoe UI", 18, "bold"), text_color="#7fa99b").pack(pady=(15, 10))
        
        textbox = ctk.CTkTextbox(container, font=("Segoe UI", 12), fg_color="#222b31", border_color="#2c353d", border_width=1)
        textbox.pack(pady=10, padx=30, fill="both", expand=True)
        
        policy_text = (
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
        textbox.insert("1.0", policy_text)
        textbox.configure(state="disabled")
        
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        btn_accept = ctk.CTkButton(
            btn_frame, text="Aceptar y Continuar", font=("Segoe UI", 12, "bold"),
            fg_color="#7fa99b", text_color="#12161a", hover_color="#638d80",
            height=36, command=self.handle_accept
        )
        btn_accept.pack(side="left", padx=15)
        
        btn_decline = ctk.CTkButton(
            btn_frame, text="Declinar y Salir", font=("Segoe UI", 12, "bold"),
            fg_color="#e84118", text_color="#ffffff", hover_color="#c23616",
            height=36, command=self.on_decline
        )
        btn_decline.pack(side="left", padx=15)

    def handle_accept(self):
        self.on_accept()

class ApiKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_key, on_save):
        super().__init__(parent)
        self.title("Configuración de Groq API Key")
        self.geometry("450x200")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color="#1a2126")
        self.resizable(False, False)
        self.on_save = on_save
        
        ctk.CTkLabel(self, text="Clave de API de Groq", font=("Segoe UI", 14, "bold"), text_color="#7fa99b").pack(pady=15)
        
        self.api_entry = ctk.CTkEntry(self, width=380, placeholder_text="gsk_...", show="*", font=("Segoe UI", 11), fg_color="#222b31", border_color="#2c353d", border_width=1, height=32)
        self.api_entry.pack(pady=10)
        if current_key:
            self.api_entry.insert(0, current_key)
            
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        btn_save = ctk.CTkButton(
            btn_frame, text="Guardar", font=("Segoe UI", 12, "bold"),
            fg_color="#7fa99b", text_color="#12161a", hover_color="#638d80",
            width=100, command=self.handle_save
        )
        btn_save.pack(side="left", padx=10)
        
        btn_cancel = ctk.CTkButton(
            btn_frame, text="Cancelar", font=("Segoe UI", 12, "bold"),
            fg_color="#e84118", text_color="#ffffff", hover_color="#c23616",
            width=100, command=self.destroy
        )
        btn_cancel.pack(side="left", padx=10)
        
    def handle_save(self):
        new_key = self.api_entry.get().strip()
        if not new_key:
            messagebox.showerror("Error", "La clave de API no puede estar vacía.")
            return
        self.on_save(new_key)
        self.destroy()

class PrivacyDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Aviso de Privacidad")
        self.geometry("600x460")
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color="#1a2126")
        self.resizable(False, False)
        
        ctk.CTkLabel(self, text="Política de Privacidad y Manejo de Datos", font=("Segoe UI", 14, "bold"), text_color="#7fa99b").pack(pady=15)
        
        textbox = ctk.CTkTextbox(self, width=540, height=290, font=("Segoe UI", 11), fg_color="#222b31", border_color="#2c353d", border_width=1)
        textbox.pack(pady=10, padx=20)
        
        policy_text = (
            "POLÍTICA DE PRIVACIDAD Y MANEJO DE DATOS\n\n"
            "1. ALMACENAMIENTO LOCAL\n"
            "Esta aplicación no registra conversaciones en archivos de texto, bases de datos o logs en el disco local de su computadora. "
            "Cualquier análisis realizado por el asistente (como temas o patrones emocionales) permanece únicamente en la memoria RAM temporal de su computadora durante el transcurso de la sesión activa.\n\n"
            "2. PROCESAMIENTO DE IA\n"
            "Para generar las respuestas, las conversaciones son enviadas a través de una conexión HTTPS segura a la API externa de Groq (usando modelos abiertos Llama/Qwen). No se comparte información personal que no sea la que usted ingrese en la caja de diálogo.\n\n"
            "3. CONTROL DEL USUARIO\n"
            "Usted puede reiniciar el historial por completo en cualquier momento usando el botón 'Nueva Sesión'. Además, si lo desea, puede desactivar el guardado del perfil temporal desmarcando la casilla 'Guardar perfil de sesión' en la barra superior. Esto evitará que la IA acumule memoria conductual entre mensajes.\n\n"
            "4. CARGA DE LIBROS\n"
            "Los libros o reportes que cargue localmente mediante 'Añadir Libro' se copian a la carpeta de datos de la aplicación (%APPDATA%\\PsicoAIPro\\books\\) y se indexan en memoria local. Ningún contenido de sus libros es cargado en la web para entrenamiento."
        )
        textbox.insert("1.0", policy_text)
        textbox.configure(state="disabled")
        
        btn_close = ctk.CTkButton(
            self, text="Cerrar", font=("Segoe UI", 12, "bold"),
            fg_color="#7fa99b", text_color="#12161a", hover_color="#638d80",
            width=100, command=self.destroy
        )
        btn_close.pack(pady=15)

# ─────────────────────────────────────────────────────────────
# APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────────────────────
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("✦ PsicoAI Pro - Acompañamiento Emocional & Psicoeducación")
        self.geometry("1250x850")
        self.configure(fg_color="#12161a")
        
        # Current temp audio file reference
        self.current_temp_audio = None
        self.typing_frame = None
        self.typing_label = None
        
        # Clean up any leftover voice temp files
        self.cleanup_temp_files()
        
        # Migrate default books to %APPDATA%
        migrate_default_books()
        
        # Initialize AI Psychologist Engine in %APPDATA%\books
        self.bot = PsychologistBot(books_dir=get_books_dir())
        
        # Check consent before starting
        self.check_consent()
        
    def setup_ui(self):
        # Grid Configuration (3 columns: left sidebar, chat display, right sidebar)
        self.grid_columnconfigure(0, weight=0, minsize=260)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=300)
        self.grid_rowconfigure(0, weight=1)
        
        # ─────────────────────────────────────────────────────
        # 1. LEFT SIDEBAR (Panel Terapéutico y Control Emocional)
        # ─────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, fg_color="#1a2126", corner_radius=0, border_width=1, border_color="#2c353d")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            try:
                img = ctk.CTkImage(light_image=Image.open(logo_path), size=(120, 120))
                ctk.CTkLabel(self.sidebar, image=img, text="").pack(pady=(20, 5))
            except Exception:
                ctk.CTkLabel(self.sidebar, text="🌿", font=("Segoe UI", 50)).pack(pady=(20, 5))
        else:
            ctk.CTkLabel(self.sidebar, text="🌿", font=("Segoe UI", 50)).pack(pady=(20, 5))
            
        ctk.CTkLabel(self.sidebar, text="PsicoAI Pro", font=("Segoe UI", 22, "bold"), text_color="#7fa99b").pack(pady=(0, 20))
        
        # Medidor de Emociones
        emociones_frame = ctk.CTkFrame(self.sidebar, fg_color="#222b31", border_width=1, border_color="#2c353d", corner_radius=10)
        emociones_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(emociones_frame, text="📊 Perfil Emocional Actual", font=("Segoe UI", 13, "bold"), text_color="#d4c4b0").pack(pady=10)
        
        self.emotion_widgets = {}
        emotions_config = [
            ("Calma", "calma", "#4cd137"),
            ("Ansiedad", "ansiedad", "#e1b12c"),
            ("Tristeza", "tristeza", "#00a8ff"),
            ("Ira", "ira", "#e84118"),
            ("Alegría", "alegria", "#fbc531")
        ]
        
        for name, key, color in emotions_config:
            row = ctk.CTkFrame(emociones_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(row, text=name, font=("Segoe UI", 11), text_color="#aaaaaa", width=60, anchor="w").pack(side="left")
            
            pb = ctk.CTkProgressBar(row, progress_color=color, fg_color="#12161a", height=8)
            pb.pack(side="left", fill="x", expand=True, padx=10)
            pb.set(0.1)  # Initial value
            
            lbl_val = ctk.CTkLabel(row, text="10%", font=("Consolas", 10), text_color=color, width=30)
            lbl_val.pack(side="right")
            
            self.emotion_widgets[key] = {"pb": pb, "lbl": lbl_val}
            
        self.update_emotions_ui()
        
        # Respiración Guiada
        resp_frame = ctk.CTkFrame(self.sidebar, fg_color="#222b31", border_width=1, border_color="#2c353d", corner_radius=10)
        resp_frame.pack(fill="both", expand=True, padx=15, pady=(10, 20))
        
        ctk.CTkLabel(resp_frame, text="🧘 Respiración Guiada", font=("Segoe UI", 13, "bold"), text_color="#d4c4b0").pack(pady=10)
        
        self.resp_canvas = tk.Canvas(resp_frame, bg="#222b31", highlightthickness=0, height=120)
        self.resp_canvas.pack(fill="x", padx=10)
        self.draw_breathing_circle(40)  # Initial circle
        
        self.resp_lbl = ctk.CTkLabel(resp_frame, text="Pulsa Iniciar para calmar tu mente", font=("Segoe UI", 11, "italic"), text_color="#aaaaaa")
        self.resp_lbl.pack(pady=5)
        
        self.btn_resp = ctk.CTkButton(resp_frame, text="Iniciar Respiración", font=("Segoe UI", 11, "bold"), 
                                      fg_color="#7fa99b", text_color="#12161a", hover_color="#638d80",
                                      command=self.toggle_breathing)
        self.btn_resp.pack(pady=10)
        
        self.breathing_active = False
        self.breathing_step = 0
        self.circle_radius = 40
        
        # ─────────────────────────────────────────────────────
        # 2. MAIN CONTENT (Chat Terapéutico y Biblioteca)
        # ─────────────────────────────────────────────────────
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=15, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Top Header Bar
        header = ctk.CTkFrame(self.main_content, fg_color="#1a2126", border_width=1, border_color="#2c353d", corner_radius=10, height=60)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header.grid_rowconfigure(0, weight=1)
        
        ctk.CTkLabel(header, text="Enfoque Clínico:", font=("Segoe UI", 12, "bold"), text_color="#7fa99b").pack(side="left", padx=(15, 5))
        
        self.approach_selector = ctk.CTkOptionMenu(
            header, 
            values=["Terapia Cognitivo-Conductual (TCC)", "Logoterapia (Viktor Frankl)", "Terapia Humanista (Carl Rogers)", "Psicoanálisis (Sigmund Freud)"],
            font=("Segoe UI", 11),
            fg_color="#222b31",
            button_color="#2c353d",
            button_hover_color="#3c4650",
            dropdown_fg_color="#1a2126",
            dropdown_hover_color="#2c353d",
            command=self.change_approach
        )
        self.approach_selector.pack(side="left", padx=5)
        
        self.btn_upload = ctk.CTkButton(header, text="📂 Añadir Libro (PDF/TXT)", font=("Segoe UI", 11, "bold"),
                                        fg_color="#222b31", hover_color="#2c353d", border_width=1, border_color="#2c353d",
                                        command=self.upload_book)
        self.btn_upload.pack(side="right", padx=5)
        
        btn_clear = ctk.CTkButton(header, text="🔄 Nueva Sesión", font=("Segoe UI", 11, "bold"),
                                  fg_color="#e84118", hover_color="#c23616", text_color="#ffffff",
                                  command=self.clear_session)
        btn_clear.pack(side="right", padx=5)

        btn_privacy = ctk.CTkButton(header, text="🛡️ Privacidad", font=("Segoe UI", 11, "bold"),
                                    fg_color="#222b31", hover_color="#2c353d", border_width=1, border_color="#2c353d",
                                    command=self.show_privacy_policy)
        btn_privacy.pack(side="right", padx=5)
        
        btn_apikey = ctk.CTkButton(header, text="🔑 API Key", font=("Segoe UI", 11, "bold"),
                                    fg_color="#222b31", hover_color="#2c353d", border_width=1, border_color="#2c353d",
                                    command=self.change_api_key)
        btn_apikey.pack(side="right", padx=5)

        self.save_profile_var = tk.BooleanVar(value=True)
        self.cb_save_profile = ctk.CTkCheckBox(
            header, text="Guardar perfil", font=("Segoe UI", 11),
            text_color="#aaaaaa", variable=self.save_profile_var,
            fg_color="#7fa99b", hover_color="#638d80", border_color="#2c353d"
        )
        self.cb_save_profile.pack(side="left", padx=10)

        self.tts_active_var = tk.BooleanVar(value=False)
        self.cb_tts_active = ctk.CTkCheckBox(
            header, text="🔊 Voz", font=("Segoe UI", 11),
            text_color="#aaaaaa", variable=self.tts_active_var,
            fg_color="#7fa99b", hover_color="#638d80", border_color="#2c353d",
            command=self.toggle_tts
        )
        self.cb_tts_active.pack(side="left", padx=10)
        
        # Chat Display Window
        self.chat_display = ctk.CTkScrollableFrame(self.main_content, fg_color="#1a2126", border_width=1, border_color="#2c353d", corner_radius=10)
        self.chat_display.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        
        # Bottom area (Bibliographical support card + Input row)
        self.bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="ew")
        
        # Card of Bibliographical Support
        self.citation_card = ctk.CTkFrame(self.bottom_frame, fg_color="#222b31", border_width=1, border_color="#2c353d", corner_radius=8, height=80)
        self.citation_card.pack(fill="x", pady=(0, 10))
        self.citation_card.pack_propagate(False)
        
        self.lbl_citation_title = ctk.CTkLabel(self.citation_card, text="📖 Soporte Científico y Lectura de Sesión:", font=("Segoe UI", 11, "bold"), text_color="#7fa99b")
        self.lbl_citation_title.pack(anchor="w", padx=15, pady=(5, 0))
        
        self.lbl_citation_text = ctk.CTkLabel(self.citation_card, text="Para comenzar la sesión. Aún no se han citado fragmentos de soporte de libros reales.", 
                                              font=("Segoe UI", 11, "italic"), text_color="#aaaaaa", wraplength=500, justify="left")
        self.lbl_citation_text.pack(anchor="w", padx=15, pady=(5, 5))
        
        # Suggested Options Area (Interactive Context Questions with Horizontal Scroll)
        self.options_frame = ctk.CTkScrollableFrame(self.bottom_frame, fg_color="transparent", orientation="horizontal", height=50)
        self.options_frame.pack(fill="x", pady=(5, 10))
        
        # Input Area (Textbox + Send Button)
        input_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        input_frame.pack(fill="x")
        
        self.entry_msg = ctk.CTkEntry(input_frame, placeholder_text="Escribe aquí cómo te sientes o qué pasa por tu mente...", 
                                      font=("Segoe UI", 12), fg_color="#1a2126", border_width=1, border_color="#2c353d", height=45)
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_msg.bind("<Return>", lambda e: self.send_message())
        
        self.btn_send = ctk.CTkButton(input_frame, text="Enviar 🌿", font=("Segoe UI", 12, "bold"),
                                      fg_color="#7fa99b", text_color="#12161a", hover_color="#638d80", width=120, height=45,
                                      command=self.send_message)
        self.btn_send.pack(side="right")
        
        # ─────────────────────────────────────────────────────
        # 3. RIGHT SIDEBAR (Resumen Clínico del Caso)
        # ─────────────────────────────────────────────────────
        self.setup_right_sidebar()
        
    def setup_right_sidebar(self):
        self.right_sidebar = ctk.CTkFrame(self, fg_color="#1a2126", corner_radius=0, border_width=1, border_color="#2c353d")
        self.right_sidebar.grid(row=0, column=2, sticky="nsew")
        
        ctk.CTkLabel(self.right_sidebar, text="📋 Resumen del Caso", font=("Segoe UI", 15, "bold"), text_color="#7fa99b").pack(pady=(20, 10))
        
        self.summary_text = ctk.CTkTextbox(self.right_sidebar, font=("Segoe UI", 11), fg_color="#222b31", border_color="#2c353d", border_width=1)
        self.summary_text.pack(pady=10, padx=15, fill="both", expand=True)
        self.summary_text.configure(state="disabled")
        
        self.btn_export = ctk.CTkButton(self.right_sidebar, text="📥 Exportar Resumen (TXT)", font=("Segoe UI", 11, "bold"),
                                        fg_color="#7fa99b", text_color="#12161a", hover_color="#638d80",
                                        command=self.export_summary)
        self.btn_export.pack(pady=(10, 20), padx=15, fill="x")

    def add_message(self, sender, text):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        bubble_bg = "#222b31" if sender == "assistant" else "#7fa99b"
        text_color = "#e4dcd3" if sender == "assistant" else "#12161a"
        time_color = "#7f8c8d" if sender == "assistant" else "#3c4d47"
        
        row = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)
        
        bubble = ctk.CTkFrame(row, fg_color=bubble_bg, corner_radius=10)
        bubble.pack(side="left" if sender == "assistant" else "right")
        
        lbl_sender = ctk.CTkLabel(bubble, text="PsicoAI Pro" if sender == "assistant" else "Paciente",
                                  font=("Segoe UI", 9, "bold"), text_color="#7fa99b" if sender == "assistant" else "#222b31")
        lbl_sender.pack(anchor="w", padx=12, pady=(8, 2))
        
        lbl_text = ctk.CTkLabel(bubble, text=text, font=("Segoe UI", 12), text_color=text_color, wraplength=420, justify="left")
        lbl_text.pack(anchor="w", padx=12, pady=(2, 2))
        
        lbl_time = ctk.CTkLabel(bubble, text=timestamp, font=("Segoe UI", 8), text_color=time_color)
        lbl_time.pack(anchor="e", padx=12, pady=(0, 6))
        
        self.chat_display._parent_canvas.yview_moveto(1.0)
        
    def change_approach(self, val):
        self.bot.set_approach(val)
        self.add_message("assistant", f"He ajustado el enfoque de nuestra sesión a: {val}. Cuéntame, ¿cómo quieres continuar?")
        self.update_summary_panel()
        
    def send_message(self):
        msg = self.entry_msg.get().strip()
        if not msg:
            return
            
        self.entry_msg.delete(0, "end")
        self.add_message("user", msg)
        
        # Stop any active speaking voice
        self.stop_speaking()
        
        # Disable inputs while AI is thinking
        self.btn_send.configure(state="disabled")
        self.entry_msg.configure(state="disabled")
        
        # Clear suggested options immediately
        self.clear_options_ui()
        
        # Show typing indicator bubble
        self.show_typing_indicator()
        
        # Run AI query in separate thread to prevent GUI freezing
        threading.Thread(target=self.query_ai, args=(msg, self.save_profile_var.get()), daemon=True).start()
        
    def query_ai(self, msg, save_profile):
        try:
            res = self.bot.chat(msg, save_profile=save_profile)
            # Return components to Main thread
            self.after(0, lambda: self.handle_ai_response(res))
        except Exception as e:
            error_res = {
                "respuesta": f"Lo siento, ocurrió un error inesperado al procesar la sesión:\n\n{e}\n\nPor favor, verifica tu conexión o intenta de nuevo.",
                "cita_libro": {},
                "emociones": self.bot.emotions.copy(),
                "opciones_respuesta": ["Quiero intentar de nuevo", "Necesito hablar de otra cosa"]
            }
            self.after(0, lambda: self.handle_ai_response(error_res))
        
    def handle_ai_response(self, res):
        # Hide typing indicator
        self.hide_typing_indicator()
        
        self.btn_send.configure(state="normal")
        self.entry_msg.configure(state="normal")
        
        respuesta = res.get("respuesta", "")
        self.add_message("assistant", respuesta)
        self.update_emotions_ui()
        self.update_citation_ui(res.get("cita_libro", {}))
        
        # Update suggested options in the UI
        self.update_options_ui(res.get("opciones_respuesta", []))
        
        # Update Right Sidebar Summary
        self.update_summary_panel()
        
        # Speak the response if enabled
        self.speak(respuesta)
        
    def show_typing_indicator(self):
        self.hide_typing_indicator()
        
        self.typing_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        self.typing_frame.pack(fill="x", padx=10, pady=5)
        
        bubble = ctk.CTkFrame(self.typing_frame, fg_color="#222b31", corner_radius=10)
        bubble.pack(side="left")
        
        self.typing_label = ctk.CTkLabel(bubble, text="Alejandro está escribiendo.", font=("Segoe UI", 11, "italic"), text_color="#aaaaaa")
        self.typing_label.pack(padx=12, pady=8)
        
        self.chat_display._parent_canvas.yview_moveto(1.0)
        self.animate_typing()
        
    def animate_typing(self):
        if not self.typing_frame:
            return
        try:
            current_text = self.typing_label.cget("text")
            if current_text.endswith("..."):
                next_text = "Alejandro está escribiendo."
            else:
                next_text = current_text + "."
            self.typing_label.configure(text=next_text)
            self.chat_display._parent_canvas.yview_moveto(1.0)
            self.after(500, self.animate_typing)
        except Exception:
            pass
            
    def hide_typing_indicator(self):
        if self.typing_frame:
            try:
                self.typing_frame.destroy()
            except Exception:
                pass
            self.typing_frame = None

    def update_emotions_ui(self):
        for key, w in self.emotion_widgets.items():
            val = self.bot.emotions.get(key, 10)
            normalized = max(0.0, min(1.0, val / 100.0))
            w["pb"].set(normalized)
            w["lbl"].configure(text=f"{val}%")
            
    def update_citation_ui(self, citation):
        if citation and citation.get("libro"):
            title = f"📖 Soporte Científico: {citation.get('libro')} — {citation.get('autor')}"
            text = f'"{citation.get("texto")}"'
            self.lbl_citation_title.configure(text=title, text_color="#7fa99b")
            self.lbl_citation_text.configure(text=text, text_color="#d4c4b0")
        else:
            self.lbl_citation_title.configure(text="📖 Soporte Científico y Lectura de Sesión:", text_color="#aaaaaa")
            self.lbl_citation_text.configure(text="No se ha citado ningún libro en la última respuesta.", text_color="#888888")
            
    def update_summary_panel(self):
        if not hasattr(self, "summary_text") or not self.summary_text:
            return
        
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        
        profile = self.bot.profile
        
        summary_lines = []
        summary_lines.append("=========================================")
        summary_lines.append("         PSICOAI PRO - RESUMEN CLÍNICO")
        summary_lines.append("=========================================\n")
        summary_lines.append(f"Enfoque actual: {self.bot.approach}\n")
        
        summary_lines.append("🔍 TEMAS RECURRENTES:")
        if profile.temas_recurrentes:
            for t in profile.temas_recurrentes:
                summary_lines.append(f"  • {t}")
        else:
            summary_lines.append("  (Ninguno detectado aún)")
        summary_lines.append("")
        
        summary_lines.append("🧠 PATRONES CONDUCTUALES / COGNITIVOS:")
        if profile.patrones_identificados:
            for p in profile.patrones_identificados:
                summary_lines.append(f"  • {p}")
        else:
            summary_lines.append("  (Ninguno detectado aún)")
        summary_lines.append("")
        
        summary_lines.append("💪 RECURSOS Y FORTALEZAS:")
        if profile.recursos_personales:
            for r in profile.recursos_personales:
                summary_lines.append(f"  • {r}")
        else:
            summary_lines.append("  (Ninguno detectado aún)")
        summary_lines.append("")
        
        summary_lines.append("👥 VÍNCULOS IMPORTANTES:")
        if profile.vinculos_importantes:
            for v in profile.vinculos_importantes:
                summary_lines.append(f"  • {v}")
        else:
            summary_lines.append("  (Ninguno detectado aún)")
        summary_lines.append("")
        
        summary_lines.append("📝 HISTORIAL DE NOTAS CLÍNICAS:")
        if profile.notas_sesion:
            for idx, nota in enumerate(profile.notas_sesion, 1):
                summary_lines.append(f"  [{idx}] {nota}")
        else:
            summary_lines.append("  (Sin notas en esta sesión)")
            
        text_content = "\n".join(summary_lines)
        self.summary_text.insert("1.0", text_content)
        self.summary_text.configure(state="disabled")

    def export_summary(self):
        self.summary_text.configure(state="normal")
        content = self.summary_text.get("1.0", "end-1c")
        self.summary_text.configure(state="disabled")
        
        if not content.strip() or ("Sin notas" in content and "Ninguno" in content):
            messagebox.showwarning("Exportar", "No hay datos clínicos acumulados para exportar en esta sesión.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivo de Texto", "*.txt")],
            title="Exportar Resumen Clínico",
            initialfile="Resumen_Clinico_PsicoAI.txt"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Éxito", "El resumen clínico ha sido exportado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n\n{e}")

    def clear_session(self):
        if messagebox.askyesno("Nueva Sesión", "¿Seguro que quieres reiniciar la sesión? Se borrará el historial de conversación temporal."):
            self.stop_speaking()
            self.bot.clear_session()
            for w in self.chat_display.winfo_children():
                w.destroy()
            self.update_emotions_ui()
            self.update_citation_ui({})
            self.update_summary_panel()
            self.add_message("assistant", "Sesión reiniciada. Estoy listo para escucharte. ¿De qué te gustaría hablar hoy?")
            self.update_options_ui(["Me siento ansioso/a", "Tengo problemas para dormir", "Quiero hablar de una relación", "No sé por dónde empezar"])
            
    def upload_book(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos de Lectura", "*.txt *.pdf")])
        if not path:
            return
            
        # Disable button and update text for visual feedback
        self.btn_upload.configure(state="disabled", text="📂 Indexando...")
        
        # Run copying and indexing in a separate thread to prevent blocking
        threading.Thread(target=self.bg_upload_book, args=(path,), daemon=True).start()

    def bg_upload_book(self, path):
        target_dir = self.bot.db.books_dir
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        fname = os.path.basename(path)
        dest_path = os.path.join(target_dir, fname)
        
        success = False
        error_msg = ""
        try:
            shutil.copy(path, dest_path)
            self.bot.db.load_all_books()
            success = True
        except Exception as e:
            error_msg = str(e)
            
        self.after(0, lambda: self.after_upload_book(success, fname, error_msg))

    def after_upload_book(self, success, fname, error_msg):
        self.btn_upload.configure(state="normal", text="📂 Añadir Libro (PDF/TXT)")
        if success:
            messagebox.showinfo("Éxito", f"Libro '{fname}' cargado e indexado correctamente en la biblioteca.")
        else:
            messagebox.showerror("Error", f"No se pudo copiar o indexar el archivo:\n\n{error_msg}")
            
    def check_consent(self):
        settings_path = get_settings_path()
        consent_granted = False
        api_key = ""
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    consent_granted = data.get("consent_granted", False)
                    api_key = data.get("api_key", "")
            except Exception:
                pass
                
        # If there's no API key in settings, use the default hardcoded one
        if not api_key:
            api_key = DEFAULT_API_KEY
            
        if not consent_granted:
            self.consent_frame = ConsentFrame(self, on_accept=self.accept_consent, on_decline=self.decline_consent)
            self.consent_frame.pack(fill="both", expand=True)
        else:
            self.bot.api_key = api_key
            self.show_main_ui()
 
    def accept_consent(self):
        settings_path = get_settings_path()
        api_key = DEFAULT_API_KEY
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump({"consent_granted": True, "api_key": api_key}, f)
        except Exception as e:
            print(f"Error guardando consentimiento: {e}")
        
        self.bot.api_key = api_key
        self.consent_frame.pack_forget()
        self.consent_frame.destroy()
        self.show_main_ui()
        
    def decline_consent(self):
        self.stop_speaking()
        self.destroy()

    def show_main_ui(self):
        self.setup_ui()
        self.add_message("assistant", "Hola, bienvenido a PsicoAI Pro. Estoy aquí para escucharte y acompañarte hoy en tu proceso de manera psicoeducativa y emocional. ¿Qué te gustaría compartir conmigo en esta sesión?")
        self.update_options_ui(["Me siento ansioso/a", "Tengo problemas para dormir", "Quiero hablar de una relación", "No sé por dónde empezar"])
        self.update_summary_panel()

    def change_api_key(self):
        ApiKeyDialog(self, self.bot.api_key, self.save_api_key)
        
    def save_api_key(self, new_key):
        self.bot.api_key = new_key
        settings_path = get_settings_path()
        try:
            settings = {"consent_granted": True}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)
            settings["api_key"] = new_key
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f)
            messagebox.showinfo("Éxito", "Clave de API guardada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la clave de API:\n\n{e}")

    def update_options_ui(self, options):
        self.clear_options_ui()
        if not options:
            return
            
        for opt in options:
            btn = ctk.CTkButton(
                self.options_frame,
                text=opt,
                font=("Segoe UI", 11),
                fg_color="#222b31",
                text_color="#7fa99b",
                hover_color="#2c353d",
                border_width=1,
                border_color="#7fa99b",
                corner_radius=15,
                height=30,
                command=lambda val=opt: self.select_option(val)
            )
            btn.pack(side="left", padx=5, pady=2)
            
    def clear_options_ui(self):
        for w in self.options_frame.winfo_children():
            w.destroy()
            
    def select_option(self, val):
        self.clear_options_ui()
        self.add_message("user", val)
        self.btn_send.configure(state="disabled")
        self.entry_msg.configure(state="disabled")
        self.show_typing_indicator()
        threading.Thread(target=self.query_ai, args=(val, self.save_profile_var.get()), daemon=True).start()

    def show_privacy_policy(self):
        PrivacyDialog(self)
            
    # ─────────────────────────────────────────────────────
    # ANIMACION CANVA DE RESPIRACION GUIADA (INTERACTIVA)
    # ─────────────────────────────────────────────────────
    def draw_breathing_circle(self, radius):
        self.resp_canvas.delete("circle")
        cx = 120
        cy = 60
        self.resp_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, 
                                     fill="", outline="#7fa99b", width=3, tags="circle")
        
    def toggle_breathing(self):
        if self.breathing_active:
            self.breathing_active = False
            self.btn_resp.configure(text="Iniciar Respiración", fg_color="#7fa99b", text_color="#12161a")
            self.resp_lbl.configure(text="Pulsa Iniciar para calmar tu mente", text_color="#aaaaaa")
            self.circle_radius = 40
            self.draw_breathing_circle(40)
        else:
            self.breathing_active = True
            self.btn_resp.configure(text="Detener", fg_color="#e84118", text_color="#ffffff")
            self.breathing_step = 0
            self.run_breathing_cycle()
            
    def run_breathing_cycle(self):
        if not self.breathing_active:
            return
            
        stage = self.breathing_step // 40
        step_in_stage = self.breathing_step % 40
        
        if stage == 0:
            self.resp_lbl.configure(text="💨 INHALA profundamente...", text_color="#7fa99b")
            self.circle_radius = 30 + int(50 * (step_in_stage / 40.0))
        elif stage == 1:
            self.resp_lbl.configure(text="🛑 MANTÉN el aire...", text_color="#e1b12c")
            self.circle_radius = 80 + int(3 * (1 if step_in_stage % 10 < 5 else -1))
        elif stage == 2:
            self.resp_lbl.configure(text="🌬️ EXHALA despacio...", text_color="#00a8ff")
            self.circle_radius = 80 - int(50 * (step_in_stage / 40.0))
        elif stage == 3:
            self.resp_lbl.configure(text="🛑 MANTÉN vacío...", text_color="#e84118")
            self.circle_radius = 30
            
        self.draw_breathing_circle(self.circle_radius)
        self.breathing_step = (self.breathing_step + 1) % 160
        self.after(100, self.run_breathing_cycle)

    # ─────────────────────────────────────────────────────
    # TEXT TO SPEECH (edge-tts + MCI winmm.dll)
    # ─────────────────────────────────────────────────────
    def toggle_tts(self):
        if not self.tts_active_var.get():
            self.stop_speaking()

    def speak(self, text):
        if not self.tts_active_var.get():
            return
        self.stop_speaking()
        threading.Thread(target=self.bg_speak, args=(text,), daemon=True).start()

    def bg_speak(self, text):
        try:
            # Clean up text for speech
            clean = re.sub(r"[\*\#\_\-\`]", "", text)
            clean = clean.replace('"', '""').replace('\n', ' ')
            
            temp_dir = tempfile.gettempdir()
            filename = f"psicoai_speak_{uuid.uuid4().hex[:8]}.mp3"
            self.current_temp_audio = os.path.join(temp_dir, filename)
            
            # Select es-MX-JorgeNeural (Alejandro)
            voice = "es-MX-JorgeNeural"
            
            async def generate_speech():
                communicate = edge_tts.Communicate(clean, voice)
                await communicate.save(self.current_temp_audio)
                
            asyncio.run(generate_speech())
            
            # Play using MCI
            winmm = ctypes.windll.winmm
            winmm.mciSendStringW("close psicoai_voice", None, 0, 0)
            
            open_cmd = f'open "{self.current_temp_audio}" type mpegvideo alias psicoai_voice'
            res = winmm.mciSendStringW(open_cmd, None, 0, 0)
            if res == 0:
                winmm.mciSendStringW("play psicoai_voice", None, 0, 0)
            else:
                print(f"Error opening audio via MCI: {res}")
        except Exception as e:
            print(f"Error in edge-tts: {e}")

    def stop_speaking(self):
        try:
            winmm = ctypes.windll.winmm
            winmm.mciSendStringW("stop psicoai_voice", None, 0, 0)
            winmm.mciSendStringW("close psicoai_voice", None, 0, 0)
            
            if self.current_temp_audio and os.path.exists(self.current_temp_audio):
                try:
                    os.remove(self.current_temp_audio)
                except Exception:
                    pass
                self.current_temp_audio = None
        except Exception as e:
            print(f"Error stopping audio: {e}")

    def cleanup_temp_files(self):
        try:
            import glob
            temp_dir = tempfile.gettempdir()
            for path in glob.glob(os.path.join(temp_dir, "psicoai_speak_*")):
                try:
                    os.remove(path)
                except Exception:
                    pass
        except Exception:
            pass

    def destroy(self):
        self.stop_speaking()
        self.cleanup_temp_files()
        super().destroy()
 
if __name__ == "__main__":
    app = App()
    app.mainloop()