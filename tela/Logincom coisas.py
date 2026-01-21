import customtkinter as ctk
from PIL import Image
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

usuarios = {
    "admin": {"senha": "123", "tipo": "admin"},
    "usuario": {"senha": "123", "tipo": "usuario"}
}

app = ctk.CTk()
app.title("Sistema desktop")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()
# app.geometry(f"{largura}x{altura}")
app.geometry(f"1000x600")

def limpar_tela():
    for widget in app.winfo_children():
        widget.destroy()

def tela_login():
    limpar_tela()

    container = ctk.CTkFrame(app, corner_radius=20)
    container.pack(expand=True, fill="both", padx=40, pady=40)