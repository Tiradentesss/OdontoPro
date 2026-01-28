import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# -----------------------------
# MOCK DE USUÁRIOS (FUTURO BANCO)
# -----------------------------
usuarios = {
    "admin": {"senha": "123", "tipo": "admin"},
}

app = ctk.CTk()
app.title("Sistema Desktop OdontoPro")
app.geometry("1200x700")


# =============================
# UTIL
# =============================
def limpar_tela():
    for w in app.winfo_children():
        w.destroy()


# =============================
# LOGIN
# =============================
def tela_login():
    limpar_tela()

    container = ctk.CTkFrame(app, corner_radius=20)
    container.pack(expand=True, fill="both", padx=40, pady=40)
    container.grid_columnconfigure((0, 1), weight=1)

    left = ctk.CTkFrame(container, fg_color="#1f6aa5")
    left.grid(row=0, column=0, sticky="nsew")

    ctk.CTkLabel(left, text="Bem-vindo!", font=("Arial", 34, "bold"), text_color="white").pack(pady=(150, 10))
    ctk.CTkLabel(left, text="Sistema Profissional", font=("Arial", 18), text_color="white").pack()

    right = ctk.CTkFrame(container, fg_color="white")
    right.grid(row=0, column=1, sticky="nsew")

    ctk.CTkLabel(right, text="LOGIN", font=("Arial", 30, "bold"), text_color="#1f6aa5").pack(pady=(120, 30))

    usuario = ctk.CTkEntry(right, placeholder_text="Usuário", width=300, height=45)
    usuario.pack(pady=10)

    senha = ctk.CTkEntry(right, placeholder_text="Senha", show="*", width=300, height=45)
    senha.pack(pady=10)

    erro = ctk.CTkLabel(right, text="", text_color="red")
    erro.pack()

    def autenticar():
        u = usuario.get()
        s = senha.get()

        if u in usuarios and usuarios[u]["senha"] == s:
            abrir_dashboard(usuarios[u]["tipo"])
        else:
            erro.configure(text="Usuário ou senha inválidos")

    ctk.CTkButton(right, text="Entrar", width=300, height=45, font=("Arial", 16), command=autenticar).pack(pady=30)


# =============================
# DASHBOARD
# =============================
def abrir_dashboard(tipo):
    limpar_tela()

    container = ctk.CTkFrame(app)
    container.pack(expand=True, fill="both")
    container.grid_columnconfigure(1, weight=1)

    # SIDEBAR
    sidebar = ctk.CTkFrame(container, fg_color="#1f6aa5", width=220)
    sidebar.grid(row=0, column=0, sticky="ns")

    ctk.CTkLabel(sidebar, text="OdontoPro", font=("Arial", 22, "bold"), text_color="white").pack(pady=30)

    # CONTEÚDO
    content = ctk.CTkFrame(container, fg_color="#f4f7fe")
    content.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

    def trocar_tela(func):
        for w in content.winfo_children():
            w.destroy()
        func()

    # =============================
    # TELAS
    # =============================
    def tela_inicio():
        ctk.CTkLabel(content, text="Dashboard", font=("Arial", 32, "bold")).pack(pady=40)

    def tela_consultas():
        frame = ctk.CTkFrame(content, corner_radius=20, fg_color="white")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text="Consultas da Semana", font=("Arial", 24, "bold")).pack(pady=20)

        tabela = ctk.CTkFrame(frame, fg_color="transparent")
        tabela.pack(fill="x", padx=20)

        headers = ["Paciente", "Data", "Horário", "Status"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(tabela, text=h, font=("Arial", 16, "bold")).grid(row=0, column=i, padx=15, pady=10)

        consultas = [
            ("Victor Araújo", "14/12/2025", "09:30", "Confirmado"),
            ("Natália Silva", "15/12/2025", "12:00", "Não confirmado"),
            ("Ronald Richards", "18/12/2025", "08:00", "Reagendado"),
        ]

        cores = {
            "Confirmado": "#2ecc71",
            "Não confirmado": "#e74c3c",
            "Reagendado": "#3498db"
        }

        for r, c in enumerate(consultas, start=1):
            for i, v in enumerate(c):
                if i == 3:
                    ctk.CTkLabel(
                        tabela, text=v, text_color=cores[v],
                        fg_color=cores[v] + "33", corner_radius=8
                    ).grid(row=r, column=i, padx=15, pady=8)
                else:
                    ctk.CTkLabel(tabela, text=v).grid(row=r, column=i, padx=15, pady=8)

    # =============================
    # BOTÕES SIDEBAR
    # =============================
    def botao(texto, comando):
        ctk.CTkButton(
            sidebar, text=texto,
            fg_color="#1f6aa5", hover_color="#174f7d",
            text_color="white", height=45,
            command=lambda: trocar_tela(comando)
        ).pack(fill="x", padx=20, pady=6)

    botao("Início", tela_inicio)
    botao("Consultas", tela_consultas)
    botao("Sair", tela_login)

    tela_inicio()


# START
tela_login()
app.mainloop()