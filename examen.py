def calcular_nota(respuestas_totales, respuestas_correctas, respuestas_incorrectas):
    # Cada acierto suma 1, cada fallo resta 1/3, blanco no suma ni resta.
    if respuestas_totales <= 0:
        return 0
    puntuacion = respuestas_correctas - (respuestas_incorrectas / 3)
    nota = max(0, min(10, (puntuacion / respuestas_totales) * 10))
    return round(nota, 2)