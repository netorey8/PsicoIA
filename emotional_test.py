"""
emotional_test.py — Diagnosticador de Patrones Inconscientes, Heridas de la Infancia y Lealtades Familiares.
Enfocado en psicoanálisis, psicología profunda y patrones del desarrollo temprano.
"""

QUESTIONS = [
    {
        "id": 1,
        "pregunta": "Al recordar tu infancia y el ambiente familiar donde creciste, ¿cuál era la sensación emocional más constante?",
        "categoria": "herida_abandono",
        "opciones": [
            ("Sensación de acompañamiento y seguridad emocional", 1),
            ("Sostén material, pero con cierta distancia o frialdad afectiva", 2),
            ("Temor recurrente a la soledad, inestabilidad o ausencias de las figuras de cuidado", 3),
            ("Sensación profunda de desamparo o tener que resolver la vida solo/a desde muy pequeño/a", 4)
        ]
    },
    {
        "id": 2,
        "pregunta": "En las dinámicas de tu familia de origen, ¿qué rol sentías que debías asumir inconscientemente?",
        "categoria": "parentificacion_control",
        "opciones": [
            ("El rol de un niño/a cuidado/a y sin cargas de adultos", 1),
            ("El/la hijo/a pacificante que evitaba discusiones entre los padres", 2),
            ("El/la 'hijo/a fuerte' o cuidador/a de mis propios padres o hermanos (parentificación)", 3),
            ("El/la perfecto/a que no podía cometer errores ni mostrar debilidad para ser aceptado/a", 4)
        ]
    },
    {
        "id": 3,
        "pregunta": "Cuando en tus relaciones adultas percibes cierta distancia o silencio en la otra persona, ¿cuál es tu primera reacción inconsciente?",
        "categoria": "herida_rechazo",
        "opciones": [
            ("Doy espacio con tranquilidad, sin asumir que es hacia mí", 1),
            ("Intento indagar con calma si algo le pasa", 2),
            ("Siento una angustia automática creyendo que hice algo mal o me van a dejar", 3),
            ("Me aíslo o me adelanto a cortar el vínculo para evitar que me rechacen primero", 4)
        ]
    },
    {
        "id": 4,
        "pregunta": "¿Cómo se manejaba la expresión de la vulnerabilidad o la tristeza en tu hogar de origen?",
        "categoria": "humillacion_culpa",
        "opciones": [
            ("Se validaba y escuchaba con empatía", 1),
            ("Se minimizaba con frases como 'no es para tanto'", 2),
            ("Se criticaba o castigaba (sentía que estorbaba si lloraba o mostraba dolor)", 3),
            ("Era algo que daba vergüenza o culpa mostrar; aprendí a tragarme todo", 4)
        ]
    },
    {
        "id": 5,
        "pregunta": "¿Sientes que estás repitiendo un mandato o destino familiar (miedos, elecciones de pareja, sacrificios) que no te pertenece del todo?",
        "categoria": "lealtad_inconsciente",
        "opciones": [
            ("No, siento autonomía plena en mis decisiones de vida", 1),
            ("Dudo en ocasiones, pero logro marcar límites con mi historia familiar", 2),
            ("Siento culpa si soy más feliz o exitoso/a que mis padres o familiares", 3),
            ("Elijo parejas o situaciones que me hacen sufrir de forma idéntica a la historia de mi hogar", 4)
        ]
    },
    {
        "id": 6,
        "pregunta": "Ante situaciones donde necesitas poner un límite a los demás, ¿qué pensamiento automático surge?",
        "categoria": "herida_rechazo",
        "opciones": [
            ("Puedo poner límites sin sentirme mal por ello", 1),
            ("Me cuesta, pero lo intento cuando es importante", 2),
            ("Siento miedo de que se enojen o me abandonen si digo que no", 3),
            ("Prefiero callarme y aguantar antes que arriesgar que me rechacen o se vayan", 4)
        ]
    },
    {
        "id": 7,
        "pregunta": "¿Cómo recibiste el afecto y el reconocimiento en tu infancia?",
        "categoria": "herida_abandono",
        "opciones": [
            ("Con frecuencia y de forma espontánea, sin condiciones", 1),
            ("Solo cuando cumplía expectativas o me portaba bien", 2),
            ("Era escaso e impredecible — nunca sabía cuándo iba a venir", 3),
            ("Prácticamente ausente — no recuerdo haberme sentido visto/a ni valorado/a", 4)
        ]
    },
    {
        "id": 8,
        "pregunta": "¿Con cuál de estas frases internalizadas te identificas más al reflexionarlo honestamente?",
        "categoria": "humillacion_culpa",
        "opciones": [
            ("'Soy suficiente y merezco lo que quiero'", 1),
            ("'Tengo que esforzarme mucho para merecer'", 2),
            ("'Si me muestro tal como soy, los demás se irán o me rechazarán'", 3),
            ("'Mis necesidades son una carga para los demás; mejor no pido ni doy problemas'", 4)
        ]
    },
    {
        "id": 9,
        "pregunta": "En tu familia de origen, ¿cómo se hablaba del éxito personal, del placer o de la superación individual?",
        "categoria": "lealtad_inconsciente",
        "opciones": [
            ("Se celebraba y apoyaba con genuino orgullo", 1),
            ("Se veía con cierta indiferencia o normalidad", 2),
            ("Con desconfianza o envidia encubierta ('¿quién te crees?')", 3),
            ("Sobresalir era visto como una traición o un abandono a la familia ('no te olvides de dónde vienes')", 4)
        ]
    },
    {
        "id": 10,
        "pregunta": "¿Cómo describes la figura de autoridad principal en tu infancia (padre, madre o quien te cuidó)?",
        "categoria": "parentificacion_control",
        "opciones": [
            ("Presente, afectuosa y con límites claros y amorosos", 1),
            ("Muy exigente o perfeccionista, con amor condicionado al rendimiento", 2),
            ("Ausente emocionalmente o físicamente (trabajo, enfermedad, adicciones)", 3),
            ("Impredecible, crítica o con necesidades emocionales que yo debía satisfacer siendo niño/a", 4)
        ]
    },
]


def analyze_test_results(answers: dict) -> dict:
    """
    Analiza las respuestas y determina el patrón psicoanalítico predominante
    con el enfoque clínico más efectivo sugerido.
    """
    scores = {
        "herida_abandono": 0,
        "herida_rechazo": 0,
        "humillacion_culpa": 0,
        "parentificacion_control": 0,
        "lealtad_inconsciente": 0
    }

    for q in QUESTIONS:
        q_id = q["id"]
        cat = q["categoria"]
        pts = answers.get(q_id, 1)
        scores[cat] += pts

    # Patrón predominante
    max_cat = max(scores, key=scores.get)

    perfiles = {
        "herida_abandono": {
            "patron": "Herida de Abandono y Apego Ansioso",
            "descripcion": (
                "Tu historia temprana estuvo marcada por ausencias emocionales, inestabilidad "
                "o figuras de apego impredecibles. Esto generó un modo de vincularte en el que "
                "el miedo a quedarte solo/a o a perder el amor se convirtió en el motor inconsciente "
                "de muchas de tus decisiones en las relaciones adultas."
            ),
            "manifestaciones": [
                "Hipervigilancia en las relaciones (buscas señales de que te van a dejar)",
                "Tendencia a tolerar situaciones dañinas por miedo al desamparo",
                "Dificultad para estar solo/a sin una sensación de angustia",
                "Aferramiento emocional o, al contrario, desapego para autoprotegerse"
            ],
            "enfoque_sugerido": "Psicoanálisis (Sigmund Freud / John Bowlby - Teoría del Apego)",
            "recomendacion": (
                "Explorar las figuras tempranas de apego, los vínculos originales y comprender "
                "cómo se transfieren a las relaciones actuales. Trabajar la internalización "
                "de una 'base segura' interna que no dependa de la presencia externa."
            )
        },
        "herida_rechazo": {
            "patron": "Herida de Rechazo y Desvalorización Temprana",
            "descripcion": (
                "En tu historia temprana recibiste mensajes —verbales o silenciosos— de que "
                "tus necesidades, deseos o presencia no eran del todo bienvenidos. Esto activó "
                "un mecanismo de retirada o invisibilidad como forma de protección: 'si no me muestro, "
                "no pueden herirme'. En la vida adulta se traduce en miedo al juicio, autosabotaje "
                "o relaciones donde eliges quedarte pequeño/a para no incomodar."
            ),
            "manifestaciones": [
                "Dificultad para recibir elogios o reconocimiento sin dudar de ellos",
                "Adelantarse a cortar relaciones antes de que te rechacen",
                "Sensación de ser 'demasiado' o 'no suficiente' simultáneamente",
                "Miedo irracional al juicio ajeno o a ocupar espacio propio"
            ],
            "enfoque_sugerido": "Terapia Humanista (Carl Rogers) / Psicoanálisis",
            "recomendacion": (
                "Trabajar la autoestima profunda desde la autoaceptación incondicional. "
                "Revisar los introyectos (mensajes absorbidos de figuras parentales) sobre el "
                "valor propio y reconstruir la identidad desde la autenticidad, no desde "
                "la búsqueda de aprobación externa."
            )
        },
        "humillacion_culpa": {
            "patron": "Herida de Humillación y Mandato de Postergación",
            "descripcion": (
                "Aprendiste tempranamente que mostrar necesidades, fragilidad o alegría personal "
                "podía traer vergüenza, crítica o desaprobación. Con el tiempo interiorizaste "
                "que postergar tus propias necesidades en favor de los demás era la forma de "
                "ser aceptado/a y de evitar el castigo emocional. Esta dinámica suele manifestarse "
                "como culpa profunda cada vez que priorizas tu propio bienestar."
            ),
            "manifestaciones": [
                "Incapacidad de disfrutar algo sin sentir que 'no te lo mereces'",
                "Tendencia a la autoexigencia extrema o al perfeccionismo paralizante",
                "Vergüenza corporal, emocional o social desproporcionada ante errores menores",
                "Dificultad para recibir cuidado sin sentirte en deuda"
            ],
            "enfoque_sugerido": "Logoterapia (Viktor Frankl) / Psicoanálisis (Sigmund Freud)",
            "recomendacion": (
                "Reconstruir la relación con tus propias necesidades como algo legítimo y no "
                "egoísta. Explorar los mandatos de culpa heredados y trabajar el perdón interno. "
                "La logoterapia puede ayudar a reconectar con un sentido de merecimiento "
                "y dignidad personal desde adentro hacia afuera."
            )
        },
        "parentificacion_control": {
            "patron": "Parentificación y Necesidad de Control Hiperresponsable",
            "descripcion": (
                "Desde pequeño/a asumiste responsabilidades emocionales o prácticas que "
                "correspondían a los adultos de tu entorno. Te convertiste en el/la 'hijo/a fuerte', "
                "el pacificador, el cuidador o el perfecto/a. Esta dinámica te dio una sensación "
                "de valía condicionada al rendimiento y al control. De adulto/a, soltar el control "
                "o pedir ayuda se siente como una amenaza a tu identidad."
            ),
            "manifestaciones": [
                "Hiperresponsabilidad: sientes que todo depende de ti",
                "Dificultad extrema para delegar o pedir ayuda ('es más fácil hacerlo yo')",
                "Perfeccionismo como identidad más que como herramienta",
                "Agotamiento crónico por sostener a los demás antes que a ti mismo/a"
            ],
            "enfoque_sugerido": "Terapia Cognitivo-Conductual (TCC) / Psicoanálisis Relacional",
            "recomendacion": (
                "Revisar el origen de la responsabilidad excesiva y los roles rígidos internalizados. "
                "Trabajar la tolerancia a la imperfección y la delegación como actos de confianza, "
                "no de debilidad. Reconstruir la identidad más allá del rol de 'el que resuelve todo'."
            )
        },
        "lealtad_inconsciente": {
            "patron": "Lealtad Familiar Inconsciente y Repetición Transgeneracional",
            "descripcion": (
                "Existe en ti una corriente invisible de lealtad hacia tu sistema familiar que "
                "puede estar guiando decisiones de pareja, de carrera o de vida sin que lo notes "
                "conscientemente. Bowen y Hellinger denominan esto como 'mandatos del campo familiar': "
                "la tendencia a repetir patrones o destinos de figuras previas de la familia por "
                "amor inconsciente hacia el sistema del que formamos parte."
            ),
            "manifestaciones": [
                "Culpa irracional cuando superas o te alejas emocionalmente de tu familia de origen",
                "Elecciones de pareja que reproducen dinámicas vividas en el hogar de infancia",
                "Sentir que no tienes 'permiso interno' para ser feliz o exitoso/a más allá del nivel familiar",
                "Bloqueos inexplicables justo cuando estás cerca de algo bueno"
            ],
            "enfoque_sugerido": "Psicoanálisis Transgeneracional / Constelaciones Familiares (Bert Hellinger)",
            "recomendacion": (
                "Explorar los sistemas familiares, los secretos, las lealtades invisibles y los "
                "mandatos no verbalizados que se transmiten entre generaciones. "
                "El trabajo con el árbol genealógico emocional puede revelar patrones que "
                "trascienden la historia personal inmediata."
            )
        }
    }

    resultado = perfiles.get(max_cat, perfiles["herida_abandono"])
    resultado["puntuaciones"] = scores
    resultado["categoria_principal"] = max_cat

    # Segunda categoría más alta (patrón secundario)
    scores_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if len(scores_ordenados) > 1:
        segunda_cat = scores_ordenados[1][0]
        resultado["patron_secundario"] = perfiles.get(segunda_cat, {}).get("patron", "")

    return resultado
