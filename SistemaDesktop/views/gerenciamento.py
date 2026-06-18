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
        self.selected_dates = set()
        self.last_selected_date = None
        self.selected_slots = set()
        self.last_selected_slot = None
        self.current_month = self.selected_date.month
        self.current_year = self.selected_date.year
        self.date_buttons = {}
        
        # Paginação de médicos
        self.medicos_por_pagina = 7
        self.pagina_atual = 0
        self.total_medicos_filtrados = 0

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

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=24, pady=(40, 24))
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1, minsize=500)
        main_container.grid_columnconfigure(1, weight=1, minsize=500)

        self._build_left_panel(main_container)
        self._build_right_panel(main_container)

    def _build_left_panel(self, parent):
        left_card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=24,
            border_width=1,
            border_color=self.colors["border"]
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=10)
        left_card.grid_rowconfigure(2, weight=1)
        left_card.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 12))
        
        title = ctk.CTkLabel(
            title_frame,
            text="Médicos da Clínica",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        title.pack(anchor="w")

        search_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            height=40,
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=self.colors["card_soft"],
            text_color=self.colors["text"],
            placeholder_text="Pesquisar médico por nome ou especialidade...",
            placeholder_text_color=self.colors["muted"]
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_medicos())

        self.medicos_list = ctk.CTkFrame(
            left_card,
            fg_color="transparent",
            corner_radius=0
        )
        self.medicos_list.grid(row=2, column=0, sticky="nsew", padx=16, pady=(16, 12))
        self.medicos_list.grid_columnconfigure(0, weight=1)

        # Container para abas de paginação
        self.pagination_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        self.pagination_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(16, 20))
        self.pagination_frame.grid_columnconfigure(0, weight=1)
        
        self.pagination_buttons = {}

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

        self.total_medicos_filtrados = len(filtrados)
        
        # Resetar página se busca mudou
        if busca and self.pagina_atual > 0:
            self.pagina_atual = 0

        # Calcular paginação
        total_paginas = (self.total_medicos_filtrados + self.medicos_por_pagina - 1) // self.medicos_por_pagina
        if self.pagina_atual >= total_paginas and total_paginas > 0:
            self.pagina_atual = total_paginas - 1

        inicio = self.pagina_atual * self.medicos_por_pagina
        fim = inicio + self.medicos_por_pagina
        medicos_pagina = filtrados[inicio:fim]

        # Atualizar abas de paginação
        self._update_pagination_tabs(total_paginas)

        if not medicos_pagina:
            empty = ctk.CTkLabel(
                self.medicos_list,
                text="Nenhum médico encontrado." if filtrados else "Nenhum médico cadastrado.",
                text_color=self.colors["muted"],
                font=ctk.CTkFont(size=14)
            )
            empty.grid(row=0, column=0, pady=40)
            return

        for i, medico in enumerate(medicos_pagina):
            is_selected = self.selected_medico and self.selected_medico["id"] == medico["id"]
            
            row = ctk.CTkFrame(
                self.medicos_list,
                fg_color=self.colors["selected_row"] if is_selected else self.colors["card"],
                corner_radius=12,
                border_width=1,
                border_color=self.colors["primary"] if is_selected else self.colors["border"],
                height=60
            )
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_propagate(False)
            
            row.grid_columnconfigure(0, weight=0, minsize=50)
            row.grid_columnconfigure(1, weight=1, minsize=240)
            row.grid_columnconfigure(2, weight=1, minsize=240)
            row.grid_columnconfigure(3, weight=1, minsize=180)
            row.grid_rowconfigure(0, weight=1)
            
            avatar_img = self._create_avatar(medico["nome"], 32)
            avatar = ctk.CTkLabel(row, image=avatar_img, text="")
            avatar.image = avatar_img
            avatar.grid(row=0, column=0, padx=(12, 8), pady=14)
            
            nome = ctk.CTkLabel(
                row,
                text=medico["nome"],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text"],
                anchor="w"
            )
            nome.grid(row=0, column=1, sticky="w", padx=8)
            
            email = ctk.CTkLabel(
                row,
                text=medico["email"],
                font=ctk.CTkFont(size=13),
                text_color=self.colors["muted"],
                anchor="w"
            )
            email.grid(row=0, column=2, sticky="w", padx=8)
            
            especialidade = ctk.CTkLabel(
                row,
                text=medico["especialidade"],
                font=ctk.CTkFont(size=13),
                text_color=self.colors["muted"],
                anchor="w"
            )
            especialidade.grid(row=0, column=3, sticky="w", padx=8)
            
            for widget in [row, avatar, nome, email, especialidade]:
                widget.bind("<Button-1>", lambda e, m=medico: self._select_medico(m))
                widget.bind("<Enter>", lambda e, r=row, s=is_selected: self._hover_row(r, s, True))
                widget.bind("<Leave>", lambda e, r=row, s=is_selected: self._hover_row(r, s, False))

    def _update_pagination_tabs(self, total_paginas):
        """Atualiza as abas de paginação com números"""
        # Limpar abas anteriores
        for widget in self.pagination_frame.winfo_children():
            widget.destroy()
        self.pagination_buttons = {}

        if total_paginas <= 1:
            return

        # Criar container interno para centralizar abas
        tabs_container = ctk.CTkFrame(self.pagination_frame, fg_color="transparent")
        tabs_container.pack(pady=8)

        # Criar abas com números
        for pagina_num in range(total_paginas):
            is_current = pagina_num == self.pagina_atual
            
            tab_btn = ctk.CTkButton(
                tabs_container,
                text=str(pagina_num + 1),
                width=36,
                height=36,
                corner_radius=8,
                fg_color=self.colors["primary"] if is_current else self.colors["card"],
                text_color="white" if is_current else self.colors["text"],
                border_width=1 if is_current else 0,
                border_color=self.colors["primary"] if is_current else self.colors["border"],
                hover_color=self.colors["primary_dark"] if is_current else self.colors["hover"],
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda p=pagina_num: self._go_to_page(p)
            )
            tab_btn.pack(side="left", padx=4)
            self.pagination_buttons[pagina_num] = tab_btn

    def _go_to_page(self, pagina_num):
        """Navega para a página especificada"""
        self.pagina_atual = pagina_num
        self._render_medicos()

    def _prev_page_medicos(self):
        if self.pagina_atual > 0:
            self.pagina_atual -= 1
            self._render_medicos()

    def _next_page_medicos(self):
        total_paginas = (self.total_medicos_filtrados + self.medicos_por_pagina - 1) // self.medicos_por_pagina
        if self.pagina_atual < total_paginas - 1:
            self.pagina_atual += 1
            self._render_medicos()

    def _build_right_panel(self, parent):
        self.right_card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=24,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=10)
        self.right_card.grid_rowconfigure(3, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 12))
        
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
        
        tip_label = ctk.CTkLabel(
            title_frame,
            text="💡 Dica: Use Shift + Clique para selecionar intervalos de datas/horários",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["success"]
        )
        tip_label.pack(anchor="w", pady=(6, 0))

        self.calendar_card = ctk.CTkFrame(
            self.right_card,
            fg_color=self.colors["card_soft"],
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.calendar_card.grid(row=1, column=0, sticky="ew", padx=16, pady=(12, 16))
        self._build_calendar()

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
            text_color=self.colors["primary"] if self._is_dark_theme() else self.colors["primary_dark"]
        )
        self.date_info_label.pack(padx=16, pady=12, anchor="w")

        slots_container = ctk.CTkFrame(self.right_card, fg_color="transparent")
        slots_container.grid(row=3, column=0, sticky="nsew", padx=16, pady=(12, 20))
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
            border_color=self.colors["border"]
        )
        self.slots_grid.grid(row=1, column=0, sticky="nsew")
        
        for i in range(4):
            self.slots_grid.grid_columnconfigure(i, weight=1)
        
        self._build_time_slots()

        footer = ctk.CTkFrame(self.right_card, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 28))
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
            height=38,
            width=160,
            corner_radius=12,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._save_disponibilidade
        )
        save_btn.grid(row=0, column=1, sticky="e")

    def _build_calendar(self):
        for widget in self.calendar_card.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.calendar_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(16, 12))
        
        prev_btn = ctk.CTkButton(
            header,
            text="◀",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=self.colors["card"],
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            hover_color=self.colors["hover"],
            font=ctk.CTkFont(size=14),
            command=self._prev_month
        )
        prev_btn.pack(side="left")
        
        month_label = ctk.CTkLabel(
            header,
            text=self._month_year_label(),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=self.colors["text"]
        )
        month_label.pack(side="left", padx=12)
        
        next_btn = ctk.CTkButton(
            header,
            text="▶",
            width=32,
            height=32,
            corner_radius=8,
            fg_color=self.colors["card"],
            text_color=self.colors["text"],
            border_width=1,
            border_color=self.colors["border"],
            hover_color=self.colors["hover"],
            font=ctk.CTkFont(size=14),
            command=self._next_month
        )
        next_btn.pack(side="right")
        
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
        
        first_day = datetime(self.current_year, self.current_month, 1).date()
        start_weekday = first_day.weekday()
        last_day = self._last_day_of_month(self.current_year, self.current_month)
        
        self.date_buttons = {}
        row = 1
        col = start_weekday
        
        for day_num in range(1, last_day + 1):
            current_date = datetime(self.current_year, self.current_month, day_num).date()
            is_today = current_date == datetime.now().date()
            is_selected = current_date in self.selected_dates
            is_sunday = current_date.weekday() == 6
            
            btn = ctk.CTkButton(
                days_frame,
                text=str(day_num),
                width=40,
                height=36,
                corner_radius=10,
                fg_color=self._get_date_button_color(is_selected, is_today, is_sunday),
                text_color=self._get_date_text_color(is_selected, is_sunday),
                border_width=1,
                border_color=self.colors["primary"] if is_selected else self.colors["border"],
                hover_color=self.colors["hover"] if not is_sunday else self.colors["card_soft"],
                font=ctk.CTkFont(size=13),
                state="disabled" if is_sunday else "normal"
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            
            if not is_sunday:
                btn.bind("<Button-1>", lambda e, d=current_date: self._on_date_clicked(e, d))
            
            self.date_buttons[current_date] = btn
            
            col += 1
            if col > 6:
                col = 0
                row += 1

    def _is_dark_theme(self):
        """Detecta se está usando tema escuro baseado na cor de fundo"""
        bg_color = self.colors["bg"]
        # Se a cor de fundo for escura (RGB baixo), é tema escuro
        if bg_color.startswith('#'):
            # Remove o # e converte para RGB
            hex_color = bg_color.lstrip('#')
            if len(hex_color) == 6:
                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                # Se a média for menor que 128, considera tema escuro
                return (r + g + b) / 3 < 128
        return False

    def _get_date_button_color(self, is_selected, is_today, is_sunday):
        """Retorna a cor de fundo correta para botões de data"""
        if is_sunday:
            return self.colors["card_soft"]
        elif is_selected:
            return self.colors["primary"]
        elif is_today:
            return self.colors["primary_soft"]
        else:
            return self.colors["card"]

    def _get_date_text_color(self, is_selected, is_sunday):
        """Retorna a cor do texto correta para botões de data"""
        if is_sunday:
            return self.colors["muted"]
        elif is_selected:
            return "white"
        else:
            return self.colors["text"]

    def _build_time_slots(self):
        for widget in self.slots_grid.winfo_children():
            widget.destroy()
        
        self.slot_buttons = {}
        
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
            
            is_selected = horario in self.selected_slots
            
            btn = ctk.CTkButton(
                self.slots_grid,
                text=horario,
                height=38,
                corner_radius=10,
                fg_color=self.colors["primary"] if is_selected else self.colors["card"],
                text_color="white" if is_selected else self.colors["text"],
                border_width=1,
                border_color=self.colors["primary"] if is_selected else self.colors["border"],
                hover_color=self.colors["hover"],
                font=ctk.CTkFont(size=13)
            )
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            btn.bind("<Button-1>", lambda e, h=horario: self._on_slot_clicked(e, h))
            
            self.slot_buttons[horario] = btn

    def _on_date_clicked(self, event, selected_date):
        shift_pressed = (event.state & 0x1) != 0
        
        if shift_pressed and self.last_selected_date:
            self._toggle_date_range(self.last_selected_date, selected_date)
        else:
            if selected_date in self.selected_dates:
                self.selected_dates.remove(selected_date)
            else:
                self.selected_dates.add(selected_date)
        
        self.last_selected_date = selected_date
        self._update_calendar_display()
        self._update_date_info()

    def _toggle_date_range(self, start_date, end_date):
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        interval_dates = set()
        current = start_date
        while current <= end_date:
            if current.weekday() != 6:
                interval_dates.add(current)
            current += timedelta(days=1)
        
        if interval_dates.issubset(self.selected_dates):
            self.selected_dates -= interval_dates
        else:
            self.selected_dates.update(interval_dates)

    def _update_calendar_display(self):
        for date, btn in self.date_buttons.items():
            is_selected = date in self.selected_dates
            is_today = date == datetime.now().date()
            is_sunday = date.weekday() == 6
            
            btn.configure(
                fg_color=self._get_date_button_color(is_selected, is_today, is_sunday),
                text_color=self._get_date_text_color(is_selected, is_sunday),
                border_color=self.colors["primary"] if is_selected else self.colors["border"],
                state="disabled" if is_sunday else "normal"
            )

    def _update_date_info(self):
        if not self.selected_dates:
            self.date_info_label.configure(text="Nenhuma data selecionada")
        elif len(self.selected_dates) == 1:
            date = list(self.selected_dates)[0]
            self.date_info_label.configure(text=self._format_date(date))
        else:
            dates_sorted = sorted(list(self.selected_dates))
            primeira = dates_sorted[0]
            ultima = dates_sorted[-1]
            self.date_info_label.configure(
                text=f"Período: {primeira.strftime('%d/%m/%Y')} até {ultima.strftime('%d/%m/%Y')} ({len(self.selected_dates)} dias)"
            )

    def _on_slot_clicked(self, event, horario):
        shift_pressed = (event.state & 0x1) != 0
        
        horarios_list = [
            "08:00", "08:30", "09:00", "09:30",
            "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30",
            "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30"
        ]
        
        if shift_pressed and self.last_selected_slot and self.last_selected_slot in horarios_list:
            self._toggle_slot_range(self.last_selected_slot, horario)
        else:
            if horario in self.selected_slots:
                self.selected_slots.remove(horario)
            else:
                self.selected_slots.add(horario)
        
        self.last_selected_slot = horario
        self._update_slots_display()

    def _update_slots_display(self):
        for horario, btn in self.slot_buttons.items():
            is_selected = horario in self.selected_slots
            
            btn.configure(
                fg_color=self.colors["primary"] if is_selected else self.colors["card"],
                text_color="white" if is_selected else self.colors["text"],
                border_color=self.colors["primary"] if is_selected else self.colors["border"]
            )
        
        qtd = len(self.selected_slots)
        self.selection_label.configure(
            text=f"{qtd} horário{'s' if qtd != 1 else ''} selecionado{'s' if qtd != 1 else ''}"
        )

    def _toggle_slot_range(self, start_horario, end_horario):
        horarios_list = [
            "08:00", "08:30", "09:00", "09:30",
            "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30",
            "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30"
        ]
        
        start_idx = horarios_list.index(start_horario)
        end_idx = horarios_list.index(end_horario)
        
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx
        
        interval_slots = set(horarios_list[start_idx:end_idx + 1])
        
        if interval_slots.issubset(self.selected_slots):
            self.selected_slots -= interval_slots
        else:
            self.selected_slots.update(interval_slots)

    def _select_medico(self, medico):
        self.selected_medico = medico
        self.right_subtitle.configure(
            text=f"Configurando agenda de {medico['nome']}."
        )
        self._render_medicos()

    def _save_disponibilidade(self):
        if not self.selected_medico:
            messagebox.showwarning("Aviso", "Selecione um médico primeiro.")
            return
        
        if not self.selected_dates:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma data.")
            return
        
        if not self.selected_slots:
            messagebox.showwarning("Aviso", "Selecione pelo menos um horário.")
            return
        
        horarios = ", ".join(sorted(self.selected_slots))
        datas_sorted = sorted(list(self.selected_dates))
        
        if len(datas_sorted) == 1:
            datas_str = datas_sorted[0].strftime("%d/%m/%Y")
        else:
            datas_str = f"{datas_sorted[0].strftime('%d/%m/%Y')} até {datas_sorted[-1].strftime('%d/%m/%Y')} ({len(datas_sorted)} dias)"
        
        messagebox.showinfo(
            "Disponibilidade salva",
            f"Médico: {self.selected_medico['nome']}\n"
            f"Datas: {datas_str}\n"
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

    def _format_date(self, date):
        dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", 
                "Sexta-feira", "Sábado", "Domingo"]
        nome_dia = dias[date.weekday()]
        return f"Data selecionada: {nome_dia}, {date.strftime('%d/%m/%Y')}"

    def _hover_row(self, row, is_selected, entering):
        if entering:
            if not is_selected:
                row.configure(fg_color=self.colors["hover"])
        else:
            row.configure(fg_color=self.colors["selected_row"] if is_selected else self.colors["card"])

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
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, "Gerenciamento")
        
        if hasattr(self, 'content_card'):
            self.content_card.pack_forget()
        
        screen = MedicosDisponibilidadeScreen(self, clinica_id=clinica_id)
        screen.pack(fill="both", expand=True)