import customtkinter as ctk
from PIL import Image
import os

# ================= MOCK LOGIN =================

USUARIOS = {
    "admin": {"senha": "123", "nome": "Lucas"},
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ================= MOCK AGENDA =================

CONSULTAS_DATA = [
    ("Victor Araújo", "14/12/2025", "09:30", "Confirmado"),
    ("Natália Silva", "15/12/2025", "12:00", "Não Confirmado"),
    ("Ronald Richards", "18/12/2025", "08:00", "Reagendado"),
    ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
    ("Camila Rocha", "17/12/2025", "10:00", "Confirmado"),
    ("Felipe Andrade", "18/12/2025", "15:30", "Não Confirmado"),
    ("Ana Paula", "19/12/2025", "09:00", "Confirmado"),
    ("Lucas Lima", "19/12/2025", "13:00", "Reagendado"),
    ("João Pedro", "20/12/2025", "08:30", "Confirmado"),
    ("Mariana Alves", "20/12/2025", "14:00", "Confirmado"),
    ("Carlos Eduardo", "21/12/2025", "11:00", "Não Confirmado"),
]

LIMITE_CONSULTAS = 6

STATUS_COLORS = {
    "Confirmado": {"text": "#22C55E", "bg": "#DCFCE7"},
    "Não Confirmado": {"text": "#EF4444", "bg": "#FEE2E2"},
    "Reagendado": {"text": "#0EA5E9", "bg": "#E0F2FE"},
}


class App(ctk.CTk):
    def __init__(self, usuario_nome="Usuário"):
        super().__init__()

        self.usuario_nome = usuario_nome


        self.title("OdontoPro - Sistema de Gerenciamento")
        self.geometry("1150x750")
        self.minsize(1000, 650)
        self.configure(fg_color="#F5F6FA")

        # Grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= Sidebar =================
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E5E7EB"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Nome
        ctk.CTkLabel(
            self.sidebar,
            text="OdontoPro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#0d99c7"
        ).pack(pady=(40, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="Clinical Management",
            font=ctk.CTkFont(size=11),
            text_color="#9CA3AF"
        ).pack(pady=(0, 30))

        # Menu
        self.buttons = {}
        self.menu_items = [
            ("▣  Painel", "painel"),
            ("🗓  Agenda", "agenda"),
            ("👤  Pacientes", "pacientes"),
            ("💰  Financeiro", "financeiro"),
            ("⚙  Configurações", "config"),
        ]

        for text, name in self.menu_items:
            self.buttons[name] = self.create_menu_button(text, name)

        # Sair
        ctk.CTkButton(
            self.sidebar,
            text="⎋  Sair do Sistema",
            fg_color="transparent",
            text_color="#EF4444",
            hover_color="#FEE2E2",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.quit
        ).pack(side="bottom", fill="x", padx=20, pady=30)

        # ================= Área Principal =================
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        self.frames = {
            "painel": Painel(self.container),
            "agenda": Agenda(self.container),
            "pacientes": Pacientes(self.container),
            "financeiro": Financeiro(self.container),
            "config": Configuracoes(self.container),
        }

        self.current_frame = None
        self.show_frame("painel")

    def create_menu_button(self, text, name):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            fg_color="transparent",
            text_color="#4B5563",
            hover_color="#F0F9FF",
            height=46,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            command=lambda: self.show_frame(name)
        )
        btn.pack(fill="x", padx=16, pady=6)
        return btn

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.pack_forget()

        self.current_frame = self.frames[name]
        self.current_frame.pack(expand=True, fill="both")
        self.update_active_button(name)

    def update_active_button(self, active):
        for name, btn in self.buttons.items():
            if name == active:
                btn.configure(
                    fg_color="#0d99c7",
                    text_color="white",
                    hover_color="#0b86af"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#4B5563",
                    hover_color="#F0F9FF"
                )


# ================= BASE DAS TELAS =================

class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F2937"
        ).pack(anchor="w", pady=(0, 20))

        self.content_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=18,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.content_card.pack(expand=True, fill="both")


# ================= TELAS =================

class Painel(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Painel")

        dashboard = ctk.CTkFrame(self.content_card, fg_color="transparent")
        dashboard.pack(expand=True, fill="both", padx=25, pady=25)

        dashboard.grid_columnconfigure((0, 1), weight=1)

        # ---- Próximas Consultas ----
        consultas = ctk.CTkFrame(
            dashboard,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        consultas.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        ctk.CTkLabel(
            consultas,
            text="Próximas Consultas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)

        dados = [
            ("Victor Araújo", "Hoje • 09:00"),
            ("Natália Silva", "Hoje • 12:00"),
            ("Hugo Pontes", "Hoje • 14:30"),
        ]

        for nome, horario in dados:
            row = ctk.CTkFrame(consultas, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)

            ctk.CTkLabel(row, text=nome, font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            ctk.CTkLabel(row, text=horario, text_color="#6B7280", font=ctk.CTkFont(size=12)).pack(anchor="w")

        # ---- Relatório ----
        relatorio = ctk.CTkFrame(
            dashboard,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        relatorio.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(
            relatorio,
            text="Relatório",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=15)

        progresso = ctk.CTkProgressBar(
            relatorio,
            width=220,
            height=14,
            progress_color="#FACC15"
        )
        progresso.set(0.92)
        progresso.pack(pady=25)

        ctk.CTkLabel(
            relatorio,
            text="92% de comparecimento",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 10))

        legendas = [
            ("Agendados", "#22C55E"),
            ("Atendidos", "#FACC15"),
            ("Primeira vez", "#0EA5E9"),
            ("Faltas", "#A78BFA"),
        ]

        for texto, cor in legendas:
            item = ctk.CTkFrame(relatorio, fg_color="transparent")
            item.pack(anchor="w", padx=20, pady=4)

            ctk.CTkLabel(item, text="●", text_color=cor).pack(side="left")
            ctk.CTkLabel(item, text=f" {texto}", text_color="#374151").pack(side="left")


class Financeiro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Financeiro")

        grid = ctk.CTkFrame(self.content_card, fg_color="transparent")
        grid.pack(padx=25, pady=25)

        dados = [
            ("Faturamento Mensal", "R$ 25.480", "#22C55E"),
            ("Despesas", "R$ 9.320", "#EF4444"),
            ("Lucro Líquido", "R$ 16.160", "#0EA5E9"),
        ]

        for i, (label, valor, cor) in enumerate(dados):
            card = ctk.CTkFrame(
                grid,
                fg_color="#F8FAFC",
                corner_radius=14,
                width=240,
                height=120
            )
            card.grid(row=0, column=i, padx=12)

            ctk.CTkLabel(card, text=label, text_color="#6B7280").pack(pady=(25, 5))
            ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"), text_color=cor).pack()


class Agenda(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Agenda")

        self.pagina_atual = 0

        self.render()

    def render(self):
        for w in self.content_card.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(self.content_card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        # ---------- TABELA ----------
        table = ctk.CTkFrame(container, fg_color="transparent")
        table.pack(fill="both", expand=True)

        headers = ["Paciente", "Data", "Horário", "Status"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=h,
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            ).grid(row=0, column=i, sticky="w", padx=20, pady=(0, 10))

        inicio = self.pagina_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados = CONSULTAS_DATA[inicio:fim]

        for r, (nome, data, hora, status) in enumerate(dados, start=1):
            ctk.CTkLabel(
                table,
                text=nome,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=r, column=0, sticky="w", padx=20, pady=14)

            ctk.CTkLabel(table, text=data).grid(row=r, column=1, sticky="w", padx=20)
            ctk.CTkLabel(table, text=hora).grid(row=r, column=2, sticky="w", padx=20)

            info = STATUS_COLORS[status]
            badge = ctk.CTkFrame(
                table,
                fg_color=info["bg"],
                corner_radius=6
            )
            badge.grid(row=r, column=3, sticky="w", padx=20)

            ctk.CTkLabel(
                badge,
                text=status,
                text_color=info["text"],
                font=ctk.CTkFont(size=11, weight="bold"),
                padx=10,
                pady=3
            ).pack()

        # ---------- PAGINAÇÃO ----------
        pag = ctk.CTkFrame(container, fg_color="transparent")
        pag.pack(anchor="e", pady=(20, 0))

        total_paginas = (len(CONSULTAS_DATA) + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS

        def btn(text, ativo=False, cmd=None):
            return ctk.CTkButton(
                pag,
                text=text,
                width=32,
                height=32,
                corner_radius=6,
                fg_color="#0d99c7" if ativo else "#F3F4F6",
                text_color="white" if ativo else "#6B7280",
                hover_color="#0b86af",
                command=cmd
            )

        if self.pagina_atual > 0:
            btn("‹", cmd=lambda: self.trocar_pagina(self.pagina_atual - 1)).pack(side="left", padx=4)

        for i in range(total_paginas):
            btn(
                str(i + 1),
                ativo=i == self.pagina_atual,
                cmd=lambda idx=i: self.trocar_pagina(idx)
            ).pack(side="left", padx=4)

        if self.pagina_atual < total_paginas - 1:
            btn("›", cmd=lambda: self.trocar_pagina(self.pagina_atual + 1)).pack(side="left", padx=4)

    def trocar_pagina(self, pagina):
        self.pagina_atual = pagina
        self.render()

class Pacientes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Pacientes")

        top = ctk.CTkFrame(self.content_card, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=25)

        ctk.CTkEntry(top, placeholder_text="Buscar paciente...", width=350, height=42).pack(side="left")
        ctk.CTkButton(
            top,
            text="Novo Paciente +",
            fg_color="#22C55E",
            hover_color="#16A34A",
            height=42
        ).pack(side="right")


class Configuracoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Configurações")
        ctk.CTkLabel(self.content_card, text="Configurações do sistema.", font=ctk.CTkFont(size=14)).pack(pady=40)

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - OdontoPro")
        self._set_appearance_mode("light")
        self.configure(fg_color="#FFFFFF")

        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{largura}x{altura}")
        self.minsize(1100, 650)

        caminho = os.path.dirname(__file__)

        # ===== IMAGENS =====
        logo_original = Image.open(os.path.join(caminho, "logo.png"))
        proporcao_logo = logo_original.width / logo_original.height
        self.img_logo = ctk.CTkImage(
            logo_original,
            size=(int(50 * proporcao_logo), 50)
        )

        dentista_img = Image.open(os.path.join(caminho, "dentistalogin.png"))
        proporcao_dentista = dentista_img.width / dentista_img.height
        largura_img = int(largura * 0.45)
        altura_img = int((largura_img / proporcao_dentista) * 0.75)

        self.img_dentista = ctk.CTkImage(
            dentista_img,
            size=(largura_img, altura_img)
        )

        # ===== GRID =====
        self.grid_columnconfigure(0, weight=1, uniform="a")
        self.grid_columnconfigure(1, weight=1, uniform="a")
        self.grid_rowconfigure(0, weight=1)

        # ===== ESQUERDA =====
        frame_img = ctk.CTkFrame(self, fg_color="#F2F3F5", corner_radius=0)
        frame_img.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            frame_img,
            text="",
            image=self.img_dentista,
            fg_color="transparent"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ===== DIREITA =====
        frame_login = ctk.CTkFrame(self, fg_color="#F2F3F5", corner_radius=0)
        frame_login.grid(row=0, column=1, sticky="nsew")

        central = ctk.CTkFrame(frame_login, fg_color="transparent")
        central.pack(padx=20, pady=100)

        conteudo = ctk.CTkFrame(central, fg_color="transparent")
        conteudo.pack(anchor="nw", padx=200, pady=40)

        # LOGO
        ctk.CTkLabel(conteudo, text="", image=self.img_logo).pack(anchor="w", pady=(0, 80))

        # TÍTULOS
        ctk.CTkLabel(
            conteudo,
            text="Acesse sua conta",
            font=("Arial", 28, "bold"),
            text_color="#1C1C1C"
        ).pack(anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="Bem-vindo de volta! Entre com seus dados.",
            font=("Arial", 14),
            text_color="#666666"
        ).pack(anchor="w", pady=(0, 20))

        # CAMPOS
        self.ent_user = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Usuário",
            fg_color="white",
            border_width=0
        )
        self.ent_user.pack(pady=15, anchor="w")

        self.ent_pass = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Senha",
            show="*",
            fg_color="white",
            border_width=0
        )
        self.ent_pass.pack(pady=15, anchor="w")

        # OPÇÕES
        linha = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha.pack(fill="x", pady=5)

        ctk.CTkCheckBox(linha, text="Lembrar-me").grid(row=0, column=0)

        ctk.CTkLabel(
            linha,
            text="Esqueci minha senha",
            text_color="#0A66C2"
        ).grid(row=0, column=1, sticky="e")

        linha.grid_columnconfigure(1, weight=1)

        # BOTÃO ENTRAR
        ctk.CTkButton(
            conteudo,
            text="ENTRAR",
            width=420,
            height=50,
            font=("Arial", 12, "bold"),
            fg_color="#0A66C2",
            hover_color="#0959A8",
            corner_radius=8,
            command=self.autenticar
        ).pack(pady=15, anchor="w")

        self.bind("<Return>", lambda e: self.autenticar())

    def autenticar(self):
        user = self.ent_user.get()
        senha = self.ent_pass.get()

        if user in USUARIOS and USUARIOS[user]["senha"] == senha:
            self.destroy()
            app = App(usuario_nome=USUARIOS[user]["nome"])
            app.mainloop()
        else:
            ctk.CTkMessagebox(
                title="Erro",
                message="Usuário ou senha inválidos",
                icon="cancel"
            )


if __name__ == "__main__":
    login = Login()
    login.mainloop()
