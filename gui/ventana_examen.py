import tkinter as tk
from tkinter import messagebox
import time
from datetime import datetime
import os
import estadisticas
from examen import calcular_nota

def iniciar_examen(preguntas, root_menu=None, root=None):
    resultados = {"totales": 0, "correctas": 0, "falladas": 0, "saltadas": 0}
    sesion_id = datetime.now().strftime("%Y%m%d%H%M%S")
    tiempos_respuesta = {}

    if root is None:
        root = tk.Tk()
        is_main = True
    else:
        root = tk.Toplevel(root)
        is_main = False

    root.title("Examen GPDS")
    root.configure(bg="#f0f0f0")
    root.update_idletasks()
    try:
        root.state('zoomed')
    except tk.TclError:
        root.attributes('-zoomed', True)
    except Exception:
        root.attributes('-fullscreen', True)

    font_question = ("Helvetica", 18)
    font_option = ("Helvetica", 16)

    lbl_pregunta = tk.Label(root, text="", wraplength=1200, justify="center", bg="#f0f0f0", font=font_question)
    lbl_pregunta.pack(pady=30)

    opciones = {}
    colores = {
        "A": "#4CAF50",
        "B": "#2196F3",
        "C": "#FFC107",
        "D": "#FF5722"
    }
    for key in ["A", "B", "C", "D"]:
        frame = tk.Frame(root, bg=colores[key], bd=2, relief="raised", cursor="hand2")
        frame.pack(pady=12, padx=100, fill="x")
        msg = tk.Message(frame, text="", width=1100, font=font_option, bg=colores[key], fg="white" if key != "C" else "black", justify="left")
        msg.pack(padx=10, pady=10, fill="x")
        opciones[key] = {"frame": frame, "msg": msg}

    btn_s = tk.Button(root, text="Saltar pregunta", width=70, height=2, bg="#9E9E9E", fg="white", font=font_option)
    btn_s.pack(pady=25)

    def cerrar_todo(event=None):
        try:
            root.quit()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass
        if root_menu:
            try:
                root_menu.quit()
            except Exception:
                pass
            try:
                root_menu.destroy()
            except Exception:
                pass
        os._exit(0)  

    btn_exit = tk.Button(root, text="Salir", width=20, height=2, bg="#f44336", fg="white", font=font_option, command=cerrar_todo)
    btn_exit.pack(side="bottom", pady=20)

    root.protocol("WM_DELETE_WINDOW", cerrar_todo)

    def mostrar_pregunta(index):
        if index >= len(preguntas):
            root.after(100, mostrar_estadisticas)
            return

        pregunta = preguntas[index]
        tiempos_respuesta[index] = time.time()  
        lbl_pregunta.config(text=f"Pregunta {index + 1}: {pregunta['pregunta']}")

        for key, widget in opciones.items():
            widget['frame'].unbind("<Button-1>")
            widget['msg'].unbind("<Button-1>")
            widget['msg'].config(text=f"{key}: {pregunta[key]}")
            widget['frame'].bind("<Button-1>", lambda e, k=key: responder(k, index))
            widget['msg'].bind("<Button-1>", lambda e, k=key: responder(k, index))

        btn_s.config(command=lambda: responder("S", index))

    def responder(respuesta, index):
        tiempo_respuesta = time.time() - tiempos_respuesta.get(index, time.time())
        resultados["totales"] += 1
        if respuesta == preguntas[index]["respuesta_correcta"]:
            resultados["correctas"] += 1
            messagebox.showinfo("Resultado", "¡Respuesta correcta!")
            estadisticas.update_stats(
                preguntas[index]["pregunta"], 
                True, 
                categoria=preguntas[index]["categoria"],
                tiempo=tiempo_respuesta,
                sesion_id=sesion_id,
                archivo=preguntas[index].get("origen_archivo")
            )
        elif respuesta == "S":
            resultados["saltadas"] += 1
            resultados["totales"] -= 1  # No cuenta como respondida
            messagebox.showinfo("Resultado", "Pregunta saltada.")
        else:
            resultados["falladas"] += 1
            messagebox.showinfo("Resultado", f"Respuesta incorrecta. Correcta: {preguntas[index]['respuesta_correcta']}")
            estadisticas.update_stats(
                preguntas[index]["pregunta"], 
                False, 
                categoria=preguntas[index]["categoria"],
                tiempo=tiempo_respuesta,
                sesion_id=sesion_id,
                archivo=preguntas[index].get("origen_archivo")
            )

        if root.winfo_exists():
            mostrar_pregunta(index + 1)

    def mostrar_estadisticas():
        if not root.winfo_exists():
            return
        nota = calcular_nota(resultados["totales"], resultados["correctas"], resultados["falladas"])
        resumen = (
            f"Correctas: {resultados['correctas']}\n"
            f"Falladas: {resultados['falladas']}\n"
            f"En blanco: {resultados['saltadas']}\n"
            f"Totales: {resultados['totales']}\n"
            f"Nota: {nota:.2f}"
        )
        if messagebox.askyesno("Estadísticas finales", resumen + "\n\n¿Quieres hacer otro examen?"):
            try:
                root.destroy()
            except Exception:
                pass
            if root_menu:
                root_menu.deiconify()
        else:
            cerrar_todo()

    import signal
    def signal_handler(sig, frame):
        cerrar_todo()
    signal.signal(signal.SIGINT, signal_handler)

    mostrar_pregunta(0)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        cerrar_todo()
    if is_main:
        try:
            root.quit()
            root.destroy()
        except Exception:
            pass
