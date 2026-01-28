import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

# =============================
# CONFIGURAÇÕES GERAIS
# =============================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# =============================
# MOCK DE DADOS
# =============================
usuarios = {"admin": {"senha": "123", "nome": "Lucas"}}

consultas_data = [
    ("Victor Araújo", "14/12/2025", "09:30", "Confirmado"),
    ("Natália Silva", "15/12/2025", "12:00", "Não Confirmado"),
    ("Ronald Richards", "18/12/2025", "08:00", "Reagendado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
]

LIMITE_CONSULTAS = 10

# =============================
# CORES
# =============================
COLOR_BG = "#F0F2F5"
COLOR_SIDEBAR = "#FFFFFF"
COLOR_TEXT = "#2D3436"
COLOR_TEXT_MUTED = "#A0AEC0"
COLOR_ACCENT = "#00B4D8"

STATUS_COLORS = {
    "Confirmado": {"text": "#1ABC9C", "bg": "#D1F2EB"},
    "Não Confirmado": {"text": "#E74C3C", "bg": "#FADBD8"},
    "Reagendado": {"text": "#3498DB", "bg": "#D6EAF8"}
}

# =============================
# APP
# =============================
class OdontoProApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("OdontoPro")
        self.geometry("1280x800")
        self.configure(fg_color=COLOR_BG)

        self.aba_atual = "Agendamento"
        self.pagina_consultas_atual = 0
        self.tela_login()

    def limpar_tela(self):
        for w in self.winfo_children():
            w.destroy()

    # =============================
    # LOGIN (NOVO ESTILO)
    # =============================
    def tela_login(self):
        self.limpar_tela()

        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self, fg_color="#D1D1D1", corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(left, text="[ IMAGEM LATERAL ]", font=("Arial", 18)).pack(expand=True)

        right = ctk.CTkFrame(self, fg_color="#F2F2F2", corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew", padx=60)

        ctk.CTkLabel(right, text="[ LOGO AQUI ]", font=("Arial", 14, "bold"), text_color="#0056b3").pack(anchor="w", pady=(60, 30))
        ctk.CTkLabel(right, text="Faça Login com sua conta", font=("Inter", 28, "bold")).pack(anchor="w")
        ctk.CTkLabel(right, text="Digite seu usuário e senha", font=("Inter", 14), text_color="#666").pack(anchor="w", pady=(0, 30))

        ctk.CTkLabel(right, text="Usuário").pack(anchor="w")
        self.ent_user = ctk.CTkEntry(right, height=45, fg_color="white")
        self.ent_user.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(right, text="Senha").pack(anchor="w")
        self.ent_pass = ctk.CTkEntry(right, show="*", height=45, fg_color="white")
        self.ent_pass.pack(fill="x", pady=(5, 20))

        ctk.CTkButton(
            right, text="Entrar na conta",
            height=50, fg_color=COLOR_ACCENT,
            font=("Inter", 14, "bold"),
            command=self.autenticar
        ).pack(fill="x")

    def autenticar(self):
        u = self.ent_user.get()
        s = self.ent_pass.get()
        if u in usuarios and usuarios[u]["senha"] == s:
            self.abrir_dashboard(usuarios[u]["nome"])
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos")

    # =============================
    # DASHBOARD
    # =============================
    def abrir_dashboard(self, nome):
        self.limpar_tela()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="🦷 OdontoPro", font=("Arial", 24, "bold"), text_color=COLOR_ACCENT).pack(pady=40)

        self.menu = [
            ("Painel", "🏠"),
            ("Agendamento", "📅"),
            ("Meus Pacientes", "👥"),
            ("Relatório", "📊"),
            ("Mensagens", "💬"),
            ("Configuração", "⚙️"),
        ]

        self.menu_buttons = {}
        for nome_item, icon in self.menu:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {nome_item}",
                anchor="w",
                height=45,
                fg_color="transparent",
                text_color=COLOR_TEXT_MUTED,
                hover_color="#E0F7FA",
                command=lambda n=nome_item: self.mudar_aba(n)
            )
            btn.pack(fill="x", padx=20, pady=4)
            self.menu_buttons[nome_item] = btn

        ctk.CTkButton(
            self.sidebar, text="⬅️ Sair",
            fg_color="transparent",
            text_color=COLOR_TEXT_MUTED,
            command=self.tela_login
        ).pack(side="bottom", pady=30)

        self.content_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=20)

        self.mudar_aba("Agendamento")

    # =============================
    # NAVEGAÇÃO
    # =============================
    def mudar_aba(self, aba):
        self.aba_atual = aba
        for nome, btn in self.menu_buttons.items():
            ativo = nome == aba
            btn.configure(
                fg_color="#E0F7FA" if ativo else "transparent",
                text_color=COLOR_ACCENT if ativo else COLOR_TEXT_MUTED,
                font=("Arial", 14, "bold" if ativo else "normal")
            )

        for w in self.content_frame.winfo_children():
            w.destroy()

        {
            "Painel": self.render_painel,
            "Agendamento": self.render_agendamento,
            "Meus Pacientes": self.render_pacientes,
            "Relatório": self.render_relatorio,
            "Mensagens": self.render_mensagens,
            "Configuração": self.render_config
        }[aba]()

    # =============================
    # ABAS
    # =============================
    def trocar_pagina_consultas(self, pagina):
        self.pagina_consultas_atual = pagina
        self.mudar_aba("Agendamento")


    def render_painel(self):
        ctk.CTkLabel(self.content_frame, text="Painel Geral", font=("Arial", 28, "bold")).pack(anchor="w")

    def render_agendamento(self):
        card = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=20)
        card.pack(fill="both", expand=True)

        # Título
        ctk.CTkLabel(
            card,
            text="Consultas da Semana",
            font=("Arial", 22, "bold"),
            text_color=COLOR_TEXT
        ).pack(anchor="w", padx=30, pady=(30, 20))

        # ---------- TABELA ----------
        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="both", expand=True)

        headers = ["Nome do Paciente", "Data", "Horário", "Status"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=h,
                font=("Arial", 13),
                text_color=COLOR_TEXT_MUTED
            ).grid(row=0, column=i, sticky="w", padx=30, pady=10)

        inicio = self.pagina_consultas_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados = consultas_data[inicio:fim]

        for r, (p, d, h, s) in enumerate(dados, start=1):
            ctk.CTkLabel(table, text=p, font=("Arial", 14, "bold")).grid(row=r, column=0, sticky="w", padx=30, pady=15)
            ctk.CTkLabel(table, text=d).grid(row=r, column=1, sticky="w", padx=30)
            ctk.CTkLabel(table, text=h).grid(row=r, column=2, sticky="w", padx=30)

            status_info = STATUS_COLORS[s]
            badge = ctk.CTkFrame(table, fg_color=status_info["bg"], corner_radius=6)
            badge.grid(row=r, column=3, sticky="w", padx=30)

            ctk.CTkLabel(
                badge,
                text=s,
                font=("Arial", 11, "bold"),
                text_color=status_info["text"],
                padx=10,
                pady=3
            ).pack()

        # ---------- PAGINAÇÃO ----------
        pag_frame = ctk.CTkFrame(card, fg_color="transparent")
        pag_frame.pack(anchor="e", padx=30, pady=20)

        total_paginas = (len(consultas_data) + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS

        def botao_pagina(texto, ativo=False, comando=None):
            return ctk.CTkButton(
                pag_frame,
                text=texto,
                width=32,
                height=32,
                corner_radius=6,
                fg_color=COLOR_ACCENT if ativo else "#F0F2F5",
                text_color="white" if ativo else COLOR_TEXT_MUTED,
                hover_color=COLOR_ACCENT,
                command=comando
            )
        
        # ‹ Anterior
        if self.pagina_consultas_atual > 0:
            botao_pagina("‹", comando=lambda: self.trocar_pagina_consultas(self.pagina_consultas_atual - 1)).pack(side="left", padx=4)

        for i in range(total_paginas):
            ativo = i == self.pagina_consultas_atual
            botao_pagina(
                str(i + 1),
                ativo=ativo,
                comando=lambda idx=i: self.trocar_pagina_consultas(idx)
            ).pack(side="left", padx=4)

        # › Próximo
        if self.pagina_consultas_atual < total_paginas - 1:
            botao_pagina("›", comando=lambda: self.trocar_pagina_consultas(self.pagina_consultas_atual + 1)).pack(side="left", padx=4)


    def render_pacientes(self):
        ctk.CTkLabel(self.content_frame, text="Meus Pacientes", font=("Arial", 28, "bold")).pack(anchor="w")

    def render_relatorio(self):
        ctk.CTkLabel(self.content_frame, text="Relatórios", font=("Arial", 28, "bold")).pack(anchor="w")

    def render_mensagens(self):
        ctk.CTkLabel(self.content_frame, text="Mensagens", font=("Arial", 28, "bold")).pack(anchor="w")

    def render_config(self):
        ctk.CTkLabel(self.content_frame, text="Configurações", font=("Arial", 28, "bold")).pack(anchor="w")


if __name__ == "__main__":
    app = OdontoProApp()
    app.mainloop()
