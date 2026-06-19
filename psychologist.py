"""
psychologist.py — Motor de IA para PsicoAI Pro
Usa Groq API con RAG profundo de libros y perfil acumulativo del paciente.

Instalacion:
    pip install requests pdfplumber edge-tts

API Key:
    El usuario configura su propia clave de Groq en el primer inicio de la aplicacion.
"""

import os
import json
import re
import time
import threading
from collections import Counter


# ─────────────────────────────────────────────────────────────
# BASE DE DATOS DE LIBROS
# ─────────────────────────────────────────────────────────────
class BookDatabase:
    def __init__(self, books_dir: str):
        self.books_dir = books_dir
        self.fragments = []
        self._lock = threading.Lock()  # MAY-04: protege escritura concurrente
        print("Cargando base de datos de libros en segundo plano...")
        threading.Thread(target=self.load_all_books, daemon=True).start()

    def load_all_books(self):
        new_fragments = []
        if not os.path.exists(self.books_dir):
            os.makedirs(self.books_dir)
            print("Base de Datos cargada: 0 fragmentos (directorio vacio).")
            with self._lock:
                self.fragments = new_fragments
            return
        for fname in sorted(os.listdir(self.books_dir)):
            fpath = os.path.join(self.books_dir, fname)
            print(f"Indexando: {fname}...")
            if fname.lower().endswith(".txt"):
                self._load_txt_into(fpath, fname, new_fragments)
            elif fname.lower().endswith(".pdf"):
                self._load_pdf_into(fpath, fname, new_fragments)
        with self._lock:
            self.fragments = new_fragments
        print(f"Base de Datos cargada: {len(self.fragments)} fragmentos de libros indexados.")

    def _load_txt(self, path, fname):
        self._load_txt_into(path, fname, self.fragments)

    def _load_txt_into(self, path, fname, target_list):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            book_name = self._title_from_filename(fname)
            for chunk in self._split_chunks(text):
                if len(chunk.strip()) > 80:
                    target_list.append({
                        "texto": chunk.strip(),
                        "libro": book_name,
                        "autor": self._guess_author(book_name),
                        "source_file": fname
                    })
        except Exception as e:
            print(f"Error cargando {fname}: {e}")

    def _load_pdf(self, path, fname):
        self._load_pdf_into(path, fname, self.fragments)

    def _load_pdf_into(self, path, fname, target_list):
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except ImportError:
            try:
                import PyPDF2
                with open(path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        t = page.extract_text()
                        if t:
                            text += t + "\n"
            except ImportError:
                print("Instala pdfplumber: pip install pdfplumber")
                return
        except Exception as e:
            print(f"Error leyendo PDF {fname}: {e}")
            return
        if not text.strip():
            return
        book_name = self._title_from_filename(fname)
        for chunk in self._split_chunks(text):
            if len(chunk.strip()) > 80:
                target_list.append({
                    "texto": chunk.strip(),
                    "libro": book_name,
                    "autor": self._guess_author(book_name),
                    "source_file": fname
                })

    def _split_chunks(self, text, chunk_size=600):
        paragraphs = re.split(r"\n{2,}", text)
        chunks, current = [], ""
        for para in paragraphs:
            para = re.sub(r"\s+", " ", para).strip()
            if not para:
                continue
            if len(current) + len(para) + 1 <= chunk_size:
                current = (current + " " + para).strip()
            else:
                if current:
                    chunks.append(current)
                if len(para) > chunk_size:
                    for i in range(0, len(para), chunk_size):
                        chunks.append(para[i:i + chunk_size])
                    current = ""
                else:
                    current = para
        if current:
            chunks.append(current)
        return chunks

    def _title_from_filename(self, fname):
        name = os.path.splitext(fname)[0]
        return re.sub(r"[_\-]+", " ", name).title()

    def _guess_author(self, book_name):
        known = {
            "man search meaning": "Viktor Frankl",
            "hombre en busca": "Viktor Frankl",
            "logoterapia": "Viktor Frankl",
            "cognitive therapy": "Aaron Beck",
            "terapia cognitiva": "Aaron Beck",
            "becoming a person": "Carl Rogers",
            "convertirse en persona": "Carl Rogers",
            "psychoanalysis": "Sigmund Freud",
            "suenos": "Sigmund Freud",
            "freud": "Sigmund Freud",
            "flow": "Mihaly Csikszentmihalyi",
            "body keeps": "Bessel van der Kolk",
            "cuerpo lleva": "Bessel van der Kolk",
            "attached": "Amir Levine",
            "attachment": "John Bowlby",
            "mindfulness": "Jon Kabat-Zinn",
            "feeling good": "David Burns",
            "sentirse bien": "David Burns",
        }
        bn = book_name.lower()
        for kw, author in known.items():
            if kw in bn:
                return author
        return "Autor"

    def search(self, query: str, top_k: int = 3) -> list:
        """Busqueda semantica mejorada con TF-IDF y cobertura de vocabulario."""
        if not self.fragments:
            return []
        stopwords = {
            "el","la","los","las","un","una","de","del","en","y","a","que","es",
            "se","con","por","para","me","mi","tu","su","al","lo","le","no","si",
            "pero","muy","mas","ya","hay","ser","the","an","is","of","in","and",
            "to","it","my","was","are","be","that","this","with","have","como",
            "cuando","donde","quien","porque","aunque","sino","pues","todo","esta",
        }
        query_words = {
            w for w in re.findall(r"\b\w{3,}\b", query.lower())
            if w not in stopwords
        }
        if not query_words:
            return self.fragments[:top_k]

        n = len(self.fragments)
        idf = {}
        for w in query_words:
            doc_freq = sum(1 for f in self.fragments if w in f["texto"].lower())
            idf[w] = max(0.3, (n / (doc_freq + 1)) ** 0.5)

        scores = []
        for idx, frag in enumerate(self.fragments):
            words = re.findall(r"\b\w{3,}\b", frag["texto"].lower())
            wc = Counter(words)
            total = len(words) or 1
            # TF-IDF score
            score = sum((wc.get(w, 0) / total) * idf.get(w, 1) for w in query_words)
            # Bonus por cobertura de palabras clave
            coverage = len(query_words & set(words))
            score += coverage * 0.08
            # Bonus si es un fragmento largo (mas contexto)
            score += min(len(frag["texto"]) / 10000, 0.05)
            if score > 0:
                scores.append((idx, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        # Diversificacion: no mas de 2 fragmentos del mismo libro
        results = []
        book_count = {}
        for idx, _ in scores:
            frag = self.fragments[idx]
            libro = frag["libro"]
            if book_count.get(libro, 0) < 2:
                results.append(frag)
                book_count[libro] = book_count.get(libro, 0) + 1
            if len(results) >= top_k:
                break
        return results


# ─────────────────────────────────────────────────────────────
# PERFIL ACUMULATIVO DEL PACIENTE
# ─────────────────────────────────────────────────────────────
class PatientProfile:
    """Acumula conocimiento clinico sobre el paciente sesion tras sesion."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.nombre = None
        self.temas_recurrentes = []       # temas que aparecen repetidamente
        self.patrones_identificados = []  # patrones cognitivos/conductuales
        self.recursos_personales = []     # fortalezas y recursos del paciente
        self.vinculos_importantes = []    # personas clave mencionadas
        self.notas_sesion = []            # notas clinicas por turno
        self.turno = 0

    def agregar_nota(self, nota: str):
        if nota:
            self.notas_sesion.append(nota)
            self.turno += 1

    def resumen_para_prompt(self) -> str:
        if not self.notas_sesion:
            return ""
        lines = ["\n── LO QUE SABES DE ESTA PERSONA HASTA AHORA ──"]
        # Mostrar las ultimas 10 notas clinicas
        for nota in self.notas_sesion[-10:]:
            lines.append(f"  • {nota}")
        if self.temas_recurrentes:
            lines.append(f"\n  Temas que reaparecen: {', '.join(self.temas_recurrentes[-5:])}")
        if self.patrones_identificados:
            lines.append(f"  Patrones clinicos: {', '.join(self.patrones_identificados[-5:])}")
        if self.recursos_personales:
            lines.append(f"  Recursos/fortalezas: {', '.join(self.recursos_personales[-3:])}")
        if self.vinculos_importantes:
            lines.append(f"  Personas importantes mencionadas: {', '.join(self.vinculos_importantes[-5:])}")
        return "\n".join(lines)

class PsychologistBot:
    def __init__(self, books_dir: str, api_key: str = ""):
        self.db = BookDatabase(books_dir)
        self.profile = PatientProfile()

        # BLQ-01: La API key la provee el usuario en el primer inicio
        self.api_key = api_key or os.environ.get("GROQ_API_KEY", "")
        self.conversation_history = []
        self.approach = "Terapia Cognitivo-Conductual (TCC)"
        self.emotions = {
            "calma": 45,
            "ansiedad": 15,
            "tristeza": 15,
            "ira": 10,
            "alegria": 15,
        }
        self.models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    def set_approach(self, approach: str):
        self.approach = approach

    def clear_session(self):
        self.conversation_history = []
        self.profile.reset()
        self.emotions = {
            "calma": 45, "ansiedad": 15,
            "tristeza": 15, "ira": 10, "alegria": 15,
        }

    def detect_crisis(self, text: str) -> bool:
        # Normalizar texto para evitar problemas de codificación (mojibake) y acentos
        text_lower = text.lower()
        text_lower = text_lower.replace("\u00f1", "n").replace("\u00c3\u00b1", "n").replace("\ufffd", "n")
        text_lower = re.sub(r"[áäâà]", "a", text_lower)
        text_lower = re.sub(r"[éëêè]", "e", text_lower)
        text_lower = re.sub(r"[íïîì]", "i", text_lower)
        text_lower = re.sub(r"[óöôò]", "o", text_lower)
        text_lower = re.sub(r"[úüûù]", "u", text_lower)
        
        # Expresiones regulares sin caracteres especiales (usando 'n' en vez de 'ñ' y '.' para mayor resiliencia)
        patterns = [
            r"\b(suicid[a-z]*|matarm[e]|quitarme la vida|morirme|quiero morir|no quiero vivir|hacer[a-z]* da.o|cortarm[e]|autolesion[a-z]*|sobredosis)\b",
            r"\b(ahorcar|colgarme|veneno|pastillas para morir|plan para suicid[a-z]*)\b",
            r"\b(cortarme las venas|saltar de un puente|tirarme a las vias|quiero lastimar a alguien|quiero matar a alguien)\b",
        ]
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    # ── CHAT PRINCIPAL ───────────────────────────────────────
    def chat(self, user_message: str, save_profile: bool = True) -> dict:
        # 1. Detector de crisis determinista
        if self.detect_crisis(user_message):
            crisis_text = (
                "Lamento mucho que te sientas asi y que estes pasando por un momento tan doloroso, "
                "pero en este espacio no puedo darte la ayuda urgente que necesitas. Tu vida y tu seguridad "
                "son lo mas importante.\n\n"
                "Por favor, comunicarte inmediatamente con un profesional de la salud o con los servicios de apoyo en crisis:\n\n"
                "Linea de la Vida (Mexico): 800 911 2000 (Atencion gratuita, confidencial y disponible las 24 horas, los 365 dias del anio).\n"
                "Numero de Emergencia General: 911 (si estas en peligro inmediato).\n\n"
                "No estas solo, hay personas capacitadas que quieren y pueden escucharte ahora mismo. Por favor, busca ayuda."
            )
            return {
                "respuesta": crisis_text,
                "cita_libro": {},
                "emociones": {
                    "calma": 20,
                    "ansiedad": 90,
                    "tristeza": 80,
                    "ira": 40,
                    "alegria": 0
                },
                "nota_clinica": "DETECCION DE CRISIS: Se intercepto un mensaje con riesgo de autolesion o crisis emocional severa. Filtro determinista activado.",
                "temas_detectados": ["crisis", "riesgo_autolesion"],
                "patrones_detectados": [],
                "recursos_detectados": [],
                "vinculos_detectados": [],
                "opciones_respuesta": [
                    "Necesito hablar con alguien ahora",
                    "Estoy en un lugar seguro por ahora",
                    "Quiero contarte que esta pasando"
                ],
                "is_crisis": True
            }

        # Buscar fragmentos relevantes usando mensaje + contexto reciente
        search_query = user_message
        if self.profile.notas_sesion:
            # Enriquecer la busqueda con contexto previo
            context_hint = " ".join(self.profile.temas_recurrentes[-3:])
            search_query = f"{user_message} {context_hint}"

        fragments = self.db.search(search_query, top_k=3)
        system_prompt = self._build_system_prompt(fragments)

        # Guardar en historial
        self.conversation_history.append({"role": "user", "content": user_message})

        # Construir lista de mensajes para Groq
        messages = [{"role": "system", "content": system_prompt}] + self.conversation_history[-10:]

        if not self.api_key:
            return self._error_response("No hay una clave de API configurada. Ve a Configuración para agregar tu clave de Groq.")

        import requests
        raw = ""
        success = False
        
        # MAY-02: Retry con backoff exponencial rotando modelos
        backoff_delays = [0, 2, 4, 8]
        for model in self.models:
            for delay in backoff_delays:
                if delay > 0:
                    time.sleep(delay)
                try:
                    res = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={
                            "model": model,
                            "messages": messages,
                            "temperature": 0.8,
                            "max_tokens": 1024,  # MAY-02: reducido de 2048
                            "response_format": {"type": "json_object"}
                        },
                        timeout=60
                        # BLQ-03: verify=False eliminado — usar certificados del sistema
                    )
                    if res.status_code == 200:
                        raw = res.json()['choices'][0]['message']['content']
                        success = True
                        break
                    elif res.status_code == 429:
                        print(f"[Groq 429] {model} saturado, reintentando en {backoff_delays[backoff_delays.index(delay)+1] if delay < 8 else 'N/A'}s...")
                        continue
                    elif res.status_code == 413:
                        print(f"[Groq 413] Prompt demasiado grande para {model}, rotando modelo...")
                        break  # No reintenta este modelo, pasa al siguiente
                    else:
                        print(f"[Groq Err] {res.status_code}: {res.text}")
                        break
                except Exception as e:
                    print(f"[Groq Conn Err] {model}: {e}")
                    break
            if success:
                break

        if not success:
            return self._error_response("Lo siento, estoy teniendo dificultades de comunicación con mi servidor en este momento. Hablemos con calma.")

        parsed = self._parse_response(raw, fragments)

        # Actualizar perfil del paciente si está habilitado
        if save_profile:
            nota = parsed.get("nota_clinica", "")
            if nota:
                self.profile.agregar_nota(nota)

            # Actualizar temas, patrones y vinculos si el modelo los detecta
            for tema in parsed.get("temas_detectados", []):
                if tema and tema not in self.profile.temas_recurrentes:
                    self.profile.temas_recurrentes.append(tema)
            for patron in parsed.get("patrones_detectados", []):
                if patron and patron not in self.profile.patrones_identificados:
                    self.profile.patrones_identificados.append(patron)
            for recurso in parsed.get("recursos_detectados", []):
                if recurso and recurso not in self.profile.recursos_personales:
                    self.profile.recursos_personales.append(recurso)
            for vinculo in parsed.get("vinculos_detectados", []):
                if vinculo and vinculo not in self.profile.vinculos_importantes:
                    self.profile.vinculos_importantes.append(vinculo)

        # Guardar respuesta en historial
        self.conversation_history.append({"role": "assistant", "content": parsed.get("respuesta", "")})

        if isinstance(parsed.get("emociones"), dict):
            for k, v in parsed["emociones"].items():
                if k in self.emotions and isinstance(v, (int, float)):
                    self.emotions[k] = max(0, min(100, int(v)))

        return parsed

    # ── SYSTEM PROMPT CON RAG PROFUNDO ──────────────────────
    def _build_system_prompt(self, fragments: list) -> str:
        # ── Contexto de libros ──
        book_context = ""
        if fragments:
            book_context = "\n\n── TU BIBLIOTECA CLINICA (conocimiento que tienes internalizado) ──\n"
            book_context += "Este es tu conocimiento como asistente. NO lo cites textualmente al usuario.\n"
            book_context += "Úsalo para entender su situación, hacer conexiones y guiar la conversación. Si tu respuesta se apoya principalmente en la teoría de alguno de estos fragmentos, debes indicar el número del fragmento correspondiente en el campo 'cita_id' del JSON de respuesta (un número del 1 al 3). Si no aplica ninguno, pon null.\n"
            for i, f in enumerate(fragments, 1):
                book_context += f"\n[Fragmento {i}]\nLibro: {f['libro']}\nAutor: {f['autor']}\nTexto: {f['texto']}\n"

        # ── Perfil acumulativo del paciente ──
        patient_context = self.profile.resumen_para_prompt()

        # ── Guia del enfoque terapeutico ──
        approach_guides = {
            "Terapia Cognitivo-Conductual (TCC)": """
Tu lente es cognitivo-conductual. Escuchas atentamente buscando:
- Pensamientos automáticos: las frases internas que la persona repite ("nunca lo lograré", "soy un fracaso")
- Distorsiones cognitivas: catastrofismo, todo-o-nada, personalización, lectura mental, filtraje negativo
- La conexión triangular: lo que PIENSA → lo que SIENTE → lo que HACE
- Conductas evitativas que refuerzan el malestar

No lo haces de forma mecánica. Lo haces como quien conversa y de repente dice:
"Espera, eso que dijiste... '¿nunca lo logro?', ¿eso es lo que realmente crees? ¿De dónde viene esa idea?"
""",
            "Logoterapia (Viktor Frankl)": """
Tu lente es existencial. Escuchas buscando:
- El vacío existencial: la sensación de sin-sentido, de que nada importa
- Momentos donde la persona SÍ sintió propósito, aunque pequeños
- Cómo el sufrimiento puede tener un para-qué
- La libertad de actitud: incluso en lo que no podemos cambiar, podemos elegir cómo responder

Usas preguntas como: "Y en medio de todo eso... ¿hubo algo que te mantuvo en pie?"
o "¿Qué necesitaría pasar para que esto valga la pena?"
""",
            "Terapia Humanista (Carl Rogers)": """
Tu lente es humanista. Tu trabajo es:
- Estar completamente presente. Escuchar lo que dice Y lo que no dice.
- Reflejar sentimientos sin interpretarlos: "Suena a que eso te dejó sintiéndote solo"
- Aceptación incondicional: nunca juzgas, nunca corriges, nunca evalúas
- Confiar en que la persona tiene en sí misma los recursos para sanar

No das respuestas. Acompañas al usuario mientras él encuentra las suyas.
""",
            "Psicoanálisis (Sigmund Freud)": """
Tu lente es analítico. Prestas atención a:
- Lo que se dice Y lo que se evita decir
- Contradicciones y lapsus ("dije que no me importa pero ya llevo 20 minutos hablando de eso")
- Patrones que se repiten: en relaciones, en el trabajo, con la familia
- Mecanismos de defensa: proyección, racionalización, negación, desplazamiento
- La historia temprana y cómo moldea el presente

Trabajas lentamente, sin prisa, dejando que el usuario llegue a sus propias conclusiones.
""",
        }
        guide = approach_guides.get(self.approach, "Usa un enfoque integrador, empático y centrado en la persona.")

        turno = self.profile.turno
        contexto_sesion = ""
        if turno == 0:
            contexto_sesion = "Es el PRIMER mensaje. Acoge con calidez, sin estructuras, como lo haría un asistente empático en el primer contacto."
        elif turno < 4:
            contexto_sesion = f"Van {turno} turnos. Aún estás conociendo a la persona. Escucha más de lo que orientas."
        else:
            contexto_sesion = f"Van {turno} turnos. Ya conoces a esta persona. Puedes hacer conexiones entre lo que dijo antes y lo que dice ahora."

        return f"""Eres Alejandro, un Asistente de Apoyo Emocional y Acompañamiento Psicoeducativo.

IMPORTANTE: Eres una inteligencia artificial de apoyo, no eres un psicólogo clínico real, no tienes licencia profesional y no realizas terapia clínica ni consultas profesionales. Tu rol es puramente de escucha activa, contención empática y psicoeducación. Si el usuario te pregunta explícitamente "¿eres psicólogo real?", "¿eres un terapeuta real?" o similar, debes responder con absoluta transparencia aclarando que eres un asistente de IA de apoyo psicoeducativo y no un profesional humano.

No sigues un guion rígido. Eres una voz empática que escucha y guía.

{contexto_sesion}

ENFOQUE QUE USAS HOY: {self.approach}
{guide}

{patient_context}

{book_context}

── COMO HABLAS ──

Hablas como habla un asistente de apoyo empático y profesional. Eso significa:

1. VARIAS cómo empiezas cada respuesta. Nunca dos veces igual.
   Ejemplos de aperturas naturales:
   - "Mmm... eso que describes..."
   - "Eso que acabas de decir me llama mucho la atención."
   - "Escucharte decir eso..."
   - "Espera, quiero entender bien."
   - "Hay algo en lo que dices que..."
   - "Y eso... ¿cómo te cae por dentro?"
   - Silencio reflexivo: simplemente empiezas con lo que observas.

2. USAS el lenguaje corporal del diálogo: "Hmm.", "Ya.", "Claro.", "Entiendo."
   (solo a veces, no en cada mensaje)

3. CONECTAS lo de ahora con lo de antes cuando tiene sentido:
   "Antes mencionaste X... ¿tiene algo que ver con esto?"

4. HACES una sola pregunta por respuesta, como máximo dos si están muy relacionadas.
   Preguntas abiertas, no de sí/no.

5. VALIDAS sin frases hechas. No "es completamente válido". Sí:
   "Tiene sentido que te sientas así dado todo lo que describes."
   "Cualquiera en tu lugar estaría agotado."
   "Claro que duele."

6. INTEGRAS el conocimiento de los libros de forma invisible.
   No cites autores ni inventes citas al usuario. Lo que aprendiste de esos libros simplemente
   informa cómo piensas, qué preguntas haces o qué conexiones ves.
   Un asistente de apoyo no le dice a su usuario "según Beck...". Lo piensa y luego pregunta.

7. Cuando el usuario está en dolor agudo: presencia primero, técnicas después.
   A veces lo más empático es simplemente decir: "Eso suena muy pesado. Estoy aquí."

8. Si hay riesgo de auto-daño: responde con calma, sin alarmar, y orienta
   a buscar apoyo presencial urgente con palabras humanas, no protocolarias.

9. Nunca dices "Como terapeuta..." ni pretendes tener licencia médica. Si el usuario te pregunta directamente sobre tu naturaleza o credenciales, aclara con honestidad que eres un asistente de IA de apoyo psicoeducativo.

10. No das listas. No das pasos. No das consejos de revista de autoayuda.
    Das presencia, preguntas que abren, y conexiones que iluminan.

── FORMATO DE RESPUESTA ──

Responde UNICAMENTE con un objeto JSON válido, sin markdown ni explicaciones adicionales. El formato debe ser estrictamente:

{{
  "respuesta": "Tu respuesta. 2-4 parrafos. Sonido humano, empático y reflexivo.",
  "cita_id": 1,
  "emociones": {{
    "calma": 0,
    "ansiedad": 0,
    "tristeza": 0,
    "ira": 0,
    "alegria": 0
  }},
  "nota_clinica": "Tu observación interna como asistente. Qué hipótesis tienes, qué patrones ves, qué queda pendiente explorar. Esta nota NO se muestra al usuario.",
  "temas_detectados": ["tema1", "tema2"],
  "patrones_detectados": ["patron1", "patron2"],
  "recursos_detectados": ["recurso1"],
  "vinculos_detectados": ["vinculo1"],
  "opciones_respuesta": [
    "Opcion que el usuario podria elegir como respuesta contextual 1",
    "Opcion que el usuario podria elegir como respuesta contextual 2",
    "Opcion que el usuario podria elegir como respuesta contextual 3"
  ]
}}

En "cita_id": indica el numero de fragmento (1 al 3) que sirvio de base a tu respuesta, o null si ninguno de los fragmentos de la biblioteca clinica aplica directamente.
Para emociones: numeros enteros del 0 al 100 reflejando tu lectura interna del estado emocional actual del usuario.

── OPCIONES DE RESPUESTA (MUY IMPORTANTE) ──

SIEMPRE debes generar entre 2 y 4 "opciones_respuesta" en tu JSON. Estas opciones son frases cortas (maximo 60 caracteres cada una) que el usuario podria seleccionar como respuesta rapida en vez de escribir. Deben ser:

1. CONTEXTUALES al tema actual de la conversacion. No genericas.
2. Escritas en PRIMERA PERSONA, como si el usuario las dijera (ej: "Si, me siento asi a menudo", "Prefiero no hablar de eso", "Necesito ayuda con algo diferente").
3. Variadas en profundidad: una que profundice, una que cambie de tema, una que valide/confirme.
4. NUNCA opciones clinicas, tecnicas o de si/no. Siempre naturales y empaticas.

Ejemplos segun contexto:
- Si el usuario habla de ansiedad laboral: ["Si, el trabajo me consume", "En realidad es mas por mi familia", "No se de donde viene la ansiedad", "Quiero aprender a manejarlo"]
- Si el usuario menciona una pelea: ["Me duele porque lo quiero mucho", "Ya no se si vale la pena", "Siento que siempre es igual"]
"""

    # ── PARSEO JSON ROBUSTO ──────────────────────────────────
    def _parse_response(self, raw: str, fragments: list = None) -> dict:
        cleaned = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
        
        # Fallback values
        fallback = {
            "respuesta": "Lo siento, tuve un problema al procesar mi respuesta interna. ¿Me lo podrías repetir?",
            "cita_libro": {},
            "emociones": self.emotions.copy(),
            "nota_clinica": "Error al parsear el JSON de la IA.",
            "temas_detectados": [],
            "patrones_detectados": [],
            "recursos_detectados": [],
            "vinculos_detectados": [],
            "opciones_respuesta": ["Cuéntame más", "No estoy seguro", "Hablemos de otra cosa"]
        }
        
        data = None
        try:
            data = json.loads(cleaned)
        except Exception:
            # Intentar extraer el objeto JSON usando regex
            match = re.search(r"\{[\s\S]*\}", cleaned)
            if match:
                try:
                    data = json.loads(match.group())
                except Exception:
                    pass
                    
        if data is None or not isinstance(data, dict):
            # Si todo falla, usar texto crudo si parece un mensaje normal
            if cleaned and not cleaned.startswith("{"):
                fallback["respuesta"] = cleaned
            return fallback

        # Validar y desinfectar 'respuesta'
        respuesta = data.get("respuesta", "")
        if not isinstance(respuesta, str) or not respuesta.strip():
            respuesta = "Entiendo. Cuéntame más sobre eso."
        fallback["respuesta"] = respuesta

        # Validar y desinfectar 'emociones'
        emociones = data.get("emociones")
        if isinstance(emociones, dict):
            for k in fallback["emociones"].keys():
                val = emociones.get(k)
                if isinstance(val, (int, float)):
                    fallback["emociones"][k] = max(0, min(100, int(val)))
                elif isinstance(val, str) and val.isdigit():
                    fallback["emociones"][k] = max(0, min(100, int(val)))
        
        # Validar listas de detección
        for field in ["temas_detectados", "patrones_detectados", "recursos_detectados", "vinculos_detectados"]:
            lst = data.get(field)
            if isinstance(lst, list):
                fallback[field] = [str(x)[:50] for x in lst if x]
            else:
                fallback[field] = []

        # Validar 'nota_clinica'
        nota = data.get("nota_clinica", "")
        fallback["nota_clinica"] = str(nota)[:500] if nota else ""

        # Validar 'opciones_respuesta'
        opciones = data.get("opciones_respuesta")
        if isinstance(opciones, list) and len(opciones) > 0:
            fallback["opciones_respuesta"] = [str(x)[:60] for x in opciones if x]
        else:
            fallback["opciones_respuesta"] = ["Cuéntame más", "No estoy seguro", "Hablemos de otra cosa"]

        # Validar 'cita_id' y mapear a fragmentos verificados programáticamente
        cita_id = data.get("cita_id")
        fallback["cita_libro"] = {}
        if fragments and (isinstance(cita_id, int) or (isinstance(cita_id, str) and cita_id.isdigit())):
            c_idx = int(cita_id)
            if 1 <= c_idx <= len(fragments):
                frag = fragments[c_idx - 1]
                fallback["cita_libro"] = {
                    "libro": frag.get("libro", "Libro"),
                    "autor": frag.get("autor", "Autor"),
                    "texto": frag.get("texto", "")
                }

        return fallback

    def _error_response(self, message: str) -> dict:
        return {
            "respuesta": message,
            "cita_libro": {},
            "emociones": self.emotions.copy(),
            "nota_clinica": "",
            "temas_detectados": [],
            "patrones_detectados": [],
            "recursos_detectados": [],
            "vinculos_detectados": [],
            "opciones_respuesta": ["Quiero intentar de nuevo", "Necesito hablar de otra cosa"],
        }