import re
import random
import os
from PyPDF2 import PdfReader

def leer_pdf(filename):
    preguntas = []
    try:
        with open(filename, 'rb') as archivo_pdf:
            lector_pdf = PdfReader(archivo_pdf)
            num_paginas = len(lector_pdf.pages)

            patron = r"Pregunta número:\s*(\d+)\s*(.*)\s*A:\s*(.*?)\s*B:\s*(.*?)\s*C:\s*(.*?)\s*D:\s*(.*?)\s*Respuesta correcta:\s*([A-D])"

            paginas = list(range(1, num_paginas))  # Nos saltamos la primera página
            random.shuffle(paginas) # Mezclamos las páginas para obtener preguntas aleatorias
            
            nombre_archivo = os.path.basename(filename)
            categoria = os.path.splitext(nombre_archivo)[0]  

            for pagina_num in paginas:
                pagina = lector_pdf.pages[pagina_num]
                texto = pagina.extract_text()

                match = re.search(patron, texto, re.DOTALL)
                if match:
                    texto_pregunta = match.group(2).replace("\n", " ")
                    pregunta = {
                        "pregunta": texto_pregunta,
                        "A": match.group(3).replace("\n", " "),
                        "B": match.group(4).replace("\n", " "),
                        "C": match.group(5).replace("\n", " "),
                        "D": match.group(6).replace("\n", " "),
                        "respuesta_correcta": match.group(7).replace("\n", " "),
                        "categoria": categoria,
                        "origen_archivo": filename
                    }
                    preguntas.append(pregunta)
                    if len(preguntas) == 10:  
                        break
    except FileNotFoundError:
        print("El archivo no existe.")
    except Exception as e:
        print(f"Error: {e}")
    return preguntas
