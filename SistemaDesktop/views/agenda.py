from .base import BaseScreen
import customtkinter as ctk
from .theme import font, ICON_SIZE
from datetime import date

# 🔽 IMPORTA DO MODELS (Mantido)
from models.data import LIMITE_CONSULTAS, STATUS_COLORS
from controllers.consulta_controller import ConsultaController


class Agenda(BaseScreen):
    """
    Tela de Agenda - Gerenciamento de consultas
    Segue o padrão visual estabelecido no Painel
    """
    
    def __init__(self, parent, clinica_id):
        super().__init__(parent, "Agenda")

        self.clinica_id = clinica_id
        self.pagina_atual = 0
        self.paciente_selecionado = None 

        # DEFINIÇÃO DE LARGURA DAS COLUNAS (em pixels)
        self.col_widths = {
            "nome": 280,
            "data": 100,
            "hora": 80,
            "status": 120
        }

        self.render()

    def truncate_text(self, text, limit=35):
        """Corta o texto visualmente para caber esteticamente"""
        if len(text) > limit:
            return text[:limit] + "..."
        return text

    def render(self):
        """Renderiza a tela principal"""
        # Limpa a tela anterior
        for w in self.content_card.winfo_children():
            w.destroy()

        # Container principal dentro do card
        main_container = ctk.CTkFrame(self.content_card, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=25, pady=25)
        
        # Grid Principal: Lista (70%) | Detalhes (30%)
        main_container.grid_columnconfigure(0, weight=7)
        main_container.grid_columnconfigure(1, weight=3)
        main_container.grid_rowconfigure(0, weight=1)

        # ---------- ESQUERDA: LISTA DE PACIENTES ----------
        self._render_lista_pacientes(main_container)
        
        # ---------- DIREITA: DETALHES ----------
        self._render_detalhes_paciente(main_container)

    def _render_lista_pacientes(self, parent):
        """Renderiza a lista de pacientes à esquerda"""
        left_panel = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        # Cabeçalho da Tabela
        self._render_tabela_cabecalho(left_panel)

        # Container das Linhas
        rows_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        rows_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        rows_container.grid_columnconfigure(0, weight=1)

        # Buscar consultas
        todas_consultas = ConsultaController.listar_por_clinica(self.clinica_id)
        inicio = self.pagina_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados_pagina = todas_consultas[inicio:fim]

        # Renderiza linhas
        for item in dados_pagina:
            self._render_linha_consulta(rows_container, item)

        # Paginação
        self._render_paginacao(left_panel, todas_consultas)

    def _render_tabela_cabecalho(self, parent):
        """Renderiza o cabeçalho da tabela"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        
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
            h_container = ctk.CTkFrame(header_frame, fg_color="transparent", width=width, height=30)
            h_container.grid(row=0, column=idx, sticky="ew" if idx == 0 else "e", padx=5)
            if idx > 0:
                h_container.pack_propagate(False)

            ctk.CTkLabel(
                h_container,
                text=text,
                font=font("small", "bold"),
                text_color="#6B7280"  # ✅ Cor secundária padronizada
            ).place(relx=0 if anchor == "w" else 0.5, rely=0.5, anchor=anchor if anchor == "w" else "center")

    def _render_linha_consulta(self, parent, consulta):
        """Renderiza uma linha de consulta na tabela"""
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

        data = data_hora.strftime("%d/%m/%Y")
        hora = data_hora.strftime("%H:%M")

        is_selected = self.paciente_selecionado == consulta_id
        bg_color = "#EFF6FF" if is_selected else "transparent"
        
        # Linha
        row = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=8, height=50)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)
        row.grid_columnconfigure(2, weight=0)
        row.grid_columnconfigure(3, weight=0)

        # Eventos
        row.bind("<Button-1>", lambda e, d=consulta_id: self.selecionar_paciente(d))
        if not is_selected:
            row.bind("<Enter>", lambda e, f=row: f.configure(fg_color="#F9FAFB"))
            row.bind("<Leave>", lambda e, f=row: f.configure(fg_color="transparent"))

        # Coluna 0: Nome
        nome_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["nome"])
        nome_container.grid(row=0, column=0, sticky="w", padx=(10, 5))
        nome_container.pack_propagate(False)

        nome_exibicao = self.truncate_text(nome, limit=35)
        l_nome = ctk.CTkLabel(
            nome_container,
            text=nome_exibicao,
            font=font("text", "bold"),  # ✅ Negrito padronizado
            text_color="#111827"  # ✅ Cor principal padronizada
        )
        l_nome.pack(side="left", anchor="w")
        
        # Coluna 1: Data
        data_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["data"])
        data_container.grid(row=0, column=1, padx=5)
        data_container.pack_propagate(False)

        l_data = ctk.CTkLabel(
            data_container,
            text=data,
            font=font("text"),  # ✅ Fonte padronizada
            text_color="#111827"  # ✅ Cor principal padronizada
        )
        l_data.place(relx=0.5, rely=0.5, anchor="center")
        
        # Coluna 2: Hora
        hora_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["hora"])
        hora_container.grid(row=0, column=2, padx=5)
        hora_container.pack_propagate(False)

        l_hora = ctk.CTkLabel(
            hora_container,
            text=hora,
            font=font("text"),  # ✅ Fonte padronizada
            text_color="#111827"  # ✅ Cor principal padronizada
        )
        l_hora.place(relx=0.5, rely=0.5, anchor="center")

        # Coluna 3: Status Badge
        status_container = ctk.CTkFrame(row, fg_color="transparent", height=40, width=self.col_widths["status"])
        status_container.grid(row=0, column=3, padx=5)
        status_container.pack_propagate(False)

        info_status = STATUS_COLORS.get(status, {"bg": "#F3F4F6", "text": "#374151"})
        
        badge = ctk.CTkFrame(
            status_container,
            fg_color=info_status["bg"],
            corner_radius=12,
            width=90,
            height=24
        )
        badge.place(relx=0.5, rely=0.5, anchor="center")
        
        l_status = ctk.CTkLabel(
            badge,
            text=status,
            text_color=info_status["text"],
            font=font("small", "bold")  # ✅ Fonte pequena negrito padronizada
        )
        l_status.place(relx=0.5, rely=0.5, anchor="center")

        # Propagar cliques
        widgets_clicaveis = [l_nome, nome_container, l_data, data_container,
                             l_hora, hora_container, status_container, badge, l_status]
        for widget in widgets_clicaveis:
            widget.bind("<Button-1>", lambda e, d=consulta_id: self.selecionar_paciente(d))

    def _render_paginacao(self, parent, todas_consultas):
        """Renderiza os controles de paginação"""
        total_paginas = (len(todas_consultas) + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS
        
        if total_paginas <= 1:
            return

        pag_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pag_frame.grid(row=2, column=0, sticky="e", padx=15, pady=15)

        # Botão anterior
        if self.pagina_atual > 0:
            ctk.CTkButton(
                pag_frame,
                text="←",
                width=36,
                height=36,
                corner_radius=8,  # ✅ Cantos padronizados
                fg_color="#F9FAFB",
                border_width=1,
                border_color="#E5E7EB",
                text_color="#374151",
                hover_color="#F3F4F6",
                font=font("text", "bold"),  # ✅ Fonte padronizada
                command=lambda: self.mudar_pagina(self.pagina_atual - 1)
            ).pack(side="left", padx=2)

        # Números das páginas
        for i in range(total_paginas):
            is_active = (i == self.pagina_atual)
            ctk.CTkButton(
                pag_frame,
                text=str(i + 1),
                width=36,
                height=36,
                corner_radius=8,  # ✅ Cantos padronizados
                fg_color="#0EA5E9" if is_active else "#F9FAFB",  # ✅ Azul padronizado
                text_color="white" if is_active else "#374151",
                border_width=0 if is_active else 1,
                border_color="#E5E7EB" if not is_active else None,
                hover_color="#0284C7" if is_active else "#F3F4F6",  # ✅ Hover padronizado
                font=font("text", "bold"),  # ✅ Fonte padronizada
                command=lambda idx=i: self.mudar_pagina(idx)
            ).pack(side="left", padx=2)

        # Botão próximo
        if self.pagina_atual < total_paginas - 1:
            ctk.CTkButton(
                pag_frame,
                text="→",
                width=36,
                height=36,
                corner_radius=8,  # ✅ Cantos padronizados
                fg_color="#F9FAFB",
                border_width=1,
                border_color="#E5E7EB",
                text_color="#374151",
                hover_color="#F3F4F6",
                font=font("text", "bold"),  # ✅ Fonte padronizada
                command=lambda: self.mudar_pagina(self.pagina_atual + 1)
            ).pack(side="left", padx=2)

    def _render_detalhes_paciente(self, parent):
        """Renderiza o painel de detalhes do paciente à direita"""
        details_frame = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        details_frame.grid(row=0, column=1, sticky="nsew")

        # Se nada estiver selecionado
        if not self.paciente_selecionado:
            ctk.CTkLabel(
                details_frame,
                text="Selecione um paciente\npara ver os detalhes.",
                font=font("text"),  # ✅ Fonte padronizada
                text_color="#6B7280"  # ✅ Cor secundária padronizada
            ).place(relx=0.5, rely=0.5, anchor="center")
            return

        # Buscar consulta selecionada
        todas_consultas = ConsultaController.listar_por_clinica(self.clinica_id)
        consulta = next(
            (c for c in todas_consultas if c[0] == self.paciente_selecionado),
            None
        )

        if not consulta:
            return

        self._render_conteudo_detalhes(details_frame, consulta)

    def _render_conteudo_detalhes(self, parent, consulta):
        """Renderiza o conteúdo detalhado do paciente"""
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

        data = data_hora.strftime("%d/%m/%Y")
        hora = data_hora.strftime("%H:%M")

        # Calcular idade
        idade = None
        if data_nascimento:
            idade = date.today().year - data_nascimento.year

        # Container com scroll
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#0EA5E9",  # ✅ Azul padronizado
            scrollbar_button_hover_color="#0284C7"  # ✅ Hover padronizado
        )
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Avatar
        avatar_frame = ctk.CTkFrame(
            scroll,
            fg_color="#F3F4F6",
            width=80,
            height=80,
            corner_radius=40
        )
        avatar_frame.pack(pady=(0, 15))
        avatar_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=font("title")  # ✅ Fonte título padronizada
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Nome
        ctk.CTkLabel(
            scroll,
            text=nome,
            font=font("subtitle", "bold"),  # ✅ Fonte subtitle negrito padronizada
            text_color="#111827"  # ✅ Cor principal padronizada
        ).pack()

        # Email
        ctk.CTkLabel(
            scroll,
            text=email or "Email não informado",
            font=font("small"),  # ✅ Fonte pequena padronizada
            text_color="#6B7280"  # ✅ Cor secundária padronizada
        ).pack(pady=(0, 15))

        # Status badge
        info_status = STATUS_COLORS.get(status, {"bg": "#F3F4F6", "text": "#374151"})
        status_badge = ctk.CTkFrame(
            scroll,
            fg_color=info_status["bg"],
            corner_radius=12,
            height=26
        )
        status_badge.pack(pady=(0, 20))
        
        ctk.CTkLabel(
            status_badge,
            text=status,
            text_color=info_status["text"],
            font=font("small", "bold"),  # ✅ Fonte pequena negrito padronizada
            padx=12
        ).pack(pady=4)

        # Divisor
        ctk.CTkFrame(scroll, height=1, fg_color="#E5E7EB").pack(fill="x", pady=10)

        # Informações pessoais
        self._secao_titulo(scroll, "Informações Pessoais")

        info_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        info_grid.pack(fill="x", pady=(0, 15))

        info_items = [
            ("📞 Telefone", telefone or "Não informado"),
            ("🎂 Idade", f"{idade} anos" if idade else "Não informado"),
            ("⚥ Sexo", sexo or "Não informado"),
            ("🆔 CPF", cpf or "Não informado"),
        ]

        for i, (label, value) in enumerate(info_items):
            row_frame = ctk.CTkFrame(info_grid, fg_color="transparent")
            row_frame.pack(fill="x", pady=4)
            
            ctk.CTkLabel(
                row_frame,
                text=label,
                font=font("small", "bold"),  # ✅ Fonte pequena negrito padronizada
                text_color="#6B7280",  # ✅ Cor secundária padronizada
                width=80
            ).pack(side="left")
            
            ctk.CTkLabel(
                row_frame,
                text=value,
                font=font("small"),  # ✅ Fonte pequena padronizada
                text_color="#111827"  # ✅ Cor principal padronizada
            ).pack(side="left", padx=(10, 0))

        # Divisor
        ctk.CTkFrame(scroll, height=1, fg_color="#E5E7EB").pack(fill="x", pady=15)

        # Detalhes da consulta
        self._secao_titulo(scroll, "Detalhes da Consulta")

        consulta_box = ctk.CTkFrame(
            scroll,
            fg_color="#F9FAFB",
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB"
        )
        consulta_box.pack(fill="x", pady=(0, 20))

        consulta_info = f"📅 Data: {data}\n⏰ Horário: {hora}\n📝 Observações: {observacoes or 'Nenhuma'}"

        ctk.CTkLabel(
            consulta_box,
            text=consulta_info,
            justify="left",
            font=font("text"),  # ✅ Fonte padronizada
            text_color="#374151"
        ).pack(anchor="w", padx=15, pady=15)

        # Botões de ação
        button_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="✏️ Editar Paciente",
            fg_color="#F9FAFB",
            text_color="#374151",
            border_width=1,
            border_color="#E5E7EB",
            hover_color="#F3F4F6",
            height=40,  # ✅ Altura padronizada
            corner_radius=8,  # ✅ Cantos padronizados
            font=font("text")  # ✅ Fonte padronizada
        ).pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkButton(
            button_frame,
            text="📋 Nova Consulta",
            fg_color="#0EA5E9",  # ✅ Azul padronizado
            text_color="white",
            hover_color="#0284C7",  # ✅ Hover padronizado
            height=40,  # ✅ Altura padronizada
            corner_radius=8,  # ✅ Cantos padronizados
            font=font("text", "bold")  # ✅ Fonte negrito padronizada
        ).pack(side="left", expand=True, fill="x", padx=(5, 0))

    def _secao_titulo(self, parent, texto):
        """Título de seção padronizado"""
        ctk.CTkLabel(
            parent,
            text=texto,
            font=font("text", "bold"),  # ✅ Fonte text negrito padronizada
            text_color="#111827"  # ✅ Cor principal padronizada
        ).pack(anchor="w", pady=(0, 10))

    # ---------- LÓGICA ----------
    def selecionar_paciente(self, consulta_id):
        """Seleciona um paciente para ver detalhes"""
        self.paciente_selecionado = consulta_id
        self.render()

    def mudar_pagina(self, nova_pagina):
        """Muda a página da lista de consultas"""
        self.pagina_atual = nova_pagina
        self.paciente_selecionado = None
        self.render()