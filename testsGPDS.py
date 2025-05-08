#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
import estadisticas
from pdf_parser import leer_pdf
from gui.ventana_examen import iniciar_examen

def menu_principal():
    root_menu = tk.Tk()
    root_menu.title("Simulacro Examen GPDS")
    root_menu.configure(bg="#f0f0f0")
    root_menu.update_idletasks()
    try:
        root_menu.state('zoomed')
    except tk.TclError:
        root_menu.attributes('-zoomed', True)
    except Exception:
        root_menu.attributes('-fullscreen', True)

    font_title = ("Helvetica", 28, "bold")
    font_button = ("Helvetica", 18)

    lbl_title = tk.Label(root_menu, text="Simulacro Examen GPDS", bg="#f0f0f0", font=font_title)
    lbl_title.pack(pady=80)

    def seleccionar_pdf():
        filename = filedialog.askopenfilename(
            title="Selecciona el archivo PDF de preguntas",
            filetypes=[("Archivos PDF", "*.pdf")])
        if filename:
            preguntas = leer_pdf(filename)
            if preguntas:
                root_menu.withdraw()
                iniciar_examen(preguntas, root_menu, root_menu)
            else:
                messagebox.showerror("Error", "No se encontraron preguntas válidas en el archivo.")

    btn_select = tk.Button(root_menu, text="Seleccionar PDF", width=30, height=3, bg="#2196F3", fg="white", font=font_button, command=seleccionar_pdf)
    btn_select.pack(pady=40)

    btn_stats = tk.Button(
        root_menu,
        text="Ver estadísticas",
        width=30,
        height=3,
        bg="#3F51B5",
        fg="white",
        font=font_button,
        command=estadisticas.mostrar_estadisticas_globales
    )
    btn_stats.pack(pady=10)

    def cerrar_todo_menu(event=None):
        try:
            root_menu.quit()
        except Exception:
            pass
        try:
            root_menu.destroy()
        except Exception:
            pass
        import os
        os._exit(0)

    btn_exit = tk.Button(root_menu, text="Salir", width=20, height=2, bg="#f44336", fg="white", font=font_button, command=cerrar_todo_menu)
    btn_exit.pack(side="bottom", pady=40)

    root_menu.protocol("WM_DELETE_WINDOW", cerrar_todo_menu)

    import signal
    def signal_handler_menu(sig, frame):
        cerrar_todo_menu()
    signal.signal(signal.SIGINT, signal_handler_menu)

    root_menu.mainloop()

if __name__ == "__main__":
    menu_principal()
