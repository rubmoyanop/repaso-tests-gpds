# Repaso Tests GPDS

Este es un pequeño código para practicar los tests de SIDRA de GPDS más cómodamente y con estadísticas.

## Uso

- El programa permite seleccionar un PDF de preguntas (formato compatible con los subidos por los profesores).
- Se extraen preguntas, se modifica el orden y se realiza el cuestionario subido.
- Al finalizar, se muestra un resumen del cuestionario con el total de preguntas realizadas, nota, aciertos, fallos y preguntas en blanco.
- Puedes saltar una pregunta (no cuenta en el total).
- El botón "Ver estadísticas" en el menú principal permite consultar estadísticas globales y detalladas.

## Estadísticas

- El sistema guarda automáticamente estadísticas de cada pregunta, incluyendo:
  - Número de intentos y fallos.
  - Tiempo medio de respuesta.
  - Historial de respuestas.
  - Cuestionario (nombre del archivo PDF de origen).
- En la pestaña de estadísticas puedes ver:
  - Resumen general.
  - Preguntas más problemáticas (ordenadas por tasa de fallos e intentos).
  - Estadísticas por cuestionario.
  - Evolución del rendimiento (con fecha y hora).
  - Tiempos medios de respuesta por cuestionario.
  - Detalle de cada pregunta (doble clic).

## Dependencias

Instala las dependencias necesarias con:
```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` contiene todas las dependencias necesarias para ejecutar el programa.

## Ejecución

Ejecuta el programa con el siguiente comando:

```bash
python testsGPDS.py
```