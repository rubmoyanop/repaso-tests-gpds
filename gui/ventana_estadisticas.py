import tkinter as tk
from tkinter import messagebox, Toplevel, Button, Frame, LabelFrame, Label, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

def mostrar_info_general(tab, total_preg, total_int, total_fal, tasa_global):
    frame_info = LabelFrame(tab, text="Información general")
    frame_info.pack(fill="x", padx=10, pady=10)
    Label(frame_info, text=f"Preguntas únicas: {total_preg}", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
    Label(frame_info, text=f"Total de intentos: {total_int}", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
    Label(frame_info, text=f"Total fallos: {total_fal}", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
    Label(frame_info, text=f"Tasa de fallos: {tasa_global:.1f}%", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5, sticky="w")

def grafico_pastel(tab, total_int, total_fal):
    fig, ax = plt.subplots(figsize=(5, 4))
    labels = ['Aciertos', 'Fallos']
    sizes = [total_int - total_fal, total_fal]
    colors = ['#4CAF50', '#f44336']
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

def treeview(tab, cols, vsb):
    tree = ttk.Treeview(tab, columns=cols, show="headings", yscrollcommand=vsb.set)
    vsb.config(command=tree.yview)
    for col in cols:
        tree.heading(col, text=col)
        if col == "Pregunta":
            tree.column(col, anchor="w", width=350)
        elif col == "Cuestionario":
            tree.column(col, anchor="w", width=120)
        else:
            tree.column(col, anchor="center", width=110)
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    return tree

def grafico_barras(tab, names, values, color, xlabel, ylabel, title, ylim=None, value_fmt=None):
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(names, values, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if ylim:
        ax.set_ylim(*ylim)
    for bar, val in zip(bars, values):
        height = bar.get_height()
        label = value_fmt(val) if value_fmt else f'{val:.1f}'
        ax.text(bar.get_x() + bar.get_width()/2., height + 1, label, ha='center', va='bottom', rotation=0)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

def grafico_lineas(tab, dates, rates, title):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(dates, rates, marker='o', linestyle='-', color='#4CAF50')
    ax.set_xlabel('Fecha y Hora')
    ax.set_ylabel('Tasa de Éxito (%)')
    ax.set_title(title)
    ax.set_ylim(0, 100)
    fig.autofmt_xdate()
    plt.xticks(rotation=45)
    if len(rates) > 1:
        z = np.polyfit(range(len(dates)), rates, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(range(len(dates))), "r--", alpha=0.7)
    plt.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=tab)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
