BASE_URL = "http://127.0.0.1:8000"
import requests
from io import BytesIO

from .base import BaseScreen
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from datetime import date
import os

# 🔽 IMPORTA DO MODELS (Mantido)
from models.data import LIMITE_CONSULTAS
from controllers.consulta_controller import ConsultaController

# Cores de status baseadas na paleta pastel da imagem
LOCAL_STATUS_COLORS = {
    "realizada": {"bg": "#D1FAE5", "text": "#065F46"},
    "agendada": {"bg": "#FEF3C7", "text": "#92400E"},
    "cancelada": {"bg": "#FEE2E2", "text": "#991B1B"}
}

class Agenda(BaseScreen):
    def __init__(self, parent, clinica_id):
        super().__init__(parent, "Agenda")

        # -------------------------
        # VARIÁVEIS DE FILTRO
        # -------------------------
        self.data_var = ctk.StringVar(value="Data")
        self.medico_var = ctk.StringVar(value="Médico")
        self.status_var = ctk.StringVar(value="Status")

        self.filtro_data = None
        self.filtro_medico = None
        self.filtro_status = None

        self.data_var.trace_add("write", self.aplicar_filtros)
        self.medico_var.trace_add("write", self.aplicar_filtros)
        self.status_var.trace_add("write", self.aplicar_filtros)

        # -----

        self.clinica_id = clinica_id 
        self.pagina_atual = 0
        self.paciente_selecionado = None 
        self.image_cache = [] # Evita que as imagens dos avatares sumam por Garbage Collection

        # Cores e Fontes alinhadas com a imagem
        self.colors = {
            "bg_card": "#FFFFFF",
            "bg_main": "#F3F4F6",
            "text_primary": "#111827",
            "text_secondary": "#6B7280",
            "primary": "#00AEEF", # Azul ciano da imagem
            "hover": "#F9FAFB",
            "selected": "#E0F2FE",
            "border": "#E5E7EB",
            "avatar_colors": ["#F59E0B", "#EF4444", "#EC4899", "#10B981", "#3B82F6"] # Cores dinâmicas para avatares
        }
        
        # DEFINIÇÃO RÍGIDA DE LARGURA DAS COLUNAS (Ajustado para a Imagem)
        self.col_widths = {
            "avatar": 60,
            "nome": 180,
            "medico": 150,
            "data": 100,
            "hora": 80,
            "status": 100
        }

        self.render()

    def truncate_text(self, text, limit=35):
        if len(text) > limit:
            return text[:limit] + "..."
        return text

    # --- LÓGICA DE AVATARES INCORPORADA DO CÓDIGO ADICIONAL ---
    def create_letter_avatar(self, letter, color_hex, size):
        color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        img = Image.new("RGBA", (size, size), color=color_rgb)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", int(size * 0.55))
        except:
            font = ImageFont.load_default()

        draw.text((size // 2, size // 2), letter, fill="white", font=font, anchor="mm")

        # Máscara circular para bordas perfeitas
        scale = 4
        big_size = (size * scale, size * scale)
        mask = Image.new("L", big_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, big_size[0] - 1, big_size[1] - 1), fill=255)
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)
        img.putalpha(mask)
        return img

    def render(self):
        self.image_cache.clear() # Limpa cache de imagens na re-renderização
        for w in self.content_card.winfo_children():
            w.destroy()

        self.content_card.configure(fg_color="transparent")
        
        # Grid Principal: Lista (65%) | Detalhes (35%)
        self.main_layout = ctk.CTkFrame(self.content_card, fg_color="transparent")
        self.main_layout.pack(fill="both", expand=True)
        self.main_layout.grid_columnconfigure(0, weight=65)
        self.main_layout.grid_columnconfigure(1, weight=35)
        self.main_layout.grid_rowconfigure(0, weight=1)

        # ---------- ESQUERDA: LISTA DE PACIENTES ----------
        left_panel = ctk.CTkFrame(self.main_layout, fg_color="white", corner_radius=15)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=1) # A linha 2 (lista) expande

        # 1. Filtros (Topo) - Estilo da Imagem
        filter_frame = ctk.CTkFrame(left_panel, fg_color="transparent", height=60)
        filter_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        filter_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(filter_frame, text="Filtros", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text_primary"]).grid(row=0, column=0, padx=(10, 20))
        
        # Filtro Data
        self.data_option = ctk.CTkOptionMenu(
            filter_frame,
            values=["Data"],
            variable=self.data_var
        )
        self.data_option.grid(row=0, column=1, padx=5)

        # Filtro Médico
        self.medico_option = ctk.CTkOptionMenu(
            filter_frame,
            values=["Médico"],
            variable=self.medico_var
        )
        self.medico_option.grid(row=0, column=2, padx=5)

        # Filtro Status
        self.status_option = ctk.CTkOptionMenu(
            filter_frame,
            values=["Todos", "Agendada", "Realizada", "Cancelada"],
            variable=self.status_var
        )
        self.status_option.grid(row=0, column=3, padx=5)

        # 2. Cabeçalho da Tabela
        header_frame = ctk.CTkFrame(left_panel, fg_color="#F9FAFB", height=40, corner_radius=8)
        header_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 5))
        header_frame.grid_propagate(False)
        
        # Configuração das Colunas do Header
        headers = [
            ("Avatar", self.col_widths["avatar"], "nsew"),
            ("Nome", self.col_widths["nome"], "w"),
            ("Medico", self.col_widths["medico"], "nsew"),
            ("Data", self.col_widths["data"], "nsew"),
            ("Hora", self.col_widths["hora"], "nsew"),
            ("Status", self.col_widths["status"], "nsew")
        ]
        
        for idx, (text, width, anchor) in enumerate(headers):
            header_frame.grid_columnconfigure(idx, weight=1 if text in ["Nome", "Medico"] else 0, minsize=width)
            lbl = ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_secondary"])
            lbl.grid(row=0, column=idx, sticky="ew" if anchor=="w" else "nsew", padx=10, pady=10)

        # 3. Container das Linhas
        rows_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        rows_container.grid(row=2, column=0, sticky="nsew", padx=15)
        rows_container.grid_columnconfigure(0, weight=1)

        # Paginação Lógica
        todas_consultas = ConsultaController.listar_por_clinica(self.clinica_id)

        # =========================
        # GERAR DATAS DISPONÍVEIS
        # =========================
        datas_unicas = sorted(
            {c[2].strftime("%d/%m/%Y") for c in todas_consultas}
        )

        valores_data = ["Todos"] + datas_unicas

        # =========================
        # GERAR MÉDICOS DISPONÍVEIS
        # =========================
        medicos_unicos = sorted(
            {c[10] for c in todas_consultas if c[10]}
        )

        valores_medico = ["Todos"] + medicos_unicos

        # Atualiza OptionMenus dinamicamente
        self.data_option.configure(values=valores_data)
        self.medico_option.configure(values=valores_medico)

        # Aplicar filtros
        if self.filtro_data:
            todas_consultas = [
                c for c in todas_consultas
                if c[2].strftime("%d/%m/%Y") == self.filtro_data
            ]

        if self.filtro_status:
            todas_consultas = [
                c for c in todas_consultas
                if c[3].lower() == self.filtro_status.lower()
            ]

        if self.filtro_medico:
            todas_consultas = [
                c for c in todas_consultas
                if c[10] == self.filtro_medico
            ]

        inicio = self.pagina_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados_pagina = todas_consultas[inicio:fim]

        # Renderiza Linhas
        for idx, item in enumerate(dados_pagina):
            (
                consulta_id,
                nome,
                data_hora,
                status,
                telefone,
                email,
                sexo,
                data_nascimento,
                cpf,
                observacoes,
                medico_nome
            ) = item

            medico_nome = medico_nome or "Não informado"
            
            status = status.lower() # Normaliza para buscar na paleta pastel
            data = data_hora.strftime("%d/%m/%Y")
            hora = data_hora.strftime("%H:%M")
            is_selected = self.paciente_selecionado == consulta_id

            bg_color = self.colors["selected"] if is_selected else "transparent"
            
            row = ctk.CTkFrame(rows_container, fg_color=bg_color, corner_radius=8, height=50)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            for col_idx, (_, width, _) in enumerate(headers):
                row.grid_columnconfigure(col_idx, weight=1 if col_idx in [1, 2] else 0, minsize=width)

            # Eventos (Hover e Click) replicados do código adicional
            row.bind("<Button-1>", lambda e, d=consulta_id: self.selecionar_paciente(d))
            if not is_selected:
                row.bind("<Enter>", lambda e, f=row: f.configure(fg_color=self.colors["hover"]))
                row.bind("<Leave>", lambda e, f=row: f.configure(fg_color="transparent"))

            # --- Col 0: Avatar Gerado ---
            av_color = self.colors["avatar_colors"][hash(nome) % len(self.colors["avatar_colors"])]
            av_img = self.create_letter_avatar(nome[0].upper(), av_color, 26)
            ctk_av_img = ctk.CTkImage(light_image=av_img, dark_image=av_img, size=(26, 26))
            self.image_cache.append(ctk_av_img)
            
            l_avatar = ctk.CTkLabel(row, image=ctk_av_img, text="")
            l_avatar.grid(row=0, column=0, pady=12)

            # --- Col 1: Nome ---
            l_nome = ctk.CTkLabel(row, text=self.truncate_text(nome, 30), font=ctk.CTkFont(size=13, weight="bold"), text_color=self.colors["text_primary"])
            l_nome.grid(row=0, column=1, sticky="w", padx=10)
            
            # --- Col 2: Médico ---
            l_medico = ctk.CTkLabel(row, text=medico_nome, font=ctk.CTkFont(size=13), text_color=self.colors["text_primary"])
            l_medico.grid(row=0, column=2, sticky="nsew")

            # --- Col 3: Data ---
            l_data = ctk.CTkLabel(row, text=data, font=ctk.CTkFont(size=12), text_color=self.colors["text_primary"])
            l_data.grid(row=0, column=3, sticky="nsew")
            
            # --- Col 4: Hora ---
            l_hora = ctk.CTkLabel(row, text=hora, font=ctk.CTkFont(size=12), text_color=self.colors["text_primary"])
            l_hora.grid(row=0, column=4, sticky="nsew")

            # --- Col 5: Status Badge ---
            info_status = LOCAL_STATUS_COLORS.get(status, {"bg": "#E5E7EB", "text": "#374151"})
            badge = ctk.CTkFrame(row, fg_color=info_status["bg"], corner_radius=12, width=80, height=24)
            badge.grid(row=0, column=5, sticky="nsew", pady=13)
            badge.pack_propagate(False)
            
            l_status = ctk.CTkLabel(badge, text=status, text_color=info_status["text"], font=ctk.CTkFont(size=11, weight="bold"))
            l_status.place(relx=0.5, rely=0.5, anchor="center")

            # Bind clicks nos filhos
            for widget in [l_avatar, l_nome, l_medico, l_data, l_hora, badge, l_status]:
                widget.bind("<Button-1>", lambda e, d=consulta_id: self.selecionar_paciente(d))

        self.render_pagination(left_panel, len(todas_consultas))
        self.render_details_panel(self.main_layout)

    def render_pagination(self, parent, total_items):
        pag_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pag_frame.grid(row=3, column=0, sticky="e", padx=20, pady=15)

        total_paginas = max(1, (total_items + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS)

        def create_btn(text, cmd, active=False):
            return ctk.CTkButton(
                pag_frame, text=text, width=32, height=32, corner_radius=6,
                fg_color=self.colors["primary"] if active else "transparent",
                border_width=0 if active else 1,
                border_color=self.colors["border"],
                text_color="white" if active else self.colors["text_secondary"],
                hover_color=self.colors["primary"] if not active else "#F3F4F6",
                font=ctk.CTkFont(weight="bold"),
                command=cmd
            )

        # Renderiza botões parecidos com a imagem (Quadrados azuis)
        for i in range(total_paginas):
            create_btn(str(i + 1), lambda idx=i: self.mudar_pagina(idx), active=(i == self.pagina_atual)).pack(side="left", padx=2)

    def render_details_panel(self, parent):
        details_frame = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=15)
        details_frame.grid(row=0, column=1, sticky="nsew")

        if not self.paciente_selecionado:
            ctk.CTkLabel(details_frame, text="Selecione um paciente.", font=ctk.CTkFont(size=14), text_color=self.colors["text_secondary"]).place(relx=0.5, rely=0.5, anchor="center")
            return

        consulta = ConsultaController.buscar_por_id(self.paciente_selecionado)
        if not consulta: return

        (
            consulta_id,
            nome,
            data_hora,
            status,
            telefone,
            email,
            sexo,
            data_nascimento,
            cpf,
            foto,
            observacoes,
            medico_nome
        ) = consulta
        status = status.lower()
        data = data_hora.strftime("%d/%m/%Y")
        hora = data_hora.strftime("%H:%M")
        medico_nome = medico_nome or "Não informado"

        idade = self.calcular_idade(data_nascimento)

        content = ctk.CTkFrame(details_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=40)

        # --- HEADER DETALHES (Avatar Gigante, Nome, Status) ---
        header_det = ctk.CTkFrame(content, fg_color="transparent")
        header_det.pack(fill="x", pady=(0, 30))
        
        # Avatar Grande (imagem ou círculo padrão)
        avatar_label = ctk.CTkLabel(
            header_det,
            width=90,
            height=90,
            corner_radius=45,
            fg_color="#E5E7EB",
            text=""
        )
        avatar_label.pack(pady=(0, 10))

        if foto:
            try:
                url = f"{BASE_URL}/media/{foto}"
                response = requests.get(url, timeout=5)

                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((90, 90))

                    img_ctk = ctk.CTkImage(light_image=img, size=(90, 90))
                    avatar_label.configure(image=img_ctk, text="")
                    avatar_label.image = img_ctk

            except Exception:
                pass

        ctk.CTkLabel(header_det, text=nome, font=ctk.CTkFont(size=20, weight="bold"), text_color=self.colors["text_primary"]).pack()
        ctk.CTkLabel(header_det, text=email or "sem@email.com", font=ctk.CTkFont(size=13), text_color=self.colors["primary"]).pack(pady=(0, 10))

        # Badge de Status centralizado abaixo do email
        info_status = LOCAL_STATUS_COLORS.get(status, {"bg": "#E5E7EB", "text": "#374151"})
        badge_det = ctk.CTkFrame(header_det, fg_color=info_status["bg"], corner_radius=6, height=28)
        badge_det.pack(ipadx=15)
        ctk.CTkLabel(badge_det, text=status, text_color=info_status["text"], font=ctk.CTkFont(size=12, weight="bold")).pack(padx=20, pady=4)

        # --- CORPO: DUAS COLUNAS (Paciente | Consulta) ---
        info_grid = ctk.CTkFrame(content, fg_color="transparent")
        info_grid.pack(fill="both", expand=False, pady=10)
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)

        # Coluna Esquerda: Paciente
        col_esq = ctk.CTkFrame(info_grid, fg_color="transparent")
        col_esq.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(col_esq, text="Paciente", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0,10))
        
        paciente_info = [("Idade", idade), ("Sexo", sexo or "Não informado"), ("Telefone", telefone or "Não informado"), ("CPF", cpf or "Não informado")]
        for lbl, val in paciente_info:
            row_f = ctk.CTkFrame(col_esq, fg_color="transparent")
            row_f.pack(fill="x", pady=4)
            ctk.CTkLabel(row_f, text=lbl, font=ctk.CTkFont(size=12), text_color=self.colors["text_secondary"]).pack(side="left")
            ctk.CTkLabel(row_f, text=val, font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"]).pack(side="right")

        # Coluna Direita: Consulta
        col_dir = ctk.CTkFrame(info_grid, fg_color="transparent")
        col_dir.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(col_dir, text="Consulta", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(0,10))
        
        consulta_info = [
            ("Medico:", medico_nome),
            ("Data:", data),
            ("Horário:", hora)
        ]
        for lbl, val in consulta_info:
            row_f = ctk.CTkFrame(col_dir, fg_color="transparent")
            row_f.pack(fill="x", pady=4)
            ctk.CTkLabel(row_f, text=lbl, font=ctk.CTkFont(size=12), text_color=self.colors["text_primary" if lbl=="Medico:" else "text_secondary"]).pack(side="left")
            ctk.CTkLabel(row_f, text=val, font=ctk.CTkFont(size=12, weight="bold"), text_color=self.colors["text_primary"]).pack(side="right")

        # -----------------------------
        # OBSERVAÇÕES
        # -----------------------------
        obs_frame = ctk.CTkFrame(content, fg_color="transparent")
        obs_frame.pack(fill="both", expand=False, pady=(20, 0))

        ctk.CTkLabel(
            obs_frame,
            text="Observações",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_secondary"]
        ).pack(anchor="w", pady=(0, 5))

        self.obs_text = ctk.CTkTextbox(
            obs_frame,
            height=100
        )
        self.obs_text.pack(fill="x")

        # Inserir texto vindo do banco
        self.obs_text.delete("1.0", "end")
        self.obs_text.insert("1.0", observacoes or "")

        # --- BOTÃO EDITAR ---
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(20, 0))
        ctk.CTkButton(
            btn_frame, text="Editar Paciente", fg_color=self.colors["primary"], 
            height=35, width=150, corner_radius=4, font=ctk.CTkFont(size=12, weight="bold")
        ).pack()

    # ---------- LÓGICA ----------
    def selecionar_paciente(self, consulta_id):
        self.paciente_selecionado = consulta_id
        self.render()

    def mudar_pagina(self, nova_pagina):
        self.pagina_atual = nova_pagina
        self.paciente_selecionado = None
        self.render()

    def aplicar_filtros(self, *_):
        valor_data = self.data_var.get()
        valor_medico = self.medico_var.get()
        valor_status = self.status_var.get()

        # DATA
        if valor_data in ["Data", "Todos"]:
            self.filtro_data = None
        else:
            self.filtro_data = valor_data

        # MÉDICO
        if valor_medico in ["Médico", "Todos"]:
            self.filtro_medico = None
        else:
            self.filtro_medico = valor_medico

        # STATUS
        if valor_status in ["Status", "Todos"]:
            self.filtro_status = None
        else:
            self.filtro_status = valor_status

        self.pagina_atual = 0
        self.paciente_selecionado = None

        self.render()

    def calcular_idade(self, data_nascimento):
        if not data_nascimento:
            return ""

        # Se vier string do MySQL, converte
        if isinstance(data_nascimento, str):
            from datetime import datetime
            data_nascimento = datetime.strptime(data_nascimento, "%Y-%m-%d").date()

        hoje = date.today()
        idade = hoje.year - data_nascimento.year

        if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
            idade -= 1

        return f"{idade} anos"

from datetime import date