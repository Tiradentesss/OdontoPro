import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from .base import BaseScreen
from .theme import COLORS


class MedicosDisponibilidadeScreen(ctk.CTkFrame):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, fg_color=COLORS["bg"])

        self.clinica_id = clinica_id
        self.selected_medico = None
        self.selected_date = datetime.now().date()
        self.selected_slots = set()
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year

        self.colors = {
            "bg": COLORS["bg"],
            "card": COLORS["card"],
            "card_soft": COLORS["card_soft"],
            "primary": COLORS["primary"],
            "primary_dark": COLORS["primary_dark"],
            "primary_soft": COLORS["primary_soft"],
            "border": COLORS["border"],
            "text": COLORS["text"],
            "muted": COLORS["muted"],
            "header": COLORS["card_soft"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "danger": COLORS["danger"],
            "hover": COLORS["hover"],
            "selected_row": COLORS["selected_row"]
        }

        self.medicos = self._mock_medicos()
        self.slot_buttons = {}

        self._build_ui()

    # =========================================================
    # DADOS MOCK
    # =========================================================
    def _mock_medicos(self):
        return [
            {
                "id": 1,
                "nome": "Dr. João Pedro",
                "email": "joao@clinica.com",
                "especialidade": "Ortodontia",
                "status": "Ativo"
            },
            {
                "id": 2,
                "nome": "Dra. Mariana Silva",
                "email": "mariana@clinica.com",
                "especialidade": "Endodontia",
                "status": "Ativo"
            },
            {
                "id": 3,
                "nome": "Dr. Lucas Lima",
                "email": "lucas@clinica.com",
                "especialidade": "Implantodontia",
                "status": "Ativo"
            },
        ]

    # =========================================================
    # UI PRINCIPAL
    # =========================================================
    def _build_ui(self):
        self.pack(fill="both", expand=True)

        # Configurar grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Container principal com dois painéis lado a lado
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1, minsize=500)
        main_container.grid_columnconfigure(1, weight=1, minsize=500)

        self._build_left_panel(main_container)
        self._build_right_panel(main_container)

    # =========================================================
    # PAINEL ESQUERDO - MÉDICOS
    # =========================================================
    def _build_left_panel(self, parent):
        left_card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=24,
            border_width=1,
            border_color=self.colors["border"]
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left_card.grid_rowconfigure(2, weight=1)
        left_card.grid_columnconfigure(0, weight=1)

        # Título
        title_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Médicos da Clínica",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        title.pack(anchor="w")

        # Campo de pesquisa
        search_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 16))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=40,
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"],
            fg_color="#FFFFFF",
            text_color=self.colors["text"],
            placeholder_text="Pesquisar médico por nome ou especialidade...",
            placeholder_text_color=self.colors["muted"]
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_medicos())

        # Tabela de médicos
        self.medicos_list = ctk.CTkScrollableFrame(
            left_card,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=self.colors["primary_soft"],
            scrollbar_button_hover_color=self.colors["primary"]
        )
        self.medicos_list.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.medicos_list.grid_columnconfigure(0, weight=1)

        self._render_medicos()

    def _render_medicos(self):
        for widget in self.medicos_list.winfo_children():
            widget.destroy()

        busca = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""

        filtrados = []
        for medico in self.medicos:
            if (busca in medico["nome"].lower() or 
                busca in medico["email"].lower() or 
                busca in medico["especialidade"].lower()):
                filtrados.append(medico)

        if not filtrados:
            empty = ctk.CTkLabel(
                self.medicos_list,
                text="Nenhum médico encontrado.",
                text_color=self.colors["muted"],
                font=ctk.CTkFont(size=14)
            )
            empty.grid(row=0, column=0, pady=40)
            return

        for i, medico in enumerate(filtrados):
            is_selected = self.selected_medico and self.selected_medico["id"] == medico["id"]
            
            # Linha do médico
            row = ctk.CTkFrame(
                self.medicos_list,
                fg_color=self.colors["selected_row"] if is_selected else "#FFFFFF",
                corner_radius=12,
                border_width=1,
                border_color=self.colors["primary"] if is_selected else self.colors["border"],
                height=60
            )
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_propagate(False)
            
            # Configurar colunas
            row.grid_columnconfigure(0, weight=0, minsize=50)
            row.grid_columnconfigure(1, weight=1, minsize=240)
            row.grid_columnconfigure(2, weight=1, minsize=240)
            row.grid_columnconfigure(3, weight=1, minsize=180)
            row.grid_rowconfigure(0, weight=1)
            
            # Avatar
            avatar_img = self._create_avatar(medico["nome"], 32)
            avatar = ctk.CTkLabel(row, image=avatar_img, text="")
            avatar.image = avatar_img
            avatar.grid(row=0, column=0, padx=(12, 8), pady=14)
            
            # Nome
            nome = ctk.CTkLabel(
                row,
                text=medico["nome"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text"],
                anchor="w"
            )
            nome.grid(row=0, column=1, sticky="w", padx=8)
            
            # Email
            email = ctk.CTkLabel(
                row,
                text=medico["email"],
                font=ctk.CTkFont(size=13),
                text_color=self.colors["muted"],
                anchor="w"
            )
            email.grid(row=0, column=2, sticky="w", padx=8)
            
            # Especialidade
            especialidade = ctk.CTkLabel(
                row,
                text=medico["especialidade"],
                font=ctk.CTkFont(size=13),
                text_color=self.colors["muted"],
                anchor="w"
            )
            especialidade.grid(row=0, column=3, sticky="w", padx=8)
            
            # Bind de clique
            for widget in [row, avatar, nome, email, especialidade]:
                widget.bind("<Button-1>", lambda e, m=medico: self._select_medico(m))
                widget.bind("<Enter>", lambda e, r=row, s=is_selected: self._hover_row(r, s, True))
                widget.bind("<Leave>", lambda e, r=row, s=is_selected: self._hover_row(r, s, False))

    # =========================================================
    # PAINEL DIREITO - AGENDAMENTO
    # =========================================================
    def _build_right_panel(self, parent):
        self.right_card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=24,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.right_card.grid_rowconfigure(3, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        # Título
        title_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        
        self.right_title = ctk.CTkLabel(
            title_frame,
            text="Disponibilidade & Agendamento",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        self.right_title.pack(anchor="w")
        
        self.right_subtitle = ctk.CTkLabel(
            title_frame,
            text="Selecione um médico para configurar a agenda.",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["muted"]
        )
        self.right_subtitle.pack(anchor="w", pady=(4, 0))

        # Calendário
        self.calendar_card = ctk.CTkFrame(
            self.right_card,
            fg_color=self.colors["card_soft"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.calendar_card.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
        self._build_calendar()

        # Info da data selecionada
        info_card = ctk.CTkFrame(
            self.right_card,
            fg_color=self.colors["primary_soft"],
            corner_radius=12,
            border_width=0
        )
        info_card.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        
        self.date_info_label = ctk.CTkLabel(
            info_card,
            text=self._format_selected_date(),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary_dark"]
        )
        self.date_info_label.pack(padx=16, pady=12, anchor="w")

        # Horários disponíveis
        slots_container = ctk.CTkFrame(self.right_card, fg_color="transparent")
        slots_container.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 16))
        slots_container.grid_rowconfigure(1, weight=1)
        slots_container.grid_columnconfigure(0, weight=1)
        
        slots_title = ctk.CTkLabel(
            slots_container,
            text="Horários Disponíveis",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        slots_title.grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        self.slots_grid = ctk.CTkScrollableFrame(
            slots_container,
            fg_color=self.colors["card_soft"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"],
            scrollbar_button_color=self.colors["primary_soft"],
            scrollbar_button_hover_color=self.colors["primary"]
        )
        self.slots_grid.grid(row=1, column=0, sticky="nsew")
        
        # Configurar colunas do grid de horários
        for i in range(4):
            self.slots_grid.grid_columnconfigure(i, weight=1)
        self.slots_grid.grid_rowconfigure(0, weight=1)
        
        self._build_time_slots()

        # Rodapé com seleção e botão salvar
        footer = ctk.CTkFrame(self.right_card, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 20))
        footer.grid_columnconfigure(0, weight=1)
        
        self.selection_label = ctk.CTkLabel(
            footer,
            text="0 horários selecionados",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["muted"]
        )
        self.selection_label.grid(row=0, column=0, sticky="w")
        
        save_btn = ctk.CTkButton(
            footer,
            text="Salvar Disponibilidade",
            height=40,
            width=180,
            corner_radius=12,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save_disponibilidade
        )
        save_btn.grid(row=0, column=1, sticky="e")

    # =========================================================
    # CALENDÁRIO
    # =========================================================
    def _build_calendar(self):
        for widget in self.calendar_card.winfo_children():
            widget.destroy()

        # Cabeçalho do calendário
        header = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 12))
        
        # Botão anterior
        prev_btn = ctk.CTkButton(
            header,
            text="◀",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#FFFFFF",
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            hover_color=self.colors["hover"],
            font=ctk.CTkFont(size=14),
            command=self._prev_month
        )
        prev_btn.pack(side="left")
        
        # Mês/Ano
        month_label = ctk.CTkLabel(
            header,
            text=self._month_year_label(),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"]
        )
        month_label.pack(side="left", padx=12)
        
        # Botão próximo
        next_btn = ctk.CTkButton(
            header,
            text="▶",
            width=32,
            height=32,
            corner_radius=8,
            fg_color="#FFFFFF",
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            hover_color=self.colors["hover"],
            font=ctk.CTkFont(size=14),
            command=self._next_month
        )
        next_btn.pack(side="right")
        
        # Dias da semana
        days_frame = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        days_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        week_days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for col, day in enumerate(week_days):
            lbl = ctk.CTkLabel(
                days_frame,
                text=day,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["muted"]
            )
            lbl.grid(row=0, column=col, padx=4, pady=(0, 8), sticky="nsew")
            days_frame.grid_columnconfigure(col, weight=1)
        
        # Dias do mês
        first_day = datetime(self.current_year, self.current_month, 1).date()
        start_weekday = first_day.weekday()
        last_day = self._last_day_of_month(self.current_year, self.current_month)
        
        row = 1
        col = start_weekday
        
        for day_num in range(1, last_day + 1):
            current_date = datetime(self.current_year, self.current_month, day_num).date()
            is_today = current_date == datetime.now().date()
            is_selected = current_date == self.selected_date
            
            btn = ctk.CTkButton(
                days_frame,
                text=str(day_num),
                width=40,
                height=36,
                corner_radius=10,
                fg_color=self.colors["primary"] if is_selected else ("#F0F8FF" if is_today else "#FFFFFF"),
                text_color="#FFFFFF" if is_selected else self.colors["text"],
                border_width=1,
                border_color=self.colors["primary"] if is_selected else self.colors["border"],
                hover_color=self.colors["hover"],
                font=ctk.CTkFont(size=13),
                command=lambda d=current_date: self._select_date(d)
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    # =========================================================
    # HORÁRIOS
    # =========================================================
    def _build_time_slots(self):
        for widget in self.slots_grid.winfo_children():
            widget.destroy()
        
        self.slot_buttons = {}
        self.selected_slots.clear()
        
        # Horários disponíveis (baseado na imagem)
        horarios = [
            "08:00", "08:30", "09:00", "09:30",
            "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30",
            "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30"
        ]
        
        for index, horario in enumerate(horarios):
            row = index // 4
            col = index % 4
            
            btn = ctk.CTkButton(
                self.slots_grid,
                text=horario,
                height=38,
                corner_radius=10,
                fg_color="#FFFFFF",
                text_color=self.colors["text"],
                border_width=1,
                border_color=self.colors["border"],
                hover_color=self.colors["hover"],
                font=ctk.CTkFont(size=13),
                command=lambda h=horario: self._toggle_slot(h)
            )
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            
            self.slot_buttons[horario] = btn

    # =========================================================
    # AÇÕES
    # =========================================================
    def _select_medico(self, medico):
        self.selected_medico = medico
        self.right_subtitle.configure(
            text=f"Configurando agenda de {medico['nome']}."
        )
        self._render_medicos()

    def _select_date(self, selected_date):
        self.selected_date = selected_date
        self.date_info_label.configure(text=self._format_selected_date())
        self._build_calendar()
        self._build_time_slots()

    def _toggle_slot(self, horario):
        if horario in self.selected_slots:
            self.selected_slots.remove(horario)
            btn = self.slot_buttons[horario]
            btn.configure(
                fg_color="#FFFFFF",
                text_color=self.colors["text"],
                border_color=self.colors["border"]
            )
        else:
            self.selected_slots.add(horario)
            btn = self.slot_buttons[horario]
            btn.configure(
                fg_color=self.colors["primary"],
                text_color="#FFFFFF",
                border_color=self.colors["primary"]
            )
        
        qtd = len(self.selected_slots)
        self.selection_label.configure(
            text=f"{qtd} horário{'s' if qtd != 1 else ''} selecionado{'s' if qtd != 1 else ''}"
        )

    def _save_disponibilidade(self):
        if not self.selected_medico:
            messagebox.showwarning("Aviso", "Selecione um médico primeiro.")
            return
        
        if not self.selected_slots:
            messagebox.showwarning("Aviso", "Selecione pelo menos um horário.")
            return
        
        horarios = ", ".join(sorted(self.selected_slots))
        data_formatada = self.selected_date.strftime("%d/%m/%Y")
        
        messagebox.showinfo(
            "Disponibilidade salva",
            f"Médico: {self.selected_medico['nome']}\n"
            f"Data: {data_formatada}\n"
            f"Horários: {horarios}"
        )

    def _prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._build_calendar()

    def _next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._build_calendar()

    # =========================================================
    # HELPERS
    # =========================================================
    def _hover_row(self, row, is_selected, entering):
        if entering:
            if not is_selected:
                row.configure(fg_color=self.colors["hover"])
        else:
            row.configure(fg_color=self.colors["selected_row"] if is_selected else "#FFFFFF")

    def _create_avatar(self, nome, size):
        inicial = nome[0].upper() if nome else "?"
        bg_color = "#4db8ff"
        
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill=bg_color)
        
        try:
            font_pil = ImageFont.truetype("arial.ttf", int(size * 0.45))
        except Exception:
            font_pil = ImageFont.load_default()
        
        draw.text((size / 2, size / 2), inicial, fill="white", font=font_pil, anchor="mm")
        return ctk.CTkImage(light_image=img, size=(size, size))

    def _last_day_of_month(self, year, month):
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        return (next_month - timedelta(days=1)).day

    def _month_year_label(self):
        meses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        return f"{meses[self.current_month - 1]} {self.current_year}"

    def _format_selected_date(self):
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", 
                "Sexta-feira", "Sábado", "Domingo"]
        nome_dia = dias[self.selected_date.weekday()]
        return f"Data selecionada: {nome_dia}, {self.selected_date.strftime('%d/%m/%Y')}"


class Gerenciamento(BaseScreen):
    """Wrapper que integra MedicosDisponibilidadeScreen ao sistema de telas"""
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, "Gerenciamento")
        
        # Remove o padding padrão do BaseScreen para dar espaço total à tela de disponibilidade
        if hasattr(self, 'content_card'):
            self.content_card.pack_forget()
        
        # Coloca a tela de disponibilidade diretamente no frame raiz
        screen = MedicosDisponibilidadeScreen(self, clinica_id=clinica_id)
        screen.pack(fill="both", expand=True)