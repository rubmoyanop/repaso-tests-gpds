import json
import os
from tkinter import messagebox, Toplevel, Button, Frame, LabelFrame, Label
from tkinter import ttk
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import numpy as np 
import tkinter as tk

STATS_FILE = os.path.join(os.path.dirname(__file__), 'stats.json')

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {}
    with open(STATS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_stats(stats):
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def update_stats(pregunta, correcta, categoria="General", tiempo=0, sesion_id=None, archivo=None):
    """
    Actualiza estadísticas de una pregunta.
    
    Args:
        pregunta: Texto de la pregunta
        correcta: Si la respuesta fue correcta
        categoria: Categoría de la pregunta (será sobreescrita si se proporciona archivo)
        tiempo: Tiempo en segundos que tardó en responder
        sesion_id: ID de la sesión actual
        archivo: Ruta al archivo PDF de donde procede la pregunta
    """
    stats = load_stats()
    key = pregunta.strip()
    
    if archivo:
        categoria = os.path.splitext(os.path.basename(archivo))[0]
    
    if key not in stats:
        stats[key] = {
            "intentos": 0, 
            "fallos": 0,
            "categoria": categoria,
            "tiempos": [],
            "historial": [],
            "origen_archivo": archivo
        }
    
    # Actualizar intentos y fallos
    entry = stats[key]
    entry["intentos"] += 1
    if not correcta:
        entry["fallos"] += 1
    
    # Actualizar la categoría si se proporciona un archivo nuevo
    if archivo and not entry.get("origen_archivo"):
        entry["origen_archivo"] = archivo
        entry["categoria"] = categoria
    
    # Guarda el tiempo de respuesta
    entry["tiempos"].append(round(tiempo, 2))
    
    # Guarda historial de respuestas
    entry["historial"].append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "correcta": correcta,
        "tiempo": round(tiempo, 2),
        "sesion_id": sesion_id,
        "archivo": archivo
    })
    
    stats[key] = entry
    save_stats(stats)

def get_most_failed(top_n=5):
    stats = load_stats()
    items = [(q, data["fallos"], data["intentos"], data.get("categoria", "General"), 
              sum(data.get("tiempos", [0])) / len(data.get("tiempos", [1])) if data.get("tiempos") else 0) 
             for q, data in stats.items()]
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top_n]

def get_stats_by_category():
    stats = load_stats()
    by_cuestionario = {}
    
    for q, data in stats.items():
        cuestionario = data.get("categoria", "General")
        if cuestionario not in by_cuestionario:
            by_cuestionario[cuestionario] = {"intentos": 0, "fallos": 0, "preguntas": 0}
        
        by_cuestionario[cuestionario]["intentos"] += data["intentos"]
        by_cuestionario[cuestionario]["fallos"] += data["fallos"]
        by_cuestionario[cuestionario]["preguntas"] += 1
        
    return by_cuestionario

def get_trend_data(last_n_sessions=10):
    stats = load_stats()
    
    # Recoge todos los IDs de sesión y ordenarlos
    all_sessions = set()
    for q, data in stats.items():
        for entry in data.get("historial", []):
            if "sesion_id" in entry:
                all_sessions.add(entry["sesion_id"])
    
    sessions_list = sorted(list(all_sessions))
    if last_n_sessions > 0:
        sessions_list = sessions_list[-last_n_sessions:]
    
    # Calcular rendimiento por sesión
    trend_data = []
    for sesion_id in sessions_list:
        session_stats = {"correctas": 0, "total": 0, "fecha": "", "timestamp": ""}
        
        for q, data in stats.items():
            for entry in data.get("historial", []):
                if entry.get("sesion_id") == sesion_id:
                    session_stats["total"] += 1
                    if entry.get("correcta"):
                        session_stats["correctas"] += 1
                    
                    # Solo tomamos la fecha y hora una vez
                    if not session_stats["fecha"]:
                        session_stats["fecha"] = entry.get("fecha", "")[:10]  # Solo la fecha para mostrar
                        session_stats["timestamp"] = entry.get("fecha", "")  # Fecha completa con hora
        
        if session_stats["total"] > 0:
            session_stats["tasa"] = round(session_stats["correctas"] / session_stats["total"] * 100, 1)
            trend_data.append(session_stats)
    
    return trend_data

def mostrar_estadisticas_globales():
    stats = load_stats()
    if not stats:
        messagebox.showinfo("Estadísticas globales", "Aún no hay datos de estadísticas.")
        return

    win = Toplevel()
    win.title("Estadísticas globales de preparación")
    win.geometry("1000x700")
    
    # Notebook (pestañas)
    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Tab 1: Resumen general
    tab_resumen = ttk.Frame(notebook)
    notebook.add(tab_resumen, text="Resumen")
    
    # Tab 2: Preguntas problemáticas
    tab_preguntas = ttk.Frame(notebook)
    notebook.add(tab_preguntas, text="Preguntas difíciles")
    
    # Tab 3: Cuestionarios
    tab_cuestionarios = ttk.Frame(notebook)
    notebook.add(tab_cuestionarios, text="Cuestionarios")
    
    # Tab 4: Progreso
    tab_progreso = ttk.Frame(notebook)
    notebook.add(tab_progreso, text="Progreso")
    
    # Tab 5: Tiempos
    tab_tiempos = ttk.Frame(notebook)
    notebook.add(tab_tiempos, text="Tiempos")
    
    # ---- RESUMEN ----
    total_preg = len(stats)
    total_int = sum(d["intentos"] for d in stats.values())
    total_fal = sum(d["fallos"] for d in stats.values())
    tasa_global = (total_fal / total_int * 100) if total_int else 0
    
    # Frame para info general
    frame_info = LabelFrame(tab_resumen, text="Información general")
    frame_info.pack(fill="x", padx=10, pady=10)
    
    Label(frame_info, text=f"Preguntas únicas: {total_preg}", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    Label(frame_info, text=f"Total de intentos: {total_int}", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    Label(frame_info, text=f"Total fallos: {total_fal}", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    Label(frame_info, text=f"Tasa de fallos: {tasa_global:.1f}%", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="w")
    
    # Gráfico de pastel para aciertos/fallos
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = ['Aciertos', 'Fallos']
    sizes = [total_int - total_fal, total_fal]
    colors = ['#4CAF50', '#f44336']
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Para que sea un círculo
    canvas = FigureCanvasTkAgg(fig, master=tab_resumen)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    
    # ---- PREGUNTAS PROBLEMÁTICAS ----
    items = []
    for q, data in stats.items():
        intentos = data["intentos"]
        fallos = data["fallos"]
        cuestionario = data.get("categoria", "General")
        tiempo_medio = sum(data.get("tiempos", [0])) / len(data.get("tiempos", [1])) if data.get("tiempos") else 0
        tasa = (fallos / intentos * 100) if intentos else 0
        items.append((q, cuestionario, intentos, fallos, tasa, tiempo_medio))
    items.sort(key=lambda x: (-x[4], -x[2]))

    # --- Selector de número de preguntas a mostrar ---
    frame_selector = Frame(tab_preguntas)
    frame_selector.pack(fill="x", padx=10, pady=(10, 0), anchor="w")
    Label(frame_selector, text="Mostrar:", font=("Helvetica", 11)).pack(side="left")
    num_preg_var = tk.IntVar(value=10)
    spin = ttk.Spinbox(frame_selector, from_=1, to=max(1, len(items)), width=5, textvariable=num_preg_var)
    spin.pack(side="left", padx=5)
    Label(frame_selector, text="preguntas", font=("Helvetica", 11)).pack(side="left")

    vsb = ttk.Scrollbar(tab_preguntas, orient="vertical")
    vsb.pack(side="right", fill="y")

    cols = ("Pregunta", "Cuestionario", "Intentos", "Fallos", "% Fallos", "Tiempo medio (s)")
    tree = ttk.Treeview(tab_preguntas, columns=cols, show="headings", yscrollcommand=vsb.set)
    vsb.config(command=tree.yview)

    for col in cols:
        tree.heading(col, text=col)
        if col == "Pregunta":
            tree.column(col, anchor="w", width=350)
        elif col == "Cuestionario":
            tree.column(col, anchor="w", width=120)
        else:
            tree.column(col, anchor="center", width=110)

    def actualizar_lista_preguntas(*args):
        tree.delete(*tree.get_children())
        try:
            n = int(num_preg_var.get())
        except Exception:
            n = 10  # valor por defecto si el spinbox está vacío o no es válido
        n = max(1, min(n, len(items)))
        for q, cuestionario, intentos, fallos, tasa, tiempo_medio in items[:n]:
            texto_q = q if len(q) < 60 else q[:57] + "..."
            tree.insert(
                "", "end",
                values=(
                    texto_q,
                    cuestionario,
                    intentos,
                    fallos,
                    f"{tasa:.1f}%",
                    f"{tiempo_medio:.1f}"
                )
            )

    num_preg_var.trace_add("write", actualizar_lista_preguntas)
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    actualizar_lista_preguntas()

    def mostrar_detalle(event):
        item_id = tree.focus()
        if not item_id:
            return
        vals = tree.item(item_id, "values")
        pregunta_texto = vals[0]
        for q, cuestionario, intentos, fallos, tasa, tiempo_medio in items:
            if (q if len(q) < 60 else q[:57] + "...") == pregunta_texto:
                detalles = stats[q]
                historial = detalles.get("historial", [])
                detalle_str = f"Pregunta:\n{q}\n\n"
                detalle_str += f"Cuestionario: {cuestionario}\nIntentos: {intentos}\nFallos: {fallos}\nTasa de fallos: {tasa:.1f}%\nTiempo medio: {tiempo_medio:.1f}s\n\n"
                detalle_str += "Historial:\n"
                for h in historial[-5:]:
                    detalle_str += f"- {h['fecha']} | {'✔' if h['correcta'] else '✘'} | {h['tiempo']}s\n"
                messagebox.showinfo("Detalle de pregunta", detalle_str)
                break

    tree.bind("<Double-1>", mostrar_detalle)
    
    # ---- CUESTIONARIOS ----
    cuestionarios = get_stats_by_category()
    
    if cuestionarios:
        cuestionario_names = list(cuestionarios.keys())
        if cuestionario_names != sorted(cuestionario_names):
            # Si no están ordenados, los ordenamos
            cuestionarios = {k: cuestionarios[k] for k in sorted(cuestionarios.keys())}
            cuestionario_names = list(cuestionarios.keys())
        
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        # Usar la lista ordenada
        success_rates = [(cuestionarios[name]["intentos"] - cuestionarios[name]["fallos"]) / cuestionarios[name]["intentos"] * 100 if cuestionarios[name]["intentos"] > 0 else 0 for name in cuestionario_names]
        
        bars = ax2.bar(cuestionario_names, success_rates, color='#2196F3')
        
        ax2.set_xlabel('Cuestionario')
        ax2.set_ylabel('Tasa de Éxito (%)')
        ax2.set_title('Tasa de Éxito por Cuestionario')
        ax2.set_ylim(0, 100)
        
        for bar, val in zip(bars, success_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{val:.1f}%', ha='center', va='bottom', rotation=0)
        
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        canvas2 = FigureCanvasTkAgg(fig2, master=tab_cuestionarios)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, pady=10)
        
        frame_details = Frame(tab_cuestionarios)
        frame_details.pack(fill="both", expand=True, padx=10, pady=10)
        
        cols2 = ("Cuestionario", "Preguntas", "Intentos", "Fallos", "Tasa de Fallos")
        tree2 = ttk.Treeview(frame_details, columns=cols2, show="headings")
        
        for col in cols2:
            tree2.heading(col, text=col)
            tree2.column(col, anchor="w", width=120)
        
        # Insertar en orden alfabético
        for cuestionario in cuestionario_names:
            data = cuestionarios[cuestionario]
            tasa = (data["fallos"] / data["intentos"] * 100) if data["intentos"] > 0 else 0
            tree2.insert("", "end", values=(cuestionario, data["preguntas"], data["intentos"], data["fallos"], f"{tasa:.1f}%"))
        
        tree2.pack(fill="both", expand=True)
    
    # ---- PROGRESO ----
    trend_data = get_trend_data()
    
    if trend_data:
        fig3, ax3 = plt.subplots(figsize=(8, 6))
        
        # Usamos las timestamps completas para el eje X
        dates = [td.get("timestamp", td["fecha"]) for td in trend_data]
        rates = [td["tasa"] for td in trend_data]
        
        ax3.plot(dates, rates, marker='o', linestyle='-', color='#4CAF50')
        ax3.set_xlabel('Fecha y Hora')
        ax3.set_ylabel('Tasa de Éxito (%)')
        ax3.set_title('Evolución del Rendimiento')
        ax3.set_ylim(0, 100)
        
        # Formato de fecha más detallado
        fig3.autofmt_xdate()  # Rota automáticamente las etiquetas para mejor visualización
        plt.xticks(rotation=45)
        
        # Añadir línea de tendencia
        if len(trend_data) > 1:
            z = np.polyfit(range(len(dates)), rates, 1)
            p = np.poly1d(z)
            ax3.plot(dates, p(range(len(dates))), "r--", alpha=0.7)
        
        plt.tight_layout()
        
        canvas3 = FigureCanvasTkAgg(fig3, master=tab_progreso)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True, pady=10)
    
    # ---- TIEMPOS ----
    # Recopilar datos de tiempo
    tiempo_por_cat = {}
    for q, data in stats.items():
        cat = data.get("categoria", "General")
        if cat not in tiempo_por_cat:
            tiempo_por_cat[cat] = []
        
        tiempo_por_cat[cat].extend(data.get("tiempos", []))
    
    if tiempo_por_cat:
        # Calcular tiempos medios
        cats = list(tiempo_por_cat.keys())
        if cats != sorted(cats):
            cats = sorted(cats)
        tiempos_medios = {cat: sum(tiempo_por_cat[cat])/len(tiempo_por_cat[cat]) if tiempo_por_cat[cat] else 0 for cat in cats}
        
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        times = list(tiempos_medios.values())
        
        bars2 = ax4.bar(cats, times, color='#FF9800')
        
        ax4.set_xlabel('Categoría')
        ax4.set_ylabel('Tiempo medio (seg)')
        ax4.set_title('Tiempo de respuesta por categoría')
        
        for bar, val in zip(bars2, times):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{val:.1f}s', ha='center', va='bottom', rotation=0)
        
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        
        canvas4 = FigureCanvasTkAgg(fig4, master=tab_tiempos)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill="both", expand=True, pady=10)
    
    # Botón para cerrar
    Button(win, text="Cerrar", command=win.destroy, bg="#f44336", fg="white",
           font=("Helvetica", 12), width=10).pack(pady=10)
