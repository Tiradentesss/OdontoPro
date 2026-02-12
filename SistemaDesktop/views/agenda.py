from .base import BaseScreen
import customtkinter as ctk

# 🔽 IMPORTA DO MODELS (Mantido)

from models.data import LIMITE_CONSULTAS, STATUS_COLORS
from controllers.consulta_controller import ConsultaController


class Agenda(BaseScreen):
    def __init__(self, parent, clinica_id):
        super().__init__(parent, "Agenda")

        self.clinica_id = clinica_id  # ← ESSENCIAL
        self.pagina_atual = 0
        self.paciente_selecionado = None 

        
        # Cores e Fontes (Vibe Design Moderno)
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
        
        # DEFINIÇÃO RÍGIDA DE LARGURA DAS COLUNAS (Em Pixels)
        # Isso garante que o layout nunca seja "empurrado"
        self.col_widths = {
            "nome": 280,   # Grande o suficiente para nomes completos
            "data": 100,
            "hora": 80,
            "status": 120
        }

        self.render()

    def truncate_text(self, text, limit=35):
        """
        Corta o texto visualmente para caber esteticamente, 
        mas o container físico (Frame) é quem garante o limite real.
        """
        if len(text) > limit:
            return text[:limit] + "..."
        return text

    def render(self):
        # Limpa a tela anterior
        for w in self.content_card.winfo_children():
            w.destroy()

        self.content_card.configure(fg_color=self.colors["bg_main"])
        
        # Grid Principal: Lista (70%) | Detalhes (30%)
        self.main_layout = ctk.CTkFrame(self.content_card, fg_color="transparent")
        self.main_layout.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_layout.grid_columnconfigure(0, weight=7)
        self.main_layout.grid_columnconfigure(1, weight=3)
        self.main_layout.grid_rowconfigure(0, weight=1)


        # ---------- ESQUERDA: LISTA DE PACIENTES ----------
        left_panel = ctk.CTkFrame(self.main_layout, fg_color=self.colors["bg_card"], corner_radius=12)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        # 1. Cabeçalho da Tabela
        header_frame = ctk.CTkFrame(left_panel, fg_color="transparent", height=45)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(20, 5))
        
        # Configuração do Grid do Cabeçalho (Baseado em pesos fixos para alinhar com as linhas)
        # Col 0 (Nome) pega o espaço extra (weight=1), as outras são fixas (weight=0)
        header_frame.grid_columnconfigure(0, weight=1) 
        header_frame.grid_columnconfigure(1, weight=0)
        header_frame.grid_columnconfigure(2, weight=0)
        header_frame.grid_columnconfigure(3, weight=0)

        headers = [
            ("Paciente", self.col_widths["nome"], "w"),
            ("Data", self.col_widths["data"], "center"),
            ("Horário", self.col_widths["hora"], "center"),
            ("Status", self.col_widths["status"], "center")
        ]
        
        for idx, (text, width, anchor) in enumerate(headers):
            # Usamos um Frame interno para garantir a largura mínima no header também
            h_container = ctk.CTkFrame(header_frame, fg_color="transparent", width=width, height=30)
            h_container.grid(row=0, column=idx, sticky="ew" if idx == 0 else "e", padx=5)
            if idx > 0: h_container.pack_propagate(False) # Trava largura das colunas menores

            lbl = ctk.CTkLabel(
                h_container, 
                text=text, 
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=self.colors["text_secondary"]
            )
            lbl.place(relx=0 if anchor=="w" else 0.5, rely=0.5, anchor=anchor if anchor=="w" else "center")

        # 2. Container das Linhas
        rows_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        rows_container.grid(row=1, column=0, sticky="nsew", padx=15)
        rows_container.grid_columnconfigure(0, weight=1) # Permite scroll se necessário

        # Lógica de Paginação
        todas_consultas = ConsultaController.listar_por_clinica(self.clinica_id)

        inicio = self.pagina_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados_pagina = todas_consultas[inicio:fim]


        # 3. Renderiza Linhas
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
                observacoes
            ) = item

            data = data_hora.strftime("%d/%m/%Y")
            hora = data_hora.strftime("%H:%M")

            is_selected = self.paciente_selecionado == consulta_id

            bg_color = self.colors["selected"] if is_selected else "transparent"
            
            # Linha como Frame
            row = ctk.CTkFrame(rows_container, fg_color=bg_color, corner_radius=8, height=55)
            row.pack(fill="x", pady=3)
            
            # Configura Grid da Linha (Sincronia Exata com Header)
            row.grid_columnconfigure(0, weight=1) # Nome expande
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)
            row.grid_columnconfigure(3, weight=0)

            # Eventos (Hover e Click)
            row.bind("<Button-1>", lambda e, d=consulta_id: self.selecionar_paciente(d))
            if not is_selected:
                row.bind("<Enter>", lambda e, f=row: f.configure(fg_color=self.colors["hover"]))
                row.bind("<Leave>", lambda e, f=row: f.configure(fg_color="transparent"))

            # --- Coluna 0: Nome (FIXO E RÍGIDO) ---
            # Criamos um container que NÃO muda de tamanho (pack_propagate False)
            nome_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["nome"])
            nome_container.grid(row=0, column=0, sticky="w", padx=(10, 5))
            nome_container.pack_propagate(False) # O SEGREDO: Impede que texto empurre a largura

            nome_exibicao = self.truncate_text(nome, limit=35) # Truncagem estética
            
            l_nome = ctk.CTkLabel(nome_container, text=nome_exibicao, font=ctk.CTkFont(size=14, weight="bold"), 
                                  text_color=self.colors["text_primary"])
            l_nome.pack(side="left", anchor="w") # Alinhado à esquerda dentro do container fixo
            
            # --- Coluna 1: Data ---
            data_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["data"])
            data_container.grid(row=0, column=1, padx=5)
            data_container.pack_propagate(False)

            l_data = ctk.CTkLabel(data_container, text=data, font=ctk.CTkFont(size=13),
                                  text_color=self.colors["text_primary"])
            l_data.place(relx=0.5, rely=0.5, anchor="center")
            
            # --- Coluna 2: Hora ---
            hora_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["hora"])
            hora_container.grid(row=0, column=2, padx=5)
            hora_container.pack_propagate(False)

            l_hora = ctk.CTkLabel(hora_container, text=hora, font=ctk.CTkFont(size=13),
                                  text_color=self.colors["text_primary"])
            l_hora.place(relx=0.5, rely=0.5, anchor="center")

            # --- Coluna 3: Status Badge ---
            status_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["status"])
            status_container.grid(row=0, column=3, padx=5)
            status_container.pack_propagate(False) # Garante que status longo não quebre

            info_status = STATUS_COLORS.get(status, {"bg": "#eee", "text": "#333"})
            
            badge = ctk.CTkFrame(
                status_container, 
                fg_color=info_status["bg"], 
                corner_radius=6,
                width=100,  
                height=26   
            )
            badge.place(relx=0.5, rely=0.5, anchor="center")
            
            l_status = ctk.CTkLabel(
                badge, 
                text=status, 
                text_color=info_status["text"], 
                font=ctk.CTkFont(size=11, weight="bold")
            )
            l_status.place(relx=0.5, rely=0.5, anchor="center")

            # Propagar cliques dos filhos para o pai (UX Improvement)
            widgets_clicaveis = [l_nome, nome_container, l_data, data_container, 
                                 l_hora, hora_container, status_container, badge, l_status]
            for widget in widgets_clicaveis:
                widget.bind("<Button-1>", lambda e, d=consulta_id: self.selecionar_paciente(d))


        self.render_pagination(left_panel)
        self.render_details_panel(self.main_layout)

    def render_pagination(self, parent):
        pag_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pag_frame.grid(row=2, column=0, sticky="e", padx=20, pady=20)

        todas_consultas = ConsultaController.listar_por_clinica(self.clinica_id)
        total_paginas = (len(todas_consultas) + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS


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
        from datetime import date

        details_frame = ctk.CTkFrame(parent, fg_color=self.colors["bg_card"], corner_radius=12)
        details_frame.grid(row=0, column=1, sticky="nsew")

        # Se nada estiver selecionado
        if not self.paciente_selecionado:
            ctk.CTkLabel(
                details_frame,
                text="Selecione um paciente\npara ver os detalhes.",
                font=ctk.CTkFont(size=16),
                text_color=self.colors["text_secondary"]
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # 🔹 Buscar novamente todas as consultas
        todas_consultas = ConsultaController.listar_por_clinica(self.clinica_id)

        # 🔹 Encontrar a consulta pelo ID
        consulta = next(
            (c for c in todas_consultas if c[0] == self.paciente_selecionado),
            None
        )

        if not consulta:
            return

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
            observacoes
        ) = consulta

        # 🔹 Formatar data e hora corretamente
        data = data_hora.strftime("%d/%m/%Y")
        hora = data_hora.strftime("%H:%M")

        # 🔹 Calcular idade
        idade = None
        if data_nascimento:
            idade = date.today().year - data_nascimento.year

        detalhes_extras = {
            "Idade": f"{idade} anos" if idade else "Não informado",
            "Sexo": sexo or "Não informado",
            "Telefone": telefone or "Não informado",
            "Email": email or "Não informado",
            "CPF": cpf or "Não informado"
        }

        content = ctk.CTkFrame(details_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # --- HEADER ---
        ctk.CTkLabel(
            content,
            text="",
            width=90,
            height=90,
            fg_color="#E5E7EB",
            corner_radius=45
        ).pack(pady=(10, 15))

        ctk.CTkLabel(
            content,
            text=nome,
            font=ctk.CTkFont(size=24, weight="bold"),
            wraplength=250,
            text_color=self.colors["text_primary"]
        ).pack()

        ctk.CTkLabel(
            content,
            text=detalhes_extras["Email"],
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        ).pack(pady=(0, 20))

        ctk.CTkFrame(content, height=1, fg_color=self.colors["border"]).pack(fill="x", pady=10)

        # --- INFO PESSOAL ---
        info_grid = ctk.CTkFrame(content, fg_color="transparent")
        info_grid.pack(fill="x", pady=10)
        info_grid.grid_columnconfigure(1, weight=1)

        row_idx = 0
        for label, value in detalhes_extras.items():
            if label == "Email":
                continue

            ctk.CTkLabel(
                info_grid,
                text=label,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text_secondary"],
                anchor="w"
            ).grid(row=row_idx, column=0, sticky="w", pady=4)

            ctk.CTkLabel(
                info_grid,
                text=value,
                font=ctk.CTkFont(size=15),
                text_color=self.colors["text_primary"],
                anchor="e"
            ).grid(row=row_idx, column=1, sticky="e", pady=4)

            row_idx += 1

        ctk.CTkFrame(content, height=1, fg_color=self.colors["border"]).pack(fill="x", pady=20)

        # --- DADOS DA CONSULTA ---
        ctk.CTkLabel(
            content,
            text="Detalhes da Consulta",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(fill="x", pady=(0, 10))

        consulta_box = ctk.CTkFrame(content, fg_color=self.colors["bg_main"], corner_radius=8)
        consulta_box.pack(fill="x")

        texto_consulta = (
            f"Data: {data}\n"
            f"Horário: {hora}\n"
            f"Status: {status}\n\n"
            f"Observações: {observacoes or 'Nenhuma observação registrada.'}"
        )

        ctk.CTkLabel(
            consulta_box,
            text=texto_consulta,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=15),
            text_color=self.colors["text_primary"]
        ).pack(fill="x", padx=15, pady=15)

        ctk.CTkButton(
            content,
            text="Editar Paciente",
            fg_color=self.colors["primary"],
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=30)


    # ---------- LÓGICA ----------
    def selecionar_paciente(self, consulta_id):
        self.paciente_selecionado = consulta_id
        self.render()  # redesenha tudo corretamente


    def mudar_pagina(self, nova_pagina):
        self.pagina_atual = nova_pagina
        self.paciente_selecionado = None
        self.render()