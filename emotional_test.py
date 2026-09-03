"""
emotional_test.py — Diagnosticador Híbrido de Patrones Inconscientes.
Parte 1: 15 preguntas de opción múltiple (puntuación cuantitativa por patrón).
Parte 2: 8 preguntas abiertas de profundidad psicoanalitica (analizadas por LLM).
"""

# ─────────────────────────────────────────────────────────────
# PARTE 1 — PREGUNTAS DE OPCIÓN MÚLTIPLE (puntuación por patrón)
# ─────────────────────────────────────────────────────────────

QUESTIONS = [

    # ─── HERIDA DE ABANDONO ───────────────────────────────────
    {
        "id": 1,
        "categoria": "herida_abandono",
        "pregunta": "Al recordar tu infancia, ¿cuál era la sensación más frecuente cuando estabas solo/a o las figuras de cuidado no estaban presentes?",
        "opciones": [
            ("Tranquilidad — sabía que regresarían y me sentía seguro/a", 1),
            ("Cierta incomodidad, pero lo manejaba bien", 2),
            ("Angustia o tristeza sin entender muy bien por qué", 3),
            ("Miedo intenso o una sensación real y constante de abandono", 4),
        ]
    },
    {
        "id": 2,
        "categoria": "herida_abandono",
        "pregunta": "¿Cómo recibiste el afecto de tu figura de cuidado principal durante la niñez?",
        "opciones": [
            ("Con frecuencia, de forma espontánea y sin condiciones", 1),
            ("Solo cuando me portaba bien o cumplía expectativas", 2),
            ("Era impredecible — nunca sabía cuándo vendría", 3),
            ("Prácticamente ausente — no recuerdo sentirme visto/a ni amado/a", 4),
        ]
    },
    {
        "id": 3,
        "categoria": "herida_abandono",
        "pregunta": "En tus relaciones adultas actuales, cuando alguien se aleja o guarda silencio de repente, ¿qué ocurre en ti de forma automática?",
        "opciones": [
            ("Lo tomo con calma, sin asumir que es por mi culpa", 1),
            ("Me genera algo de inquietud, pero lo manejo", 2),
            ("Siento angustia intensa, creyendo que algo hice mal o me van a dejar", 3),
            ("Entro en pánico, me desregulo o persigo a la persona para obtener respuesta", 4),
        ]
    },

    # ─── HERIDA DE RECHAZO ────────────────────────────────────
    {
        "id": 4,
        "categoria": "herida_rechazo",
        "pregunta": "De niño/a, ¿qué ocurría cuando expresabas una opinión, un deseo o una emoción diferente a la de tus padres o cuidadores?",
        "opciones": [
            ("Me escuchaban y validaban con respeto", 1),
            ("A veces me ignoraban, pero podía insistir sin represalias", 2),
            ("Sentía que era un estorbo o que lo que sentía no importaba", 3),
            ("Aprendí a no tener opiniones propias para evitar conflictos o rechazo", 4),
        ]
    },
    {
        "id": 5,
        "categoria": "herida_rechazo",
        "pregunta": "Cuando alguien te da un reconocimiento genuino o un cumplido sincero, ¿qué ocurre internamente?",
        "opciones": [
            ("Lo recibo con naturalidad y gratitud", 1),
            ("Lo agradezco, pero con cierta incomodidad", 2),
            ("Lo minimizo, lo dudo o busco el 'pero' escondido detrás", 3),
            ("Me genera ansiedad — siento que no lo merezco o que algo malo vendrá después", 4),
        ]
    },
    {
        "id": 6,
        "categoria": "herida_rechazo",
        "pregunta": "Ante la posibilidad de que alguien importante te juzgue o te rechace, ¿cuál es tu movimiento más frecuente?",
        "opciones": [
            ("Me muestro tal como soy y acepto el resultado", 1),
            ("Me cuido un poco, pero sin dejar de ser yo/a", 2),
            ("Ajusto quién soy para agradar y evitar el rechazo", 3),
            ("Me adelanto a alejarme o a cortar el vínculo antes de que me rechacen primero", 4),
        ]
    },

    # ─── HUMILLACIÓN / CULPA ──────────────────────────────────
    {
        "id": 7,
        "categoria": "humillacion_culpa",
        "pregunta": "¿Cómo se manejaba el llanto, la tristeza o la fragilidad emocional en tu hogar de infancia?",
        "opciones": [
            ("Con empatía — estaba bien mostrar que algo dolía", 1),
            ("Se minimizaba: 'no es para tanto', 'ya pasará'", 2),
            ("Se ignoraba o generaba incomodidad o enojo en los adultos", 3),
            ("Era motivo de vergüenza o burla — aprendí a tragarme todo", 4),
        ]
    },
    {
        "id": 8,
        "categoria": "humillacion_culpa",
        "pregunta": "¿Con cuál frase interna te identificas más al reflexionarlo honestamente?",
        "opciones": [
            ("'Soy suficiente y merezco lo bueno en mi vida'", 1),
            ("'Tengo que esforzarme mucho para sentir que merezco'", 2),
            ("'Si me muestro tal como soy, los demás se irán o me rechazarán'", 3),
            ("'Mis necesidades son una carga — mejor no pido ni doy problemas'", 4),
        ]
    },
    {
        "id": 9,
        "categoria": "humillacion_culpa",
        "pregunta": "Cuando cometes un error, ¿cómo es la voz interna que aparece?",
        "opciones": [
            ("Comprensiva — lo tomo como aprendizaje y sigo", 1),
            ("Me molesta, pero lo proceso relativamente rápido", 2),
            ("Me castiga de forma severa durante días", 3),
            ("Es devastadora — el error me hace sentir fundamentalmente defectuoso/a o indigno/a", 4),
        ]
    },

    # ─── PARENTIFICACIÓN / CONTROL ───────────────────────────
    {
        "id": 10,
        "categoria": "parentificacion_control",
        "pregunta": "¿Qué rol asumiste de forma inconsciente dentro de tu familia de origen?",
        "opciones": [
            ("El de un niño/a cuidado/a, sin cargas de adultos", 1),
            ("El de hijo/a que suavizaba tensiones o mediaba conflictos", 2),
            ("El de 'hijo/a fuerte' que sostenía emocionalmente a uno o ambos padres", 3),
            ("El perfecto/a que no podía fallar ni necesitar, porque el sistema familiar dependía de eso", 4),
        ]
    },
    {
        "id": 11,
        "categoria": "parentificacion_control",
        "pregunta": "¿Cómo te sientes cuando alguien más toma el control de una situación que te involucra?",
        "opciones": [
            ("Con alivio — delegar me ayuda", 1),
            ("Un poco incómodo/a, pero puedo soltarlo", 2),
            ("Con ansiedad — siento que algo saldrá mal si no estoy al mando", 3),
            ("Con angustia intensa — necesito retomar el control o siento que todo se derrumba", 4),
        ]
    },
    {
        "id": 12,
        "categoria": "parentificacion_control",
        "pregunta": "¿Cómo describirías a la figura principal que te cuidó en la infancia?",
        "opciones": [
            ("Presente, empática, con límites amorosos y consistentes", 1),
            ("Exigente o perfeccionista, pero con amor presente", 2),
            ("Ausente emocionalmente (trabajo, enfermedad, adicciones)", 3),
            ("Impredecible o con necesidades emocionales que yo debía satisfacer siendo niño/a", 4),
        ]
    },

    # ─── LEALTAD FAMILIAR / TRANSGENERACIONAL ────────────────
    {
        "id": 13,
        "categoria": "lealtad_inconsciente",
        "pregunta": "¿Sientes que hay un patrón o 'destino' familiar que se repite en tu vida aunque no lo hayas elegido conscientemente?",
        "opciones": [
            ("No, siento autonomía plena en mis decisiones de vida", 1),
            ("Dudo en ocasiones, pero logro distanciarme de esos patrones", 2),
            ("Sí, noto que repito situaciones de mi familia aunque no quiero", 3),
            ("Completamente — siento que vivo una historia que no es mía o que no tiene salida", 4),
        ]
    },
    {
        "id": 14,
        "categoria": "lealtad_inconsciente",
        "pregunta": "En tu familia de origen, ¿cómo se vivía el éxito personal, la alegría o la superación individual?",
        "opciones": [
            ("Se celebraba con genuino orgullo y apoyo", 1),
            ("Con indiferencia o normalidad", 2),
            ("Con desconfianza, envidia velada o frases como '¿quién te crees?'", 3),
            ("Sobresalir era visto como una traición o un abandono al sistema familiar", 4),
        ]
    },
    {
        "id": 15,
        "categoria": "lealtad_inconsciente",
        "pregunta": "Cuando estás a punto de lograr algo bueno (relación sana, éxito, bienestar), ¿qué ocurre con frecuencia?",
        "opciones": [
            ("Lo disfruto plenamente y lo sostengo con naturalidad", 1),
            ("Siento algo de incredulidad, pero avanzo", 2),
            ("Aparece culpa, autosabotaje o un bloqueo inexplicable", 3),
            ("Termino destruyendo lo bueno justo cuando estaba al alcance — siempre pasa igual", 4),
        ]
    },
]


# ─────────────────────────────────────────────────────────────
# PARTE 2 — PREGUNTAS ABIERTAS DE PROFUNDIDAD PSICOANALÍTICA
# ─────────────────────────────────────────────────────────────

OPEN_QUESTIONS = [
    {
        "id": "a1",
        "titulo": "Historia de pareja de tus padres",
        "pregunta": "¿Tus padres se divorciaron, hubo separaciones, infidelidades o conflictos graves en pareja durante tu infancia? Si es así, ¿cómo te sentiste en ese momento y cómo te sientes al respecto hoy?",
        "placeholder": "Ejemplo: Mis padres se separaron cuando tenía 8 años. En ese momento sentí que era mi culpa... Hoy siento...",
    },
    {
        "id": "a2",
        "titulo": "Relación con hermanos/as",
        "pregunta": "¿Cómo es tu relación actual con tus hermanos/as? ¿Hay cercanía, distancia, rivalidad o indiferencia? ¿Por qué crees que la relación es así?",
        "placeholder": "Ejemplo: Con mi hermano mayor casi no hablamos. Creo que fue porque siempre lo comparaban conmigo y eso generó...",
    },
    {
        "id": "a3",
        "titulo": "Secretos y silencios familiares",
        "pregunta": "¿Había algún tema del que no se hablaba en tu familia pero que todos sentían? ¿Un secreto, una pérdida, una vergüenza, una historia no contada? ¿Qué crees que ese silencio te transmitió?",
        "placeholder": "Ejemplo: Nunca se habló de la muerte de mi abuelo. Simplemente un día desapareció de las conversaciones y...",
    },
    {
        "id": "a4",
        "titulo": "El amor que observaste en casa",
        "pregunta": "¿Cómo era la relación entre tus padres o las parejas adultas que observaste de cerca en tu infancia? ¿Qué aprendiste del amor, la pareja y el compromiso al verlos?",
        "placeholder": "Ejemplo: Mis padres se peleaban mucho. Aprendí que el amor viene con gritos y... Hoy en mis relaciones repito...",
    },
    {
        "id": "a5",
        "titulo": "Pérdidas y duelos importantes",
        "pregunta": "¿Hubo una pérdida importante en tu historia o en tu familia (una muerte, una enfermedad, una migración, una crisis económica grave, una ruptura)? ¿Cómo afectó esa pérdida tu mundo emocional?",
        "placeholder": "Ejemplo: Mi abuela murió cuando tenía 6 años y fue la primera persona que me quiso de verdad. Desde entonces...",
    },
    {
        "id": "a6",
        "titulo": "Los mensajes que absorbiste de tu hogar",
        "pregunta": "¿Cuál era el mensaje más repetido en tu hogar, ya sea dicho o no dicho? Por ejemplo: 'hay que ser fuerte', 'no confíes en nadie', 'el dinero es lo importante', 'el amor duele'. ¿Ese mensaje sigue operando en ti hoy?",
        "placeholder": "Ejemplo: En mi casa nunca se decía 'te quiero'. El mensaje no dicho era que mostrar amor era una debilidad. Hoy me cuesta...",
    },
    {
        "id": "a7",
        "titulo": "Tu figura de identificación familiar",
        "pregunta": "¿Con quién de tu familia (abuelo/a, padre, madre, tío/a, hermano/a mayor) te identificas más o crees que te pareciste? ¿Esa persona vivió algo que tú también estás viviendo o repitiendo?",
        "placeholder": "Ejemplo: Soy muy parecido a mi papá. Él también tuvo relaciones difíciles y nunca terminó de estabilizarse. Yo ahora...",
    },
    {
        "id": "a8",
        "titulo": "Carta a tu yo de la infancia",
        "pregunta": "Si pudieras sentarte con el niño/a que fuiste a los 7 u 8 años y decirle algo que necesitaba escuchar en ese momento, ¿qué le dirías? ¿Qué necesitaba ese niño/a que no tuvo?",
        "placeholder": "Ejemplo: Le diría que no era su culpa que papá se fuera. Que él era suficiente. Que merecía ser visto...",
    },
]


# ─────────────────────────────────────────────────────────────
# ANÁLISIS CUANTITATIVO (preguntas de opción múltiple)
# ─────────────────────────────────────────────────────────────

def analyze_test_results(answers: dict) -> dict:
    """
    Analiza las respuestas de opción múltiple y determina el patrón predominante.
    """
    scores = {
        "herida_abandono":         0,
        "herida_rechazo":          0,
        "humillacion_culpa":       0,
        "parentificacion_control": 0,
        "lealtad_inconsciente":    0,
    }

    for q in QUESTIONS:
        scores[q["categoria"]] += answers.get(q["id"], 1)

    scores_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    max_cat = scores_ordenados[0][0]
    segunda_cat = scores_ordenados[1][0] if len(scores_ordenados) > 1 else None

    perfiles = {
        "herida_abandono": {
            "patron":      "Herida de Abandono y Apego Ansioso",
            "icono":       "🔴",
            "descripcion": (
                "Tu historia temprana estuvo marcada por ausencias emocionales, inestabilidad "
                "o figuras de apego impredecibles. Esto generó un modo de vincularte donde "
                "el miedo al desamparo se convirtió en el motor inconsciente de muchas decisiones."
            ),
            "manifestaciones": [
                "Hipervigilancia relacional (buscas señales de que te van a dejar)",
                "Tolerancia a relaciones dañinas por miedo al desamparo",
                "Dificultad para estar solo/a sin angustia de fondo",
                "Aferramiento intenso o desapego extremo como autoprotección",
                "Búsqueda constante de confirmación de que eres amado/a",
            ],
            "enfoque_sugerido": "Psicoanálisis (Teoría del Apego — John Bowlby / Donald Winnicott)",
            "recomendacion": (
                "Explorar las figuras tempranas de apego y cómo se transfieren a las relaciones actuales. "
                "Trabajar la internalización de una 'base segura' interna que no dependa "
                "de la presencia externa para existir emocionalmente."
            )
        },
        "herida_rechazo": {
            "patron":      "Herida de Rechazo y Desvalorización Temprana",
            "icono":       "🟠",
            "descripcion": (
                "Recibiste mensajes —verbales o silenciosos— de que tu presencia, deseos "
                "o necesidades no eran del todo bienvenidos. Activaste un mecanismo de retirada "
                "o invisibilidad como autoprotección. En la vida adulta: miedo al juicio, "
                "autosabotaje o permanecer pequeño/a para no incomodar."
            ),
            "manifestaciones": [
                "Dificultad para recibir elogios sin dudar de ellos",
                "Adelantarse a cortar relaciones antes de que te rechacen",
                "Ajustar quién eres para agradar y no generar conflicto",
                "Miedo irracional al juicio ajeno o a ocupar espacio propio",
                "Sensación de ser 'demasiado' o 'no suficiente' simultáneamente",
            ],
            "enfoque_sugerido": "Terapia Humanista (Carl Rogers) / Psicoanálisis del Self",
            "recomendacion": (
                "Trabajar la autoestima profunda desde la autoaceptación incondicional. "
                "Revisar los introyectos parentales sobre el valor propio y reconstruir "
                "la identidad desde la autenticidad, no desde la búsqueda de aprobación."
            )
        },
        "humillacion_culpa": {
            "patron":      "Herida de Humillación y Mandato de Postergación",
            "icono":       "🟡",
            "descripcion": (
                "Aprendiste tempranamente que mostrar necesidades, fragilidad o alegría podía "
                "traer vergüenza, crítica o desaprobación. Interiorizaste que postergar tus "
                "necesidades en favor de los demás era la forma de ser aceptado/a. Esta dinámica "
                "genera culpa profunda cada vez que priorizas tu propio bienestar."
            ),
            "manifestaciones": [
                "Incapacidad de disfrutar algo sin sentir que 'no te lo mereces'",
                "Autoexigencia extrema o perfeccionismo paralizante",
                "Vergüenza desproporcionada ante errores menores",
                "Dificultad para recibir cuidado sin sentirte en deuda",
                "Convertir el dolor ajeno en responsabilidad propia",
            ],
            "enfoque_sugerido": "Logoterapia (Viktor Frankl) / Psicoanálisis (Sigmund Freud)",
            "recomendacion": (
                "Reconstruir la relación con tus propias necesidades como algo legítimo y no egoísta. "
                "Explorar los mandatos de culpa heredados y trabajar el autoperdón interno. "
                "Reconectar con un sentido de merecimiento y dignidad desde adentro hacia afuera."
            )
        },
        "parentificacion_control": {
            "patron":      "Parentificación y Necesidad de Control Hiperresponsable",
            "icono":       "🔵",
            "descripcion": (
                "Desde pequeño/a asumiste responsabilidades emocionales o prácticas que "
                "correspondían a los adultos de tu entorno. Te convertiste en el/la 'hijo/a fuerte', "
                "el pacificador, el perfecto/a. Esto te dio una valía condicionada al rendimiento "
                "y al control. De adulto/a, soltar el control o pedir ayuda se siente como amenaza."
            ),
            "manifestaciones": [
                "Hiperresponsabilidad: sientes que todo depende de ti",
                "Dificultad extrema para delegar o pedir ayuda",
                "Perfeccionismo como identidad, no como herramienta",
                "Agotamiento crónico por sostener a los demás antes que a ti mismo/a",
                "Ansiedad intensa cuando algo escapa a tu control",
            ],
            "enfoque_sugerido": "Terapia Cognitivo-Conductual (TCC) / Psicoanálisis Relacional",
            "recomendacion": (
                "Revisar el origen de la responsabilidad excesiva y los roles rígidos internalizados. "
                "Trabajar la tolerancia a la imperfección y la delegación como actos de confianza, "
                "no de debilidad. Reconstruir la identidad más allá del rol de 'el que resuelve todo'."
            )
        },
        "lealtad_inconsciente": {
            "patron":      "Lealtad Familiar Inconsciente y Repetición Transgeneracional",
            "icono":       "🟣",
            "descripcion": (
                "Existe en ti una corriente invisible de lealtad hacia tu sistema familiar que "
                "puede estar guiando decisiones de pareja, de carrera o de vida sin que lo notes. "
                "La tendencia a repetir patrones o 'destinos' familiares responde a un amor "
                "inconsciente hacia el sistema del que formas parte, aunque ese amor te cueste el bienestar."
            ),
            "manifestaciones": [
                "Culpa irracional cuando superas o te alejas emocionalmente de tu familia de origen",
                "Elecciones de pareja que reproducen dinámicas del hogar de infancia",
                "Sensación de no tener 'permiso interno' para ser feliz o exitoso/a",
                "Autosabotaje justo cuando estás cerca de algo bueno",
                "Sensación de vivir una historia que no es del todo tuya",
            ],
            "enfoque_sugerido": "Psicoanálisis Transgeneracional / Constelaciones Familiares (Bert Hellinger)",
            "recomendacion": (
                "Explorar los sistemas familiares, los secretos, las lealtades invisibles y los "
                "mandatos no verbalizados que se transmiten entre generaciones. "
                "El árbol genealógico emocional puede revelar patrones que trascienden tu historia personal."
            )
        },
    }

    resultado = perfiles[max_cat].copy()
    resultado["puntuaciones"] = scores
    resultado["categoria_principal"] = max_cat
    resultado["patron_secundario"] = perfiles[segunda_cat]["patron"] if segunda_cat else ""
    resultado["icono_secundario"]   = perfiles[segunda_cat]["icono"] if segunda_cat else ""

    max_pts   = scores[max_cat]
    total_pts = sum(scores.values()) or 1
    certeza   = int((max_pts / total_pts) * 100)
    resultado["certeza"] = min(certeza + 15, 97)

    return resultado


# ─────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DEL PROMPT LLM PARA PREGUNTAS ABIERTAS
# ─────────────────────────────────────────────────────────────

def build_open_analysis_prompt(mc_result: dict, open_answers: dict) -> str:
    """
    Construye el prompt que se enviará al LLM para analizar las respuestas abiertas
    del paciente junto con el resultado cuantitativo ya obtenido.
    """
    patron_principal = mc_result.get("patron", "No determinado")
    patron_secundario = mc_result.get("patron_secundario", "")
    enfoque = mc_result.get("enfoque_sugerido", "")

    respuestas_texto = []
    for q in OPEN_QUESTIONS:
        respuesta = open_answers.get(q["id"], "").strip()
        if respuesta:
            respuestas_texto.append(
                f"[{q['titulo']}]\nPregunta: {q['pregunta']}\nRespuesta del paciente: {respuesta}"
            )

    if not respuestas_texto:
        return ""

    respuestas_bloque = "\n\n".join(respuestas_texto)

    prompt = f"""Eres un psicólogo clínico especializado en psicoanálisis, teoría del apego y psicología transgeneracional. 
Estás realizando un análisis profundo de las respuestas de un paciente en un test de diagnóstico de patrones emocionales inconscientes.

RESULTADO CUANTITATIVO PREVIO (de las preguntas de opción múltiple):
- Patrón principal detectado: {patron_principal}
- Patrón secundario: {patron_secundario}
- Enfoque terapéutico sugerido: {enfoque}

RESPUESTAS ABIERTAS DEL PACIENTE (análisis cualitativo que debes realizar):
{respuestas_bloque}

Con base en todo lo anterior, realiza un análisis clínico profundo que incluya:
1. Confirmación o matización del patrón principal detectado cuantitativamente
2. Identificación de dinámicas familiares o sistémicas específicas que emergen de las respuestas abiertas
3. Heridas o temas psicodinámicos clave que el paciente necesita explorar en sesión
4. Una reflexión sobre cómo estos patrones pueden estar afectando sus relaciones y decisiones actuales
5. Un mensaje empático y orientador, sin diagnóstico definitivo, que lo invite a continuar explorando en sesión terapéutica

Responde en formato JSON con la siguiente estructura exacta:
{{
  "confirmacion_patron": "texto que confirma o matiza el patrón principal",
  "dinamicas_familiares": ["dinámica 1", "dinámica 2", "dinámica 3"],
  "temas_para_sesion": ["tema 1", "tema 2", "tema 3"],
  "impacto_actual": "párrafo sobre cómo los patrones afectan su vida hoy",
  "mensaje_empático": "mensaje cálido, profundo y motivador para el paciente"
}}"""

    return prompt
