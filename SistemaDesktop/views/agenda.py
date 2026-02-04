from .base import BaseScreen
import customtkinter as ctk

# 🔽 IMPORTA DO MODELS (Mantido)
from models.data import (
    LIMITE_CONSULTAS,
    CONSULTAS_DATA,
    STATUS_COLORS
)

class Agenda(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Agenda")

        self.pagina_atual = 0
        self.paciente_selecionado = None 
        
        # Cores e Fontes (Vibe Design)
        self.colors = {
            "bg_card": "#FFFFFF",
            "bg_main": "#F9FAFB",
            "text_primary": "#111827",
            "text_secondary": "#6B7280",
            "primary": "#0d99c7",
            "hover": "#F3F4F6",
            "selected": "#E5F6FD",
            "border": "#E5E7EB"
        }
        
        # Configurações de layout da tabela (Pesos das colunas)
        # 0: Nome (maior), 1: Data, 2: Hora, 3: Status
        self.col_weights = [4, 2, 2, 2] 

        self.render()

    def render(self):
        # Limpa a tela anterior
        for w in self.content_card.winfo_children():
            w.destroy()

        self.content_card.configure(fg_color=self.colors["bg_main"])
        
        # Grid Principal: Lista (70%) | Detalhes (30%)
        main_layout = ctk.CTkFrame(self.content_card, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=20, pady=20)
        main_layout.grid_columnconfigure(0, weight=7)
        main_layout.grid_columnconfigure(1, weight=3)
        main_layout.grid_rowconfigure(0, weight=1)

        # ---------- ESQUERDA: LISTA DE PACIENTES ----------
        left_panel = ctk.CTkFrame(main_layout, fg_color=self.colors["bg_card"], corner_radius=12)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        # 1. Cabeçalho da Tabela (Agora usando GRID para alinhar com as linhas)
        header_frame = ctk.CTkFrame(left_panel, fg_color="transparent", height=45)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(20, 5))
        
        headers = ["Paciente", "Data", "Horário", "Status"]
        
        # Configura grid do cabeçalho
        for col_idx, weight in enumerate(self.col_weights):
            header_frame.grid_columnconfigure(col_idx, weight=weight)
            
            lbl = ctk.CTkLabel(
                header_frame, 
                text=headers[col_idx], 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_secondary"],
                anchor="w" if col_idx < 3 else "center" # Status centralizado
            )
            lbl.grid(row=0, column=col_idx, sticky="ew", padx=5)

        # 2. Container das Linhas
        rows_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        rows_container.grid(row=1, column=0, sticky="nsew", padx=10)
        rows_container.grid_columnconfigure(0, weight=1)

        # Lógica de Paginação
        inicio = self.pagina_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados_pagina = CONSULTAS_DATA[inicio:fim]

        # 3. Renderiza Linhas
        for idx, item in enumerate(dados_pagina):
            nome, data, hora, status = item
            is_selected = self.paciente_selecionado == item
            bg_color = self.colors["selected"] if is_selected else "transparent"
            
            # Linha como Frame
            row = ctk.CTkFrame(rows_container, fg_color=bg_color, corner_radius=8, height=55)
            row.pack(fill="x", pady=3)
            
            # Configura Grid da Linha (Idêntico ao Header)
            for col_idx, weight in enumerate(self.col_weights):
                row.grid_columnconfigure(col_idx, weight=weight)

            # Eventos
            row.bind("<Button-1>", lambda e, d=item: self.selecionar_paciente(d))
            if not is_selected:
                row.bind("<Enter>", lambda e, f=row: f.configure(fg_color=self.colors["hover"]))
                row.bind("<Leave>", lambda e, f=row: f.configure(fg_color="transparent"))

            # --- Coluna 0: Nome ---
            l_nome = ctk.CTkLabel(row, text=nome, font=ctk.CTkFont(size=14, weight="bold"), 
                                  text_color=self.colors["text_primary"], anchor="w")
            l_nome.grid(row=0, column=0, sticky="ew", padx=(15, 5))
            
            # --- Coluna 1: Data ---
            l_data = ctk.CTkLabel(row, text=data, font=ctk.CTkFont(size=13),
                                  text_color=self.colors["text_primary"], anchor="w")
            l_data.grid(row=0, column=1, sticky="ew", padx=5)
            
            # --- Coluna 2: Hora ---
            l_hora = ctk.CTkLabel(row, text=hora, font=ctk.CTkFont(size=13),
                                  text_color=self.colors["text_primary"], anchor="w")
            l_hora.grid(row=0, column=2, sticky="ew", padx=5)

            # --- Coluna 3: Status Badge ---
            info_status = STATUS_COLORS.get(status, {"bg": "#eee", "text": "#333"})
            
            # Frame wrapper para centralizar o badge na célula da grid
            badge_wrapper = ctk.CTkFrame(row, fg_color="transparent")
            badge_wrapper.grid(row=0, column=3, sticky="ew", padx=5)
            
            badge = ctk.CTkFrame(badge_wrapper, fg_color=info_status["bg"], corner_radius=6)
            badge.pack(anchor="center") # Centraliza visualmente
            
            l_status = ctk.CTkLabel(badge, text=status, text_color=info_status["text"], 
                                    font=ctk.CTkFont(size=11, weight="bold"), padx=10, pady=3)
            l_status.pack()

            # Propagar cliques dos filhos para o pai
            for widget in [l_nome, l_data, l_hora, badge_wrapper, badge, l_status]:
                widget.bind("<Button-1>", lambda e, d=item: self.selecionar_paciente(d))

        self.render_pagination(left_panel)
        self.render_details_panel(main_layout)

    def render_pagination(self, parent):
        pag_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pag_frame.grid(row=2, column=0, sticky="e", padx=20, pady=20)

        total_paginas = (len(CONSULTAS_DATA) + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS

        def create_btn(text, cmd, active=False):
            return ctk.CTkButton(
                pag_frame, text=text, width=36, height=36, corner_radius=8,
                fg_color=self.colors["primary"] if active else "transparent",
                border_width=0 if active else 1,
                border_color=self.colors["border"],
                text_color="white" if active else self.colors["text_secondary"],
                hover_color=self.colors["primary"] if not active else None,
                font=ctk.CTkFont(weight="bold"),
                command=cmd
            )

        if self.pagina_atual > 0:
            create_btn("‹", lambda: self.mudar_pagina(self.pagina_atual - 1)).pack(side="left", padx=4)

        for i in range(total_paginas):
            create_btn(str(i + 1), lambda idx=i: self.mudar_pagina(idx), active=(i == self.pagina_atual)).pack(side="left", padx=4)

        if self.pagina_atual < total_paginas - 1:
            create_btn("›", lambda: self.mudar_pagina(self.pagina_atual + 1)).pack(side="left", padx=4)

    def render_details_panel(self, parent):
        details_frame = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        details_frame.grid(row=0, column=1, sticky="nsew")

        if not self.paciente_selecionado:
            ctk.CTkLabel(details_frame, text="Selecione um paciente\npara ver os detalhes.", 
                         font=ctk.CTkFont(size=16),
                         text_color=self.colors["text_secondary"]).place(relx=0.5, rely=0.5, anchor="center")
            return

        nome, data, hora, status = self.paciente_selecionado
        
        # Mock Data Expandida
        detalhes_extras = {
            "Idade": "25 anos",
            "Sexo": "Feminino",
            "Telefone": "(11) 99321-7982",
            "Email": f"{nome.split()[0].lower()}@gmail.com",
            "CPF": "121.***.***-34"
        }

        content = ctk.CTkScrollableFrame(details_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # --- HEADER DO DETALHE ---
        # Avatar
        ctk.CTkLabel(content, text="", width=90, height=90, fg_color="#E5E7EB", corner_radius=45).pack(pady=(10, 15))
        
        # Nome (Fonte Aumentada)
        ctk.CTkLabel(content, text=nome, font=ctk.CTkFont(size=24, weight="bold"), 
                     text_color=self.colors["text_primary"]).pack()
        
        # Subtítulo (Email)
        ctk.CTkLabel(content, text=detalhes_extras["Email"], font=ctk.CTkFont(size=14), 
                     text_color=self.colors["text_secondary"]).pack(pady=(0, 20))

        # Divisória
        ctk.CTkFrame(content, height=1, fg_color=self.colors["border"]).pack(fill="x", pady=10)

        # --- INFO PESSOAL (Layout Grade) ---
        info_grid = ctk.CTkFrame(content, fg_color="transparent")
        info_grid.pack(fill="x", pady=10)
        info_grid.grid_columnconfigure(1, weight=1)

        row_idx = 0
        for label, value in detalhes_extras.items():
            if label == "Email": continue # Já mostramos no topo
            
            # Label (ex: Idade)
            ctk.CTkLabel(info_grid, text=label, font=ctk.CTkFont(size=14, weight="bold"), 
                         text_color=self.colors["text_secondary"], anchor="w").grid(row=row_idx, column=0, sticky="w", pady=4)
            
            # Value (ex: 25 anos) - Fonte Aumentada
            ctk.CTkLabel(info_grid, text=value, font=ctk.CTkFont(size=15), 
                         text_color=self.colors["text_primary"], anchor="e").grid(row=row_idx, column=1, sticky="e", pady=4)
            row_idx += 1

        # Divisória
        ctk.CTkFrame(content, height=1, fg_color=self.colors["border"]).pack(fill="x", pady=20)

        # --- DADOS DA CONSULTA ---
        ctk.CTkLabel(content, text="Detalhes da Consulta", font=ctk.CTkFont(size=18, weight="bold"), 
                     text_color=self.colors["text_primary"], anchor="w").pack(fill="x", pady=(0, 10))

        consulta_box = ctk.CTkFrame(content, fg_color=self.colors["bg_main"], corner_radius=8)
        consulta_box.pack(fill="x")

        # Texto da consulta maior e com espaçamento
        texto_consulta = f"Data: {data}\nHorário: {hora}\nStatus: {status}\n\nObs: Paciente relatou leve desconforto. Retorno agendado."
        
        ctk.CTkLabel(consulta_box, text=texto_consulta, justify="left", anchor="w",
                     font=ctk.CTkFont(size=15), text_color=self.colors["text_primary"]).pack(fill="x", padx=15, pady=15)

        # Botão de Ação
        ctk.CTkButton(content, text="Editar Paciente", fg_color=self.colors["primary"], 
                      height=40, corner_radius=8, font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", pady=30)

    # ---------- LÓGICA ----------
    def selecionar_paciente(self, dados_paciente):
        self.paciente_selecionado = dados_paciente
        self.render()

    def mudar_pagina(self, nova_pagina):
        self.pagina_atual = nova_pagina
        self.paciente_selecionado = None
        self.render()