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
            ("💰  Financeiro", "financeiro"),
            ("⚙  Configurações", "config"),
            ("👤  Cadastro", "cadastro"),
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
            "financeiro": Financeiro(self.container),
            "config": Configuracoes(self.container),
            "cadastro": Cadastro(self.container),
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

        # Background do Dashboard
        self.main_container = ctk.CTkFrame(
            self.content_card,
            fg_color="#F0F2F5",
            corner_radius=0
        )
        self.main_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Grid responsivo
        self.main_container.grid_columnconfigure((0, 1), weight=1)
        self.main_container.grid_rowconfigure((0, 1), weight=1)

        # Estilo padrão dos cards
        self.style = {
            "fg_color": "#FFFFFF",
            "corner_radius": 18,
            "border_width": 1,
            "border_color": "#E5E7EB"
        }

        self.setup_consultas()
        self.setup_performance()
        self.setup_pacientes()
        self.setup_financeiro()

    # --------------------------------------------------

    def create_card(self, row, column):
        card = ctk.CTkFrame(self.main_container, **self.style)
        card.grid(row=row, column=column, padx=15, pady=15, sticky="nsew")
        card.grid_rowconfigure(1, weight=1)
        return card

    def create_header(self, parent, text):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(25, 10))

        title = ctk.CTkLabel(
            header,
            text=text,
            font=font("subtitle", "bold"),
            text_color="#111827"
        )
        title.pack(anchor="w")

        return header

    # --------------------------------------------------

    def setup_consultas(self):

        card = self.create_card(0, 0)
        self.create_header(card, "📅 Próximas Consultas")

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        data = [
            ("Victor Araújo", "09:00", "Confirmado"),
            ("Natália Silva", "12:00", "Pendente")
        ]

        for nome, hora, status in data:

            item = ctk.CTkFrame(
                container,
                fg_color="#F8FAFC",
                corner_radius=12,
                height=52
            )
            item.pack(fill="x", pady=6)
            item.pack_propagate(False)

            ctk.CTkLabel(
                item,
                text=nome,
                font=font("text", "bold"),
                text_color="#334155"
            ).pack(side="left", padx=15)

            badge_color = "#6366F1" if status == "Confirmado" else "#94A3B8"

            ctk.CTkLabel(
                item,
                text=hora,
                font=font("small", "bold"),
                text_color="white",
                fg_color=badge_color,
                corner_radius=8,
                width=70,
                height=28
            ).pack(side="right", padx=15)

    # --------------------------------------------------

    def setup_performance(self):

        card = self.create_card(0, 1)
        self.create_header(card, "📊 Presença Média")

        center = ctk.CTkFrame(card, fg_color="transparent")
        center.pack(expand=True)

        ctk.CTkLabel(
            center,
            text="92%",
            font=font("h1", "bold"),
            text_color="#059669"
        ).pack(pady=(10, 5))

        bar = ctk.CTkProgressBar(
            center,
            width=220,
            height=12,
            progress_color="#10B981",
            fg_color="#E2E8F0"
        )
        bar.set(0.92)
        bar.pack(pady=10)

        ctk.CTkLabel(
            center,
            text="Taxa de comparecimento alta",
            font=font("small"),
            text_color="#64748B"
        ).pack()

    # --------------------------------------------------

    def setup_pacientes(self):

        card = self.create_card(1, 0)
        self.create_header(card, "👥 Novos Pacientes")

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        for p in ["Ana Costa", "Carlos Melo"]:

            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=8)

            avatar = ctk.CTkLabel(
                row,
                text=p[0],
                width=38,
                height=38,
                fg_color="#E0E7FF",
                text_color="#4338CA",
                corner_radius=19,
                font=font("text", "bold")
            )
            avatar.pack(side="left")

            ctk.CTkLabel(
                row,
                text=p,
                font=font("text"),
                text_color="#1F2937"
            ).pack(side="left", padx=15)

    # --------------------------------------------------

    def setup_financeiro(self):

        card = self.create_card(1, 1)
        self.create_header(card, "💰 Faturamento")

        v_container = ctk.CTkFrame(card, fg_color="transparent")
        v_container.pack(expand=True)

        ctk.CTkLabel(
            v_container,
            text="R$ 12.450",
            font=font("h1", "bold"),
            text_color="#111827"
        ).pack(pady=(10, 5))

        badge = ctk.CTkLabel(
            v_container,
            text=" ▲ 12.5% este mês ",
            font=font("small", "bold"),
            text_color="#15803d",
            fg_color="#DCFCE7",
            corner_radius=10,
            height=26
        )
        badge.pack(pady=8)

        self.update_idletasks()
        
    pass

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

class Cadastro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Cadastro")

        # =============================
        # CONTAINER PRINCIPAL
        # =============================
        container = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=30, pady=20)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # =============================
        # CARD - CADASTRO DE PACIENTES
        # =============================
        card_paciente = ctk.CTkFrame(
            container,
            corner_radius=20,
            fg_color="#FFFFFF"
        )
        card_paciente.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self._titulo(card_paciente, "Cadastro de Pacientes")

        self._entry(card_paciente, "Nome completo")
        self._entry(card_paciente, "Data de nascimento")
        self._entry(card_paciente, "Endereço")
        self._entry(card_paciente, "CPF")
        self._entry(card_paciente, "Telefone / WhatsApp")
        self._entry(card_paciente, "Email")
        self._entry(card_paciente, "Senha", show="*")

        self._botao_salvar(card_paciente)

        # =============================
        # CARD - CADASTRO DE PROFISSIONAL
        # =============================
        card_profissional = ctk.CTkFrame(
            container,
            corner_radius=20,
            fg_color="#FFFFFF"
        )
        card_profissional.grid(row=0, column=1, sticky="nsew")

        self._titulo(card_profissional, "Cadastro de Profissional")

        self._entry(card_profissional, "Nome completo")

        ctk.CTkOptionMenu(
            card_profissional,
            values=["Selecione", "Dentista", "Auxiliar", "Recepcionista"],
            height=40,
            fg_color="#F9FAFB",
            button_color="#E5E7EB",
            text_color="#111827"
        ).pack(fill="x", padx=30, pady=(10, 5))

        linha = ctk.CTkFrame(card_profissional, fg_color="transparent")
        linha.pack(fill="x", padx=30, pady=5)

        ctk.CTkEntry(linha, placeholder_text="CRO", height=40)\
            .pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkEntry(linha, placeholder_text="Telefone", height=40)\
            .pack(side="left", expand=True, fill="x")

        self._entry(card_profissional, "Email")
        self._entry(card_profissional, "Senha", show="*")

        self._botao_salvar(card_profissional)

    # =====================================================
    # COMPONENTES REUTILIZÁVEIS
    # =====================================================
    def _titulo(self, parent, texto):
        ctk.CTkLabel(
            parent,
            text=texto,
            font=("Poppins", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=30, pady=(25, 15))

    def _entry(self, parent, placeholder, show=None):
        ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40,
            show=show,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            text_color="#111827"
        ).pack(fill="x", padx=30, pady=5)

    def _botao_salvar(self, parent):
        ctk.CTkButton(
            parent,
            text="Salvar",
            height=42,
            fg_color="#06D6D6",
            hover_color="#04B4B4",
            text_color="#0F172A",
            corner_radius=20
        ).pack(pady=25)


class Configuracoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Configurações")
        ctk.CTkLabel(self.content_card, text="Configurações do sistema.", font=ctk.CTkFont(size=14)).pack(pady=40)

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - OdontoPro")

        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{largura}x{altura}")
        self.configure(fg_color="#F2F3F5")

        caminho = os.path.dirname(__file__)

        # ================= GRID 50/50 =================
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= IMAGENS =================
        logo_original = Image.open(os.path.join(caminho, "logo.png"))
        proporcao = logo_original.width / logo_original.height
        img_logo = ctk.CTkImage(logo_original, size=(int(50 * proporcao), 50))

        dentista_img = Image.open(os.path.join(caminho, "dentistalogin.png"))
        proporcao_dentista = dentista_img.width / dentista_img.height

        largura_img = int(largura * 0.42)
        altura_img = int(largura_img / proporcao_dentista)

        img_dentista = ctk.CTkImage(
            dentista_img,
            size=(largura_img, altura_img)
        )

        # ================= ESQUERDA =================
        frame_img = ctk.CTkFrame(self, fg_color="#F2F3F5", corner_radius=0)
        frame_img.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            frame_img,
            text="",
            image=img_dentista
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ================= DIREITA =================
        frame_login = ctk.CTkFrame(self, fg_color="#F2F3F5", corner_radius=0)
        frame_login.grid(row=0, column=1, sticky="nsew")

        # 🔑 SCROLL REAL (FUNCIONA)
        scroll = ctk.CTkScrollableFrame(
            frame_login,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True)

        conteudo = ctk.CTkFrame(scroll, fg_color="transparent")
        conteudo.pack(anchor="center", pady=40)

        # ================= CONTEÚDO =================
        ctk.CTkLabel(conteudo, text="", image=img_logo).pack(anchor="w", pady=(0, 40))

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
        ).pack(anchor="w", pady=(0, 25))

        self.ent_user = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Usuário",
            fg_color="white",
            border_width=0
        )
        self.ent_user.pack(pady=10, anchor="w")

        self.ent_pass = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Senha",
            show="*",
            fg_color="white",
            border_width=0
        )
        self.ent_pass.pack(pady=10, anchor="w")

        linha = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha.pack(fill="x", pady=10)

        ctk.CTkCheckBox(linha, text="Lembrar-me").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            linha,
            text="Esqueci minha senha",
            text_color="#0A66C2"
        ).grid(row=0, column=1, sticky="e")
        linha.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            conteudo,
            text="ENTRAR",
            width=420,
            height=50,
            fg_color="#0A66C2",
            hover_color="#0959A8",
            font=("Arial", 12, "bold"),
            command=self.autenticar
        ).pack(pady=15, anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="────────────  ou continue com  ────────────",
            text_color="#999"
        ).pack(pady=15)

        ctk.CTkButton(
            conteudo,
            text="Entrar com Google",
            width=420,
            height=48,
            fg_color="#0A66C2",
            hover_color="#0959A8",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        ctk.CTkButton(
            conteudo,
            text="Entrar com Facebook",
            width=420,
            height=48,
            fg_color="#0A66C2",
            hover_color="#0959A8",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        rodape = ctk.CTkFrame(conteudo, fg_color="transparent")
        rodape.pack(pady=15)

        ctk.CTkLabel(rodape, text="Não tem conta?").grid(row=0, column=0)
        ctk.CTkLabel(
            rodape,
            text=" Cadastre-se",
            text_color="#0A66C2",
            font=("Arial", 13, "bold")
        ).grid(row=0, column=1)

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
