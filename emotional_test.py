"""
emotional_test.py — Test de Detección de Patrones Emocionales y Recomendación de Enfoque Psicoeducativo.
"""

# Lista de preguntas del test psicoeducativo
QUESTIONS = [
    {
        "id": 1,
        "pregunta": "¿Con qué frecuencia sientes que ante un problema pequeño imaginas el peor escenario posible?",
        "categoria": "cognitivo_catastrofismo",
        "opciones": [
            ("Rara vez o nunca", 1),
            ("A veces", 2),
            ("Frecuentemente", 3),
            ("Casi siempre", 4)
        ]
    },
    {
        "id": 2,
        "pregunta": "¿Sueles experimentar una sensación recurrente de vacío o falta de propósito claro en tus actividades diarias?",
        "categoria": "vacio_existencial",
        "opciones": [
            ("No, tengo claridad de mi rumbo", 1),
            ("Ocasionalmente al estar solo/a", 2),
            ("Con bastante frecuencia", 3),
            ("Constantemente me cuestiono si tiene sentido", 4)
        ]
    },
    {
        "id": 3,
        "pregunta": "Cuando tienes tensión o angustia, ¿con qué frecuencia buscas la aprobación o presencia inmediata de otra persona para calmarte?",
        "categoria": "apego_dependencia",
        "opciones": [
            ("Puedo autorregularme solo/a con facilidad", 1),
            ("Prefiero compañía, pero puedo manejarlo", 2),
            ("Me cuesta mucho estar solo/a en momentos así", 3),
            ("Siento una urgencia extrema por contacto/confirmación", 4)
        ]
    },
    {
        "id": 4,
        "pregunta": "¿Sientes que tus pensamientos van tan rápido que se reflejan en tensión física (taquicardia, opresión, insomnio)?",
        "categoria": "ansiedad_somatizacion",
        "opciones": [
            ("Rara vez", 1),
            ("En ocasiones estresantes", 2),
            ("Frecuentemente a la semana", 3),
            ("Diariamente me cuesta trabajo desconectar", 4)
        ]
    },
    {
        "id": 5,
        "pregunta": "¿Te descubres repitiendo frases internas como 'soy un fracaso', 'nada me sale bien' o 'no soy suficiente'?",
        "categoria": "cognitivo_catastrofismo",
        "opciones": [
            ("Nunca me hablo así", 1),
            ("Solo cuando cometo errores grandes", 2),
            ("Con frecuencia cuando algo sale mal", 3),
            ("Es mi diálogo interno constante", 4)
        ]
    },
    {
        "id": 6,
        "pregunta": "¿Sientes que estás viviendo en 'piloto automático' cumpliendo expectativas de otros más que los tuyos propios?",
        "categoria": "vacio_existencial",
        "opciones": [
            ("No, vivo de forma congruente con mis valores", 1),
            ("A veces me distraigo de mis deseos", 2),
            ("Frecuentemente me siento desconectado/a de mí", 3),
            ("Siento que no me conozco realmente", 4)
        ]
    }
]

def analyze_test_results(answers: dict) -> dict:
    """
    Analiza las respuestas recibidas (diccionario con id_pregunta -> puntaje)
    y determina el patrón predominante y el enfoque clínico sugerido.
    """
    scores = {
        "cognitivo_catastrofismo": 0,
        "vacio_existencial": 0,
        "apego_dependencia": 0,
        "ansiedad_somatizacion": 0
    }
    
    for q in QUESTIONS:
        q_id = q["id"]
        cat = q["categoria"]
        pts = answers.get(q_id, 1)
        scores[cat] += pts

    # Encontrar la categoría con mayor puntuación
    max_cat = max(scores, key=scores.get)
    
    dict_resultados = {
        "cognitivo_catastrofismo": {
            "patron": "Catastrofismo y Distorsión Cognitiva",
            "descripcion": "Tiendes a anticipar escenarios negativos y a validar pensamientos automáticos de desvalorización.",
            "enfoque_sugerido": "Terapia Cognitivo-Conductual (TCC)",
            "recomendacion": "Identificar pensamientos automáticos, cuestionar su evidencia real y reestructurar creencias limitantes."
        },
        "vacio_existencial": {
            "patron": "Búsqueda de Sentido / Vacío Existencial",
            "descripcion": "Experimentas dudas profundas sobre el propósito de tus acciones y desconexión con tus valores personales.",
            "enfoque_sugerido": "Logoterapia (Viktor Frankl)",
            "recomendacion": "Explorar fuentes de significado personal, libertad de actitud ante la adversidad y valores vivenciales."
        },
        "apego_dependencia": {
            "patron": "Ansiedad Relacional y Apego Sensible",
            "descripcion": "Tus emociones dependen en gran medida del estado de tus vínculos significativos y de la búsqueda de validación externa.",
            "enfoque_sugerido": "Terapia Humanista (Carl Rogers)",
            "recomendacion": "Fortalecer la autoaceptación incondicional, la autonomía emocional y el autoconcepto."
        },
        "ansiedad_somatizacion": {
            "patron": "Hiperactivación Emocional y Rumia",
            "descripcion": "Tu sistema nervioso reacciona con alta intensidad emocional y tensión corporal ante la incertidumbre.",
            "enfoque_sugerido": "Terapia Cognitivo-Conductual (TCC)",
            "recomendacion": "Combinar reestructuración cognitiva con ejercicios de autorregulación (como la respiración guiada 4-4-4-4)."
        }
    }
    
    resultado = dict_resultados.get(max_cat, dict_resultados["cognitivo_catastrofismo"])
    resultado["puntuaciones"] = scores
    return resultado
