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

    container.grid_columnconfigure((0, 1), weight=1)
    container.grid_rowconfigure(0, weight=1)

    left = ctk.CTkFrame(container, fg_color="#1f6aa5", corner_radius=20)
    left.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(left, text="Bem Vindo!", font=("Arial", 34, "bold"), text_color="white").pack(pady=(120, 10))

    ctk.CTkLabel(left, text="Sistema Desktop/Profissional", font=("Arial", 18), text_color="white").pack()

    ctk.CTkLabel(left, text="Faça login para continuar", font=("Arial", 14), text_color="white").pack(pady=(10))

    right = ctk.CTkFrame(container, fg_color="white", corner_radius=20)
    right.grid(row=0, column=1, sticky="nsew")

    ctk.CTkLabel(left, text="LOGIN", font=("Arial", 30, "bold"), text_color="#1f6aa5").pack(pady=(120, 10))

    usuario=ctk.CTkEntry(right, placeholder_text="Usuário", width=280, heigth=45)
    usuario.pack(pady=10)

    senha_frame=ctk.CTkFrame(right, fg_color="transparent")
    senha_frame.pack(pady=10)

    senha=ctk.CTkEntry(senha_frame, placeholder_text="Senha", show="*", width=280, heigth=45)
    senha.pack(side="left", padx=(0, 5))

    def autenticar():
        user = usuario.get()
        pwd = senha.get()

        if user in usuarios and usuarios[user]["senha"] == pwd:
            abrir_dashboard(usuarios[user]["tipo"])
        else:
            erro.configure(text="Usuario ou senha invalidos")
    
    ctk.CTkButton(right, text="Entrar", width=280, height=45, font=("Arial", 16), command=autenticar).pack(pady=30)

    erro = ctk.CTkLabel(right, text="", text_color="red")
    erro.pack()

    def abrir_dashboard(tipo):
        limpar_tela()
        
        container = ctk.CTkFrame(app)
        container.pack(expand=True, fill="both")

        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

    sidebar = ctk.CTkFrame(container, fg_color="#1f6aa5")
    sidebar.grid(row=0, column=0)

    ctk.CTkLabel(sidebar, text="MENU", font=("Arial", 22, "bold"), text_color="white").pack(pady=30)

    content = ctk.CTkFrame(container, fg_color="white")
    content.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
    