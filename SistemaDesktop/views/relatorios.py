import calendar
import csv
import math
import os
import queue
import threading
import zipfile
from datetime import datetime, timedelta
from tkinter import Menu, filedialog
from xml.sax.saxutils import escape as xml_escape

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from config.database import get_connection
from .base import BaseScreen
from .theme import FONT_FAMILY, font, COLORS, INNER_CARD_BORDER, INNER_CARD_RADIUS, get_dark_mode
from controllers.consulta_controller import ConsultaController
from controllers.relatorios_controller import RelatoriosController


class Relatorios(BaseScreen):
    def __init__(self, parent, clinica_id=None, on_initialization_complete=None):
        super().__init__(parent, "Relatórios")

        self.clinica_id = clinica_id
        self._on_initialization_complete = on_initialization_complete
        self._initialization_reported = False
        self._initialization_thread = None
        self._loading = False
        self._load_queue = queue.Queue()
        self._current_thread_id = 0
        self._timeout_id = None
        self._loading_animation_id = None
        self._loading_dot_count = 0
        self._cache = {}
        self._medicos_map = {"Todos": None}
        self._especialidades_map = {"Todos": None}
        self._current_report_data = None
        self.export_button = None
        self._export_menu = None
        self._chart_hover_connection_id = None
        self._chart_bar_tooltip = None
        self._custom_period_modal = None
        self._custom_period_previous_value = "Hoje"
        self.custom_date_start = None
        self.custom_date_end = None

        self.periodo_var = ctk.StringVar(value="Hoje")
        self.medico_var = ctk.StringVar(value="Todos")
        self.especialidade_var = ctk.StringVar(value="Todos")
        self.status_var = ctk.StringVar(value="Todos")

        self.main_container = self.content_card

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_structure()
        self._load_data_async()

    def _build_structure(self):
        self._export_menu = Menu(self.scroll_frame, tearoff=0)
        self._export_menu.add_command(label="Exportar para PDF", command=lambda: self._export_report("pdf"))
        self._export_menu.add_command(label="Exportar para Excel (.xlsx)", command=lambda: self._export_report("xlsx"))
        self._export_menu.add_command(label="Exportar para CSV", command=lambda: self._export_report("csv"))

        filters_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        filters_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        filters_header = ctk.CTkLabel(
            filters_frame,
            text="Filtros",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        )
        filters_header.pack(anchor="w", padx=20, pady=(20, 10))

        form_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=(0, 20))
        form_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="filter_cols")

        periodo_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        periodo_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        periodo_label_frame = ctk.CTkFrame(periodo_frame, fg_color="transparent")
        periodo_label_frame.pack(anchor="w", padx=10, pady=(12, 0))
        ctk.CTkLabel(periodo_label_frame, text="📅", font=ctk.CTkFont(size=28, weight="normal"), text_color=COLORS["primary"]).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(periodo_label_frame, text="Período", font=ctk.CTkFont(size=14, weight='normal'), text_color=COLORS["text_primary"]).pack(side="left")
        self.periodo_combo = ctk.CTkComboBox(
            periodo_frame,
            values=["Hoje", "Semanal", "Mensal", "Anual", "Personalizado"],
            height=34,
            corner_radius=8,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1,
            command=self._handle_period_change,
        )
        self.periodo_combo.set(self.periodo_var.get())
        self.periodo_combo.pack(fill="x", padx=10, pady=(6, 10))

        medico_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        medico_frame.grid(row=0, column=1, sticky="nsew", padx=8, pady=0)
        medico_label_frame = ctk.CTkFrame(medico_frame, fg_color="transparent")
        medico_label_frame.pack(anchor="w", padx=10, pady=(12, 0))
        ctk.CTkLabel(medico_label_frame, text="🩺", font=ctk.CTkFont(size=28, weight="normal"), text_color=COLORS["primary"]).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(medico_label_frame, text="Médico", font=ctk.CTkFont(size=14, weight='normal'), text_color=COLORS["text_primary"]).pack(side="left")
        self.medico_combo = ctk.CTkComboBox(
            medico_frame,
            values=["Todos"],
            height=34,
            corner_radius=8,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.medico_combo.set(self.medico_var.get())
        self.medico_combo.pack(fill="x", padx=10, pady=(6, 10))

        especialidade_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        especialidade_frame.grid(row=0, column=2, sticky="nsew", padx=8, pady=0)
        especialidade_label_frame = ctk.CTkFrame(especialidade_frame, fg_color="transparent")
        especialidade_label_frame.pack(anchor="w", padx=10, pady=(12, 0))
        ctk.CTkLabel(especialidade_label_frame, text="🦷", font=ctk.CTkFont(size=28, weight="normal"), text_color=COLORS["primary"]).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(especialidade_label_frame, text="Especialidade", font=ctk.CTkFont(size=14, weight='normal'), text_color=COLORS["text_primary"]).pack(side="left")
        self.especialidade_combo = ctk.CTkComboBox(
            especialidade_frame,
            values=["Todos"],
            height=34,
            corner_radius=8,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.especialidade_combo.set(self.especialidade_var.get())
        self.especialidade_combo.pack(fill="x", padx=10, pady=(6, 10))

        status_frame = ctk.CTkFrame(form_frame, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=INNER_CARD_BORDER)
        status_frame.grid(row=0, column=3, sticky="nsew", padx=(8, 0), pady=0)
        status_label_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_label_frame.pack(anchor="w", padx=10, pady=(12, 0))
        ctk.CTkLabel(status_label_frame, text="📊", font=ctk.CTkFont(size=28, weight="normal"), text_color=COLORS["primary"]).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(status_label_frame, text="Status", font=ctk.CTkFont(size=14, weight='normal'), text_color=COLORS["text_primary"]).pack(side="left")
        self.status_combo = ctk.CTkComboBox(
            status_frame,
            values=["Todos", "Agendada", "Realizada", "Cancelada", "Falta"],
            height=34,
            corner_radius=8,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            width=1
        )
        self.status_combo.set(self.status_var.get())
        self.status_combo.pack(fill="x", padx=10, pady=(6, 10))

        action_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(0, 20))
        self.update_button = ctk.CTkButton(
            action_frame,
            text="Atualizar Relatório",
            width=180,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            corner_radius=12,
            command=self._load_data_async
        )
        self.update_button.pack(side="right")

        self._loading_label = ctk.CTkLabel(
            filters_frame,
            text="",
            font=font("small"),
            text_color=COLORS["text_secondary"]
        )
        self._loading_label.pack(anchor="w", padx=20, pady=(0, 10))
        self._loading_label.pack_forget()

        self.kpi_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=20, pady=(0, 12))
        for idx in range(4):
            self.kpi_frame.grid_columnconfigure(idx, weight=1, uniform="kpi_cards")

        self._kpi_card_labels = {}
        kpi_cards = [
            ("\uE787", "Total de Consultas", "total_consultas", "No período selecionado"),
            ("\uE73E", "Taxa de Comparecimento", "taxa_comparecimento", "Consultas realizadas"),
            ("\uE711", "Taxa de Cancelamento", "taxa_cancelamento", "Consultas canceladas"),
            ("\uE7C1", "Médico em Destaque", "medico_mais_produtivo", "Nenhuma consulta encontrada"),
        ]

        for index, (glyph, title, key, description) in enumerate(kpi_cards):
            card = ctk.CTkFrame(
                self.kpi_frame,
                fg_color=COLORS["card"],
                corner_radius=INNER_CARD_RADIUS,
                border_width=1,
                border_color=INNER_CARD_BORDER
            )
            card.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < len(kpi_cards) - 1 else 0)

            ctk.CTkLabel(card, text=glyph, font=ctk.CTkFont(size=24, weight="normal"), text_color=COLORS["primary"]).pack(anchor="w", padx=16, pady=(12, 3))

            ctk.CTkLabel(card, text=title, font=font("small", "bold"), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=16, pady=(3, 0))

            if key == "medico_mais_produtivo":
                value_label = ctk.CTkLabel(card, text="--", font=font("text", "bold"), text_color=COLORS["text"], wraplength=180, justify="left")
                value_label.pack(anchor="w", padx=16, pady=(6, 3))
            else:
                value_label = ctk.CTkLabel(card, text="--", font=font("title", "bold"), text_color=COLORS["text"])
                value_label.pack(anchor="w", padx=16, pady=(6, 1))

            desc_label = ctk.CTkLabel(card, text=description, font=font("small"), text_color=COLORS["text_secondary"])
            desc_label.pack(anchor="w", padx=16, pady=(0, 10))

            self._kpi_card_labels[key] = {
                "value": value_label,
                "description": desc_label,
            }

        self.chart_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.chart_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.chart_card,
            text="Consultas por Período",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self._chart_canvas_container = ctk.CTkFrame(self.chart_card, fg_color=COLORS["card"], corner_radius=10)
        self._chart_canvas_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.specialty_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.specialty_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.specialty_card,
            text="Consultas por Especialidade",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        self._specialty_canvas_container = ctk.CTkFrame(self.specialty_card, fg_color=COLORS["card"], corner_radius=10)
        self._specialty_canvas_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.productivity_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.productivity_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            self.productivity_card,
            text="Médicos em Destaque",
            font=font("subtitle", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(20, 10))

        table_header = ctk.CTkFrame(self.productivity_card, fg_color=COLORS["card_soft"], corner_radius=12)
        table_header.pack(fill="x", padx=(20, 16), pady=(0, 8))
        table_header.grid_columnconfigure(0, weight=1, uniform="ranking_cols")
        table_header.grid_columnconfigure(1, weight=4, uniform="ranking_cols")
        table_header.grid_columnconfigure(2, weight=3, uniform="ranking_cols")
        table_header.grid_columnconfigure(3, weight=1, uniform="ranking_cols")
        table_header.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(table_header, text="Posição", font=font("small", "bold"), text_color=COLORS["text_secondary"], anchor="center").grid(row=0, column=0, sticky="nsew", padx=(12, 8), pady=(12, 10))
        ctk.CTkLabel(table_header, text="Nome", font=font("small", "bold"), text_color=COLORS["text_secondary"], anchor="w").grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=(12, 10))

        specialty_header_cell = ctk.CTkFrame(table_header, fg_color="transparent")
        specialty_header_cell.grid(row=0, column=2, sticky="nsew", padx=(0, 8), pady=(12, 10))
        specialty_header_cell.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(specialty_header_cell, text="Especialidade", font=font("small", "bold"), text_color=COLORS["text_secondary"], anchor="w", justify="left").grid(row=0, column=0, sticky="nsew", padx=(12, 0))

        consult_header_cell = ctk.CTkFrame(table_header, fg_color="transparent")
        consult_header_cell.grid(row=0, column=3, sticky="nsew", padx=(0, 12), pady=(12, 10))
        consult_header_cell.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(consult_header_cell, text="Consultas", font=font("small", "bold"), text_color=COLORS["text_secondary"], anchor="center", justify="center").grid(row=0, column=0, sticky="nsew")

        self._productivity_rows_frame = ctk.CTkFrame(self.productivity_card, fg_color="transparent")
        self._productivity_rows_frame.pack(fill="both", expand=True, padx=(20, 16), pady=(0, 20))

        stats_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        stats_frame.pack(fill="x", padx=20, pady=(0, 20))
        for idx in range(4):
            stats_frame.grid_columnconfigure(idx, weight=1, uniform="small_stats")

        self._stat_value_labels = {}
        stats = [
            ("Pacientes Únicos Atendidos", "0"),
            ("Faltas", "0"),
            ("Novos Pacientes", "0"),
            ("Consultas Agendadas", "0"),
        ]

        for index, (label_text, value) in enumerate(stats):
            small_card = ctk.CTkFrame(
                stats_frame,
                fg_color=COLORS["card"],
                corner_radius=INNER_CARD_RADIUS,
                border_width=1,
                border_color=INNER_CARD_BORDER
            )
            small_card.grid(row=0, column=index, sticky="nsew", padx=(0, 10) if index < len(stats) - 1 else 0)

            ctk.CTkLabel(
                small_card,
                text=label_text,
                font=font("small", "bold"),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=16, pady=(16, 4))

            value_label = ctk.CTkLabel(
                small_card,
                text=value,
                font=font("title", "bold"),
                text_color=COLORS["text"]
            )
            value_label.pack(anchor="w", padx=16, pady=(0, 16))
            self._stat_value_labels[label_text] = value_label

        footer = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=(0, 20))

        self.export_button = ctk.CTkButton(
            footer,
            text="⬇ Exportar",
            width=110,
            height=34,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            corner_radius=8,
            state="disabled",
            command=self._show_export_menu
        )
        self.export_button.pack(side="right")

    def _handle_period_change(self, value):
        if value == "Personalizado":
            self._open_custom_period_modal()
            return
        self._custom_period_previous_value = value

    def _open_custom_period_modal(self):
        if self._custom_period_modal is not None:
            try:
                self._custom_period_modal.focus_set()
            except Exception:
                pass
            return

        self._custom_period_previous_value = self.periodo_combo.get() if self.periodo_combo.get() not in ["", "Personalizado"] else self._custom_period_previous_value
        modal = ctk.CTkToplevel(self)
        modal.title("Selecionar período personalizado")
        modal.transient(self)
        modal.grab_set()
        modal.attributes("-topmost", True)
        modal.resizable(False, False)
        modal.configure(fg_color=COLORS["card"])

        self._custom_period_modal = modal
        self._custom_period_type = ctk.StringVar(value="Intervalo")
        self._custom_period_error = ctk.StringVar(value="")

        window_width = 560
        window_height = 420
        x = self.winfo_rootx() + (self.winfo_width() - window_width) // 2
        y = self.winfo_rooty() + (self.winfo_height() - window_height) // 2
        modal.geometry(f"{window_width}x{window_height}+{x}+{y}")

        header = ctk.CTkFrame(modal, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(16, 8))
        ctk.CTkLabel(header, text="Selecionar período personalizado", font=font("subtitle", "bold"), text_color=COLORS["text"]).pack(anchor="w", side="left")

        option_frame = ctk.CTkFrame(modal, fg_color="transparent")
        option_frame.pack(fill="x", padx=18, pady=(0, 12))
        options = ["Ano", "Mês", "Data", "Intervalo"]
        for option in options:
            btn = ctk.CTkButton(
                option_frame,
                text=option,
                width=90,
                height=30,
                fg_color=COLORS["primary"] if self._custom_period_type.get() == option else "transparent",
                hover_color=COLORS["primary_dark"],
                text_color="white" if self._custom_period_type.get() == option else COLORS["text"],
                border_width=1 if self._custom_period_type.get() != option else 0,
                border_color=COLORS["border"],
                corner_radius=8,
                command=lambda selected=option: self._set_custom_period_type(selected),
            )
            btn.pack(side="left", padx=(0, 8))
            if option == self._custom_period_type.get():
                btn.configure(fg_color=COLORS["primary"], text_color="white", border_width=0)

        self._custom_period_content = ctk.CTkFrame(modal, fg_color="transparent")
        self._custom_period_content.pack(fill="both", expand=True, padx=18, pady=(0, 8))
        self._render_custom_period_content()

        self._custom_period_error_label = ctk.CTkLabel(modal, textvariable=self._custom_period_error, font=font("small"), text_color="#d64545")
        self._custom_period_error_label.pack(anchor="w", padx=18, pady=(0, 8))

        footer = ctk.CTkFrame(modal, fg_color="transparent")
        footer.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkButton(footer, text="Cancelar", width=100, fg_color="transparent", text_color=COLORS["text"], border_width=1, border_color=COLORS["border"], hover_color=COLORS["border"], command=self._cancel_custom_period_modal).pack(side="right", padx=(8, 0))
        ctk.CTkButton(footer, text="Aplicar", width=100, fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"], text_color="white", command=self._apply_custom_period).pack(side="right")

        modal.protocol("WM_DELETE_WINDOW", self._cancel_custom_period_modal)

    def _close_custom_period_modal(self):
        if self._custom_period_modal is not None:
            try:
                self._custom_period_modal.destroy()
            except Exception:
                pass
            self._custom_period_modal = None

    def _cancel_custom_period_modal(self):
        self._close_custom_period_modal()
        self.periodo_combo.set(self._custom_period_previous_value)

    def _set_custom_period_type(self, selected_type):
        if self._custom_period_modal is None:
            return
        self._custom_period_type.set(selected_type)
        self._render_custom_period_content()

    def _render_custom_period_content(self):
        if self._custom_period_modal is None:
            return
        for child in self._custom_period_content.winfo_children():
            child.destroy()
        option = self._custom_period_type.get()

        if option == "Ano":
            year_frame = ctk.CTkFrame(self._custom_period_content, fg_color="transparent")
            year_frame.pack(fill="x", pady=12)
            ctk.CTkLabel(year_frame, text="Ano", font=font("small", "bold"), text_color=COLORS["text"]).pack(anchor="w")
            years = [str(year) for year in range(datetime.now().year - 5, datetime.now().year + 6)]
            self._custom_year_var = ctk.StringVar(value=str(datetime.now().year))
            ctk.CTkComboBox(year_frame, values=years, variable=self._custom_year_var, width=220, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"]).pack(anchor="w", pady=(6, 0))
        elif option == "Mês":
            year_frame = ctk.CTkFrame(self._custom_period_content, fg_color="transparent")
            year_frame.pack(fill="x", pady=(8, 8))
            ctk.CTkLabel(year_frame, text="Ano", font=font("small", "bold"), text_color=COLORS["text"]).pack(anchor="w")
            years = [str(year) for year in range(datetime.now().year - 5, datetime.now().year + 6)]
            self._custom_month_year_var = ctk.StringVar(value=str(datetime.now().year))
            ctk.CTkComboBox(year_frame, values=years, variable=self._custom_month_year_var, width=220, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"]).pack(anchor="w", pady=(6, 0))

            month_frame = ctk.CTkFrame(self._custom_period_content, fg_color="transparent")
            month_frame.pack(fill="x", pady=(8, 8))
            ctk.CTkLabel(month_frame, text="Mês", font=font("small", "bold"), text_color=COLORS["text"]).pack(anchor="w")
            months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            self._custom_month_var = ctk.StringVar(value=months[datetime.now().month - 1])
            month_combo = ctk.CTkComboBox(month_frame, values=months, variable=self._custom_month_var, width=220, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            month_combo.pack(anchor="w", pady=(6, 0))
        elif option == "Data":
            date_frame = ctk.CTkFrame(self._custom_period_content, fg_color="transparent")
            date_frame.pack(fill="x", pady=12)
            ctk.CTkLabel(date_frame, text="Data", font=font("small", "bold"), text_color=COLORS["text"]).pack(anchor="w")
            self._custom_day_var = ctk.StringVar(value=str(datetime.now().day))
            self._custom_month_date_var = ctk.StringVar(value=str(datetime.now().month))
            self._custom_year_date_var = ctk.StringVar(value=str(datetime.now().year))
            day_box = ctk.CTkComboBox(date_frame, values=[str(i) for i in range(1, 32)], variable=self._custom_day_var, width=80, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            month_box = ctk.CTkComboBox(date_frame, values=[str(i) for i in range(1, 13)], variable=self._custom_month_date_var, width=90, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            year_box = ctk.CTkComboBox(date_frame, values=[str(year) for year in range(datetime.now().year - 10, datetime.now().year + 11)], variable=self._custom_year_date_var, width=100, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            for widget in (day_box, month_box, year_box):
                widget.pack(side="left", padx=(0, 8), pady=(6, 0))
        else:
            date_frame = ctk.CTkFrame(self._custom_period_content, fg_color="transparent")
            date_frame.pack(fill="x", pady=8)
            ctk.CTkLabel(date_frame, text="Data inicial", font=font("small", "bold"), text_color=COLORS["text"]).pack(anchor="w")
            self._custom_start_day_var = ctk.StringVar(value=str(datetime.now().day))
            self._custom_start_month_var = ctk.StringVar(value=str(datetime.now().month))
            self._custom_start_year_var = ctk.StringVar(value=str(datetime.now().year))
            start_day = ctk.CTkComboBox(date_frame, values=[str(i) for i in range(1, 32)], variable=self._custom_start_day_var, width=80, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            start_month = ctk.CTkComboBox(date_frame, values=[str(i) for i in range(1, 13)], variable=self._custom_start_month_var, width=90, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            start_year = ctk.CTkComboBox(date_frame, values=[str(year) for year in range(datetime.now().year - 10, datetime.now().year + 11)], variable=self._custom_start_year_var, width=100, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            for widget in (start_day, start_month, start_year):
                widget.pack(side="left", padx=(0, 8), pady=(6, 0))

            end_frame = ctk.CTkFrame(self._custom_period_content, fg_color="transparent")
            end_frame.pack(fill="x", pady=(18, 0))
            ctk.CTkLabel(end_frame, text="Data final", font=font("small", "bold"), text_color=COLORS["text"]).pack(anchor="w")
            self._custom_end_day_var = ctk.StringVar(value=str(datetime.now().day))
            self._custom_end_month_var = ctk.StringVar(value=str(datetime.now().month))
            self._custom_end_year_var = ctk.StringVar(value=str(datetime.now().year))
            end_day = ctk.CTkComboBox(end_frame, values=[str(i) for i in range(1, 32)], variable=self._custom_end_day_var, width=80, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            end_month = ctk.CTkComboBox(end_frame, values=[str(i) for i in range(1, 13)], variable=self._custom_end_month_var, width=90, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            end_year = ctk.CTkComboBox(end_frame, values=[str(year) for year in range(datetime.now().year - 10, datetime.now().year + 11)], variable=self._custom_end_year_var, width=100, height=34, fg_color=COLORS["input_bg"], border_color=COLORS["border"], button_color=COLORS["primary"], dropdown_fg_color=COLORS["card"])
            for widget in (end_day, end_month, end_year):
                widget.pack(side="left", padx=(0, 8), pady=(6, 0))

    def _parse_custom_date(self, year, month, day):
        return datetime(int(year), int(month), int(day), 0, 0, 0, 0)

    def _parse_custom_interval(self, start_year, start_month, start_day, end_year, end_month, end_day):
        start_dt = self._parse_custom_date(start_year, start_month, start_day)
        end_dt = self._parse_custom_date(end_year, end_month, end_day)
        if start_dt > end_dt:
            return None, "A data inicial não pode ser maior que a data final."
        return start_dt, end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    def _apply_custom_period(self):
        if self._custom_period_modal is None:
            return

        option = self._custom_period_type.get()
        try:
            if option == "Ano":
                year = int(self._custom_year_var.get())
                inicio = datetime(year, 1, 1, 0, 0, 0, 0)
                fim = datetime(year, 12, 31, 23, 59, 59, 999999)
            elif option == "Mês":
                year = int(self._custom_month_year_var.get())
                month_name = self._custom_month_var.get()
                month_index = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"].index(month_name) + 1
                last_day = calendar.monthrange(year, month_index)[1]
                inicio = datetime(year, month_index, 1, 0, 0, 0, 0)
                fim = datetime(year, month_index, last_day, 23, 59, 59, 999999)
            elif option == "Data":
                year = int(self._custom_year_date_var.get())
                month = int(self._custom_month_date_var.get())
                day = int(self._custom_day_var.get())
                inicio = datetime(year, month, day, 0, 0, 0, 0)
                fim = datetime(year, month, day, 23, 59, 59, 999999)
            else:
                start_year = int(self._custom_start_year_var.get())
                start_month = int(self._custom_start_month_var.get())
                start_day = int(self._custom_start_day_var.get())
                end_year = int(self._custom_end_year_var.get())
                end_month = int(self._custom_end_month_var.get())
                end_day = int(self._custom_end_day_var.get())
                inicio, message = self._parse_custom_interval(start_year, start_month, start_day, end_year, end_month, end_day)
                if inicio is None:
                    self._custom_period_error.set(message)
                    return
                fim = datetime(end_year, end_month, end_day, 23, 59, 59, 999999)
            self.custom_date_start = inicio
            self.custom_date_end = fim
            self._close_custom_period_modal()
            self.periodo_combo.set("Personalizado")
            self._load_data_async()
        except Exception:
            self._custom_period_error.set("Selecione uma data válida para o período personalizado.")

    def _show_export_menu(self):
        if self.export_button is None:
            return
        if self._current_report_data is None:
            return
        self._export_menu.post(self.export_button.winfo_rootx(), self.export_button.winfo_rooty() + self.export_button.winfo_height())

    def _build_export_payload(self, summary, chart_period, specialty_data, productivity_rows):
        snapshot = self._capture_filter_snapshot()
        payload = {
            "filters": {
                "Período": snapshot.get("periodo", ""),
                "Médico": snapshot.get("medico_name", ""),
                "Especialidade": snapshot.get("especialidade_name", ""),
                "Status": snapshot.get("status", ""),
            },
            "summary": {
                "Consultas": summary.get("total_consultas", 0),
                "Pacientes": summary.get("total_pacientes", 0),
                "Médicos": summary.get("total_medicos", 0),
                "Cancelamentos": summary.get("cancelamentos", 0),
                "Comparecimento": f"{summary.get('comparecimento', 0)}%",
                "Novos Pacientes": summary.get("novos_pacientes", 0),
                "Retornos": summary.get("retornos", 0),
            },
            "chart_period": chart_period or {"labels": [], "values": []},
            "specialty_data": specialty_data or [],
            "productivity_rows": productivity_rows or [],
        }
        return payload

    def _export_report(self, export_format):
        if self._current_report_data is None:
            return

        default_name = f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if export_format == "pdf":
            file_types = [("Arquivo PDF", "*.pdf")]
            extension = "pdf"
        elif export_format == "xlsx":
            file_types = [("Planilha Excel", "*.xlsx")]
            extension = "xlsx"
        else:
            file_types = [("CSV", "*.csv")]
            extension = "csv"

        path = filedialog.asksaveasfilename(
            defaultextension=f".{extension}",
            initialfile=f"{default_name}.{extension}",
            filetypes=file_types,
        )
        if not path:
            return

        try:
            if export_format == "pdf":
                self._write_pdf_export(path, self._current_report_data)
            elif export_format == "xlsx":
                self._write_excel_export(path, self._current_report_data)
            else:
                self._write_csv_export(path, self._current_report_data)
        except Exception as exc:
            print(f"[RELATÓRIOS] erro ao exportar: {exc}")

    def _write_csv_export(self, path, payload):
        rows = []
        rows.append(["Tipo", "Campo", "Valor"])
        for label, value in payload["filters"].items():
            rows.append(["Filtros", label, value])
        for label, value in payload["summary"].items():
            rows.append(["Resumo", label, value])
        for index, label in enumerate(payload["chart_period"].get("labels", [])):
            rows.append(["Período", label, payload["chart_period"].get("values", [])[index] if index < len(payload["chart_period"].get("values", [])) else 0])
        for item in payload["specialty_data"]:
            rows.append(["Especialidade", item[0] or "Sem Especialidade", item[1] or 0])
        for index, row in enumerate(payload["productivity_rows"]):
            rows.append(["Produtividade", f"{index + 1} - {row[0] or '-'}", f"{row[1] or '-'} | {row[2] or 0}"])

        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)

    def _write_excel_export(self, path, payload):
        rows = []
        rows.append(["Tipo", "Campo", "Valor"])
        for label, value in payload["filters"].items():
            rows.append(["Filtros", label, value])
        for label, value in payload["summary"].items():
            rows.append(["Resumo", label, value])
        for index, label in enumerate(payload["chart_period"].get("labels", [])):
            rows.append(["Período", label, payload["chart_period"].get("values", [])[index] if index < len(payload["chart_period"].get("values", [])) else 0])
        for item in payload["specialty_data"]:
            rows.append(["Especialidade", item[0] or "Sem Especialidade", item[1] or 0])
        for index, row in enumerate(payload["productivity_rows"]):
            rows.append(["Produtividade", f"{index + 1} - {row[0] or '-'}", f"{row[1] or '-'} | {row[2] or 0}"])

        try:
            from openpyxl import Workbook
        except Exception:
            Workbook = None

        if Workbook is not None:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Relatório"
            for row in rows:
                sheet.append(row)
            workbook.save(path)
            return

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            sheet_xml = []
            for row in rows:
                cells = []
                for value in row:
                    text = str(value)
                    cells.append(f"<c t=\"inlineStr\"><is><t>{xml_escape(text)}</t></is></c>")
                sheet_xml.append(f"<row>{''.join(cells)}</row>")
            worksheet = f"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?><worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetData>{''.join(sheet_xml)}</sheetData></worksheet>"
            content_types = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>'
            rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/><Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/></Relationships>'
            workbook_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Relatório" sheetId="1" r:id="rId1"/></sheets></workbook>'
            app_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>OdontoPro</Application></Properties>'
            core_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Relatório</dc:title><dc:creator>OdontoPro</dc:creator><cp:lastModifiedBy>OdontoPro</cp:lastModifiedBy></cp:coreProperties>'
            archive.writestr("[Content_Types].xml", content_types)
            archive.writestr("_rels/.rels", rels)
            archive.writestr("docProps/app.xml", app_xml)
            archive.writestr("docProps/core.xml", core_xml)
            archive.writestr("xl/workbook.xml", workbook_xml)
            archive.writestr("xl/_rels/workbook.xml.rels", '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
            archive.writestr("xl/worksheets/sheet1.xml", worksheet)

    def _write_pdf_export(self, path, payload):
        lines = [
            "Relatório OdontoPro",
            "",
            "Filtros",
        ]
        for label, value in payload["filters"].items():
            lines.append(f"- {label}: {value}")
        lines.extend(["", "Resumo"])
        for label, value in payload["summary"].items():
            lines.append(f"- {label}: {value}")
        lines.extend(["", "Consultas por Período"])
        for index, label in enumerate(payload["chart_period"].get("labels", [])):
            value = payload["chart_period"].get("values", [])[index] if index < len(payload["chart_period"].get("values", [])) else 0
            lines.append(f"- {label}: {value}")
        lines.extend(["", "Consultas por Especialidade"])
        for item in payload["specialty_data"]:
            lines.append(f"- {item[0] or 'Sem Especialidade'}: {item[1] or 0}")
        lines.extend(["", "Médicos Mais Produtivos"])
        for index, row in enumerate(payload["productivity_rows"]):
            lines.append(f"- {index + 1}. {row[0] or '-'} | {row[1] or '-'} | {row[2] or 0}")

        escaped_lines = []
        for line in lines:
            escaped_lines.append(line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))

        content = "\n".join(escaped_lines)
        stream = f"BT /F1 12 Tf 50 760 Td ({content}) Tj ET"
        objects = [
            "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
            "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
            "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj",
            f"4 0 obj << /Length {len(stream.encode('utf-8'))} >> stream\n{stream}\nendstream endobj",
            "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        ]
        pdf_parts = ["%PDF-1.4", ""]
        offsets = []
        current_offset = 0
        for obj in objects:
            offsets.append(current_offset)
            pdf_parts.append(obj)
            current_offset = len("\n".join(pdf_parts).encode("utf-8"))
        xref_offset = len("\n".join(pdf_parts[:-1]).encode("utf-8"))
        pdf = "\n".join(pdf_parts)
        pdf += f"\nxref\n0 6\n0000000000 65535 f \n"
        for offset in offsets:
            pdf += f"{offset:010d} 00000 n \n"
        pdf += "trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n0\n%%EOF"
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(pdf)

    def _load_data_async(self):
        if self._loading:
            return

        self._loading = True
        self.update_button.configure(state="disabled")
        self._loading_label.configure(text="Carregando relatório...")
        self._loading_label.pack(anchor="w", padx=20, pady=(0, 10))
        self._start_loading_animation()

        snapshot = self._capture_filter_snapshot()
        if snapshot["periodo"] == "Semanal":
            snapshot["periodo"] = "Semana"
        if snapshot["periodo"] == "Mensal":
            snapshot["periodo"] = "Mês"
        elif snapshot["periodo"] == "Anual":
            snapshot["periodo"] = "Ano"
        medico_id = self._medicos_map.get(snapshot["medico_name"])
        especialidade_id = self._especialidades_map.get(snapshot["especialidade_name"])

        self._current_thread_id += 1
        thread_id = self._current_thread_id

        def thread_wrapper():
            try:
                self._load_data_thread(
                    thread_id,
                    snapshot["periodo"],
                    snapshot["status"],
                    snapshot["medico_name"],
                    snapshot["especialidade_name"],
                    medico_id,
                    especialidade_id,
                )
            except Exception as e:
                print(f"[RELATÓRIOS] _load_data_thread error: {e}")
                import traceback
                traceback.print_exc()
                self._load_queue.put((thread_id, None, None, None, None, None, None, f"Erro interno: {e}"))

        thread = threading.Thread(target=thread_wrapper, daemon=False)
        self._initialization_thread = thread
        thread.start()

        if self._timeout_id is not None:
            try:
                self.after_cancel(self._timeout_id)
            except Exception:
                pass

        self._timeout_id = self.winfo_toplevel().after(40000, lambda: self._timeout_loading(thread_id))
        self.winfo_toplevel().after(100, self._process_load_queue)

    def _timeout_loading(self, thread_id):
        if self._current_thread_id != thread_id:
            return

        self._loading = False
        self._timeout_id = None
        self.update_button.configure(state="normal")
        self._stop_loading_animation()
        self._loading_label.configure(text="Tempo de carregamento esgotado. Tente novamente.")

    def _start_loading_animation(self):
        if self._loading_animation_id is not None:
            return

        self._loading_dot_count = 0

        def update_text():
            if not self._loading:
                self._stop_loading_animation()
                return

            self._loading_dot_count = (self._loading_dot_count + 1) % 4
            dots = "." * self._loading_dot_count
            self._loading_label.configure(text=f"Carregando relatório{dots}")
            self._loading_animation_id = self.after(300, update_text)

        update_text()

    def _stop_loading_animation(self):
        if self._loading_animation_id is not None:
            try:
                self.after_cancel(self._loading_animation_id)
            except Exception:
                pass
            self._loading_animation_id = None

    def _capture_filter_snapshot(self):
        return {
            "periodo": self.periodo_combo.get(),
            "status": self.status_combo.get(),
            "medico_name": self.medico_combo.get(),
            "especialidade_name": self.especialidade_combo.get(),
        }

    def _build_filter_conditions(self, medico_id, especialidade_id, medico_name, especialidade_name, status):
        conditions = ["c.clinica_id = %s"]
        params = [self.clinica_id]

        if status and status not in ['Todos', 'Status', '']:
            conditions.append("LOWER(TRIM(c.status)) = %s")
            params.append(status.lower())

        if medico_id not in [None, '', 'Todos', 'Médico']:
            conditions.append("c.medico_id = %s")
            params.append(medico_id)
        elif medico_name and medico_name not in ['Todos', 'Médico', '']:
            conditions.append("m.nome = %s")
            params.append(medico_name)

        if especialidade_id not in [None, '', 'Todos', 'Especialidade']:
            conditions.append("c.especialidade_id = %s")
            params.append(especialidade_id)
        elif especialidade_name and especialidade_name not in ['Todos', 'Especialidade', '']:
            conditions.append("LOWER(TRIM(e.nome)) = %s")
            params.append(especialidade_name.lower())

        return " AND ".join(conditions), params

    def _get_date_range(self, periodo):
        agora = datetime.now()

        def end_of_day(dt):
            return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        if periodo == "Hoje":
            inicio = agora.replace(hour=0, minute=0, second=0, microsecond=0)
            fim = end_of_day(agora)
            tipo = "hoje"
        elif periodo == "Semana":
            # 7 dias completos, incluindo hoje: 6 dias anteriores + dia atual
            inicio = (agora - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            fim = end_of_day(agora)
            tipo = "semana"
        elif periodo == "Mês":
            # Ano completo atual para agrupar por mês
            inicio = agora.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = end_of_day(agora.replace(month=12, day=31))
            tipo = "mes"
        elif periodo == "Ano":
            # Últimos 5 anos completos, incluindo o ano atual
            inicio = agora.replace(year=agora.year - 4, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            fim = end_of_day(agora.replace(month=12, day=31))
            tipo = "ano"
        else:
            if self.custom_date_start is not None and self.custom_date_end is not None:
                inicio = self.custom_date_start
                fim = self.custom_date_end
            else:
                inicio = (agora - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
                fim = end_of_day(agora)
            tipo = "personalizado"

        return inicio, fim, tipo

    def _load_data_thread(self, thread_id, periodo, status, medico_name, especialidade_name, medico_id, especialidade_id):
        inicio, fim, periodo_tipo = self._get_date_range(periodo)
        filtro_base, filtro_params = self._build_filter_conditions(
            medico_id,
            especialidade_id,
            medico_name,
            especialidade_name,
            status
        )

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Cache filter options once for the clinic session
            if "filter_options" not in self._cache:
                medicos = ConsultaController.listar_medicos(self.clinica_id)
                especialidades = ConsultaController.listar_especialidades_para_combo(self.clinica_id)
                self._cache["filter_options"] = {
                    "medicos": medicos,
                    "especialidades": especialidades,
                }
            else:
                medicos = self._cache["filter_options"]["medicos"]
                especialidades = self._cache["filter_options"]["especialidades"]

            # KPIs de Relatórios vêm do controller compartilhado.
            summary = RelatoriosController.obter_resumo_consultas(
                self.clinica_id,
                data_inicio=inicio,
                data_fim=fim,
                status=status,
                medico_id=medico_id,
                especialidade_id=especialidade_id,
                medico_name=medico_name,
                especialidade_name=especialidade_name,
            )

            total_consultas = summary.get("total_consultas", 0)
            total_pacientes = summary.get("total_pacientes", 0)
            total_medicos = summary.get("total_medicos", 0)
            cancelamentos = summary.get("cancelamentos", 0)
            comparecimento = summary.get("comparecimento", 0)

            # Novos pacientes: primeira consulta no período
            cursor.execute("""
                SELECT COUNT(*)
                FROM (
                    SELECT paciente_id, MIN(data_hora) AS primeira_consulta
                    FROM odontoPro_consulta
                    WHERE clinica_id = %s
                    GROUP BY paciente_id
                ) primeiro
                WHERE primeira_consulta BETWEEN %s AND %s
            """, (self.clinica_id, inicio, fim))
            row_new = cursor.fetchone()
            novos_pacientes = int(row_new[0] or 0) if row_new else 0

            cursor.execute(f"""
                SELECT
                    COUNT(DISTINCT CASE WHEN LOWER(TRIM(c.status)) = 'realizada' THEN c.paciente_id END) AS pacientes_unicos_atendidos,
                    SUM(CASE WHEN LOWER(TRIM(c.status)) = 'falta' THEN 1 ELSE 0 END) AS faltas,
                    SUM(CASE WHEN LOWER(TRIM(c.status)) IN ('agendada', 'confirmada', 'reagendada') THEN 1 ELSE 0 END) AS consultas_agendadas
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {filtro_base}
                  AND c.data_hora BETWEEN %s AND %s
            """, tuple(filtro_params + [inicio, fim]))
            row_status_cards = cursor.fetchone()
            pacientes_unicos_atendidos = int(row_status_cards[0] or 0) if row_status_cards else 0
            faltas = int(row_status_cards[1] or 0) if row_status_cards else 0
            consultas_agendadas = int(row_status_cards[2] or 0) if row_status_cards else 0

            # Retornos: paciente com consulta no período e primeira consulta antes do início
            retorno_params = [self.clinica_id, self.clinica_id, inicio, fim, inicio]
            # Reuse the same filters for the period query
            retorno_where = "c.clinica_id = %s AND c.data_hora BETWEEN %s AND %s AND firsts.primeira_consulta < %s"
            if status and status not in ['Todos', 'Status', '']:
                retorno_where += " AND LOWER(TRIM(c.status)) = %s"
                retorno_params.append(status.lower())
            if medico_id not in [None, '', 'Todos', 'Médico']:
                retorno_where += " AND c.medico_id = %s"
                retorno_params.append(medico_id)
            elif medico_name and medico_name not in ['Todos', 'Médico', '']:
                retorno_where += " AND m.nome = %s"
                retorno_params.append(medico_name)
            if especialidade_id not in [None, '', 'Todos', 'Especialidade']:
                retorno_where += " AND c.especialidade_id = %s"
                retorno_params.append(especialidade_id)
            elif especialidade_name and especialidade_name not in ['Todos', 'Especialidade', '']:
                retorno_where += " AND LOWER(TRIM(e.nome)) = %s"
                retorno_params.append(especialidade_name.lower())

            cursor.execute(f"""
                SELECT COUNT(DISTINCT c.paciente_id)
                FROM odontoPro_consulta c
                JOIN (
                    SELECT paciente_id, MIN(data_hora) AS primeira_consulta
                    FROM odontoPro_consulta
                    WHERE clinica_id = %s
                    GROUP BY paciente_id
                ) firsts ON firsts.paciente_id = c.paciente_id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {retorno_where}
            """, tuple(retorno_params))
            row_retorno = cursor.fetchone()
            retornos = int(row_retorno[0] or 0) if row_retorno else 0

            # Consultas por período para gráfico
            chart_period = self._fetch_period_chart(cursor, filtro_base, filtro_params, inicio, fim, periodo_tipo)

            # Consultas por especialidade para gráfico de pizza
            cursor.execute(f"""
                SELECT COALESCE(e.nome, 'Sem Especialidade') AS especialidade,
                      COUNT(*) AS total,
                      SUM(CASE WHEN LOWER(TRIM(c.status)) IN ('agendada', 'confirmada', 'reagendada') THEN 1 ELSE 0 END) AS agendadas,
                      SUM(CASE WHEN LOWER(TRIM(c.status)) = 'realizada' THEN 1 ELSE 0 END) AS realizadas,
                      SUM(CASE WHEN LOWER(TRIM(c.status)) = 'cancelada' THEN 1 ELSE 0 END) AS canceladas,
                      SUM(CASE WHEN LOWER(TRIM(c.status)) = 'falta' THEN 1 ELSE 0 END) AS faltas
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {filtro_base}
                  AND c.data_hora BETWEEN %s AND %s
                GROUP BY especialidade
                ORDER BY total DESC
                LIMIT 8
            """, tuple(filtro_params + [inicio, fim]))
            specialty_data = cursor.fetchall() or []

            # Médicos mais produtivos
            cursor.execute(f"""
                SELECT m.nome AS medico,
                       COALESCE(e.nome, 'Sem Especialidade') AS especialidade,
                       COUNT(*) AS consultas
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
                WHERE {filtro_base}
                  AND c.data_hora BETWEEN %s AND %s
                GROUP BY c.medico_id, m.nome, e.nome
                ORDER BY consultas DESC
                LIMIT 5
            """, tuple(filtro_params + [inicio, fim]))
            productivity_rows = cursor.fetchall() or []

            self._load_queue.put((
                thread_id,
                {
                    "total_consultas": int(total_consultas or 0),
                    "total_pacientes": int(total_pacientes or 0),
                    "total_medicos": int(total_medicos or 0),
                    "cancelamentos": int(cancelamentos or 0),
                    "comparecimento": int(comparecimento),
                    "novos_pacientes": int(novos_pacientes or 0),
                    "retornos": int(retornos or 0),
                    "pacientes_unicos_atendidos": pacientes_unicos_atendidos,
                    "faltas": faltas,
                    "consultas_agendadas": consultas_agendadas,
                },
                chart_period,
                specialty_data,
                productivity_rows,
                medicos,
                especialidades,
                None
            ))

        except Exception as e:
            print(f"[RELATÓRIOS] erro ao carregar dados: {e}")
            import traceback
            traceback.print_exc()
            self._load_queue.put((thread_id, None, None, None, None, None, None, str(e)))

        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                pass

    def _fetch_period_chart(self, cursor, filtro_base, filtro_params, inicio, fim, periodo_tipo):
        if periodo_tipo == "hoje":
            label_keys = list(range(24))
            labels = [f"{h}h" for h in label_keys]
            group_expr = "HOUR(c.data_hora)"
        elif periodo_tipo == "semana" or periodo_tipo == "personalizado":
            delta = (fim.date() - inicio.date()).days
            label_keys = [inicio.date() + timedelta(days=i) for i in range(delta + 1)]
            labels = [d.strftime("%d/%m") for d in label_keys]
            group_expr = "DATE(c.data_hora)"
        elif periodo_tipo == "mes":
            label_keys = list(range(1, 13))
            labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            group_expr = "MONTH(c.data_hora)"
        elif periodo_tipo == "ano":
            start_year = inicio.year
            end_year = fim.year
            label_keys = list(range(start_year, end_year + 1))
            labels = [str(year) for year in label_keys]
            group_expr = "YEAR(c.data_hora)"
        else:
            label_keys = list(range(1, 13))
            labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
            group_expr = "MONTH(c.data_hora)"

        params = filtro_params + [inicio, fim]
        cursor.execute(f"""
            SELECT {group_expr} AS periodo,
                   LOWER(TRIM(c.status)) AS status,
                   COUNT(*) AS total
            FROM odontoPro_consulta c
            LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
            LEFT JOIN odontoPro_especialidade e ON c.especialidade_id = e.id
            WHERE {filtro_base}
              AND c.data_hora BETWEEN %s AND %s
            GROUP BY periodo, LOWER(TRIM(c.status))
            ORDER BY periodo
        """, tuple(params))

        rows = cursor.fetchall() or []
        details = {}
        for row in rows:
            periodo_value, status_value, total = row
            total = int(total or 0)
            if periodo_value not in details:
                details[periodo_value] = {
                    "total": 0,
                    "agendadas": 0,
                    "realizadas": 0,
                    "canceladas": 0,
                    "faltas": 0,
                }
            details[periodo_value]["total"] += total
            if status_value in {"agendada", "confirmada", "reagendada"}:
                details[periodo_value]["agendadas"] += total
            elif status_value == "realizada":
                details[periodo_value]["realizadas"] = total
            elif status_value == "cancelada":
                details[periodo_value]["canceladas"] = total
            elif status_value == "falta":
                details[periodo_value]["faltas"] = total

        values = [details.get(key, {}).get("total", 0) for key in label_keys]
        detail_rows = [
            {
                "label": label,
                "total": details.get(key, {}).get("total", 0),
                "agendadas": details.get(key, {}).get("agendadas", 0),
                "realizadas": details.get(key, {}).get("realizadas", 0),
                "canceladas": details.get(key, {}).get("canceladas", 0),
                "faltas": details.get(key, {}).get("faltas", 0),
            }
            for key, label in zip(label_keys, labels)
        ]
        return {"labels": labels, "values": values, "details": detail_rows}

    def _clear_chart_container(self, container):
        for child in container.winfo_children():
            child.destroy()

    def _render_bar_chart(self, chart_period):
        self._clear_chart_container(self._chart_canvas_container)
        self._chart_canvas = None

        labels = chart_period.get("labels", [])
        values = chart_period.get("values", [])
        if not labels or sum(values) == 0:
            empty_frame = ctk.CTkFrame(self._chart_canvas_container, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True)
            ctk.CTkLabel(
                empty_frame,
                text="📅",
                font=font("title", "bold"),
                text_color=COLORS["text"],
            ).pack(pady=(40, 8))
            ctk.CTkLabel(
                empty_frame,
                text="Nenhuma consulta encontrada para o período selecionado.",
                font=font("small", "bold"),
                text_color=COLORS["text_secondary"],
            ).pack(pady=(0, 4))
            ctk.CTkLabel(
                empty_frame,
                text="Altere os filtros para visualizar os dados.",
                font=font("small"),
                text_color=COLORS["text_secondary"],
            ).pack()
            return

        is_dark = get_dark_mode()
        if is_dark:
            fig_bg = COLORS["card"]
            ax_bg = COLORS["card"]
            bar_color = COLORS.get("primary", "#06B6D4")
            text_color = COLORS.get("text", "#F8FAFC")
            label_color = COLORS.get("text_secondary", "#CBD5E1")
            border_color = COLORS.get("border", "#30363D")
            grid_color = COLORS.get("border", "#30363D")
            tick_color = COLORS.get("text_secondary", "#CBD5E1")
            annotation_color = COLORS.get("text", "#F8FAFC")
            tooltip_bg = COLORS.get("bg_soft", "#161B22")
            tooltip_text = COLORS.get("text", "#F8FAFC")
            tooltip_edge = COLORS.get("border", "#30363D")
            x_rotation = 0
            x_ha = "center"
            grid_alpha = 0.28
            bar_alpha = 0.95
            text_size = 9
            xlabel = "Período"
            ylabel = "Consultas"
        else:
            fig_bg = "#FFFFFF"
            ax_bg = "#FFFFFF"
            bar_color = COLORS.get("primary", "#06B6D4")
            text_color = COLORS.get("text", "#1F2937")
            label_color = COLORS.get("text", "#1F2937")
            border_color = COLORS.get("border", "#E5E7EB")
            grid_color = COLORS.get("border", "#E5E7EB")
            tick_color = COLORS.get("text", "#1F2937")
            annotation_color = COLORS.get("text", "#1F2937")
            tooltip_bg = "#FFFFFF"
            tooltip_text = COLORS.get("text", "#1F2937")
            tooltip_edge = COLORS.get("border", "#E5E7EB")
            x_rotation = 35
            x_ha = "right"
            grid_alpha = 0.12
            bar_alpha = 0.95
            text_size = 9
            xlabel = ""
            ylabel = "Consultas"

        fig = Figure(figsize=(9, 3.2), dpi=100, facecolor=fig_bg)
        ax = fig.add_subplot(111)
        ax.set_facecolor(ax_bg)

        positions = list(range(len(labels)))
        bar_width = 0.45
        positive_values = [value for value in values if value > 0]
        y_max = max(positive_values) if positive_values else 1
        y_limit = max(2, y_max + 1)

        bar_container = ax.bar(
            positions,
            values,
            width=bar_width,
            align="center",
            color=bar_color,
            edgecolor=bar_color,
            linewidth=1.0,
            alpha=bar_alpha,
            zorder=3,
        )

        periodo_atual = self.periodo_combo.get() if hasattr(self, "periodo_combo") and self.periodo_combo is not None else (self.periodo_var.get() if hasattr(self, "periodo_var") else "")
        if periodo_atual == "Semanal":
            periodo_atual = "Semana"
        if periodo_atual == "Mensal":
            periodo_atual = "Mês"
        elif periodo_atual == "Anual":
            periodo_atual = "Ano"

        tick_positions = list(positions)
        tick_labels = list(labels)

        if periodo_atual == "Hoje":
            tick_positions = list(range(0, len(labels), 2))
            tick_labels = [labels[i] for i in tick_positions]
            if len(labels) > 1 and tick_positions[-1] != len(labels) - 1:
                tick_positions.append(len(labels) - 1)
                tick_labels.append(labels[-1])
        elif periodo_atual == "Semana":
            tick_positions = list(positions)
            tick_labels = list(labels)
        elif periodo_atual == "Mês":
            tick_positions = list(range(12))
            tick_labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        elif periodo_atual == "Ano":
            tick_positions = list(positions)
            tick_labels = list(labels)
            tick_positions = list(range(len(labels)))
            tick_labels = list(labels)
        else:
            max_visible_ticks = 10
            if len(labels) <= max_visible_ticks:
                step = 1
            else:
                step = max(1, math.ceil(len(labels) / max_visible_ticks))
            tick_positions = list(range(0, len(labels), step))
            tick_labels = [labels[i] for i in tick_positions]
            if len(labels) > 0 and tick_positions[-1] != len(labels) - 1:
                tick_positions.append(len(labels) - 1)
                tick_labels.append(labels[-1])

        ax.set_xlim(-0.5, len(labels) - 0.5)
        ax.set_ylim(0, y_limit)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels, fontsize=10, color=tick_color, rotation=x_rotation, ha=x_ha)
        ax.tick_params(axis="y", colors=tick_color, labelsize=10)
        ax.tick_params(axis="x", colors=tick_color, labelsize=10, length=0)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color(border_color)
        ax.spines["bottom"].set_color(border_color)
        ax.spines["left"].set_linewidth(1.0)
        ax.spines["bottom"].set_linewidth(1.0)
        ax.yaxis.grid(True, color=grid_color, alpha=grid_alpha, linestyle="--", zorder=0)
        ax.xaxis.grid(False)
        ax.set_ylabel(ylabel, color=label_color, fontsize=10, labelpad=12)
        if xlabel:
            ax.set_xlabel(xlabel, color=label_color, fontsize=10, labelpad=10)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.title.set_color(text_color)

        for patch, value in zip(bar_container.patches, values):
            if value <= 0:
                continue
            ax.annotate(
                f"{int(value)}",
                xy=(patch.get_x() + patch.get_width() / 2, value),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=text_size,
                color=annotation_color,
            )

        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self._chart_canvas_container)
        canvas.draw()
        canvas.get_tk_widget().configure(bg=fig_bg)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        self._chart_canvas = canvas

        if self._chart_hover_connection_id is not None:
            try:
                self._chart_canvas.mpl_disconnect(self._chart_hover_connection_id)
            except Exception:
                pass

        self._chart_bar_tooltip = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox={"boxstyle": "round,pad=0.4", "fc": tooltip_bg, "ec": tooltip_edge, "alpha": 0.96},
            fontsize=9,
            color=tooltip_text,
            visible=False,
        )

        def _on_chart_hover(event):
            if event.inaxes != ax:
                if self._chart_bar_tooltip is not None:
                    self._chart_bar_tooltip.set_visible(False)
                    self._chart_canvas.draw_idle()
                return

            for patch, details in zip(bar_container.patches, chart_period["details"]):
                contains, _ = patch.contains(event)
                if contains:
                    tooltip_text = (
                        f"{details['label']}\n"
                        f"Total: {details['total']}\n"
                        f"Agendadas: {details['agendadas']}\n"
                        f"Realizadas: {details['realizadas']}\n"
                        f"Canceladas: {details['canceladas']}\n"
                        f"Faltas: {details['faltas']}"
                    )
                    self._chart_bar_tooltip.set_text(tooltip_text)
                    self._chart_bar_tooltip.xy = (event.xdata, event.ydata)
                    self._chart_bar_tooltip.set_visible(True)
                    self._chart_canvas.draw_idle()
                    break
            else:
                if self._chart_bar_tooltip is not None and self._chart_bar_tooltip.get_visible():
                    self._chart_bar_tooltip.set_visible(False)
                    self._chart_canvas.draw_idle()

        self._chart_hover_connection_id = self._chart_canvas.mpl_connect("motion_notify_event", _on_chart_hover)

    def _render_pie_chart(self, specialty_data):
        self._clear_chart_container(self._specialty_canvas_container)
        self._specialty_canvas = None

        labels = [row[0] or "Sem Especialidade" for row in specialty_data]
        values = [int(row[1] or 0) for row in specialty_data]
        pie_colors = [
            COLORS.get("primary", "#06B6D4"),
            COLORS.get("secondary", "#3B82F6"),
            COLORS.get("success", "#10B981"),
            COLORS.get("warning", "#F59E0B"),
            COLORS.get("danger", "#EF4444"),
            COLORS.get("info", "#8B5CF6"),
            COLORS.get("purple", "#A855F7"),
            COLORS.get("gray", "#6B7280"),
        ]

        fig = Figure(figsize=(7, 3.3), dpi=100, facecolor=COLORS["card"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(COLORS["card"])

        if sum(values) == 0:
            empty_label = ctk.CTkLabel(
                self._specialty_canvas_container,
                text="Nenhum dado disponível",
                font=font("small"),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(padx=12, pady=12)
            return

        total = sum(values)
        wedges, _, autotexts = ax.pie(
            values,
            labels=None,
            colors=pie_colors[: len(values)],
            startangle=90,
            autopct=lambda pct: f"{pct:.0f}%",
            pctdistance=0.82,
            textprops={"color": COLORS["text"], "fontsize": 9},
            wedgeprops={"width": 0.58, "edgecolor": COLORS["card"], "linewidth": 1.2}
        )

        for autotext in autotexts:
            autotext.set_color(COLORS["text"])
            autotext.set_fontsize(8)
            autotext.set_fontweight("bold")

        legend_labels = [f"{label}: {int(round((value / total) * 100))}%" for label, value in zip(labels, values)]
        ax.legend(
            wedges,
            legend_labels,
            loc="center left",
            bbox_to_anchor=(1.0, 0.5),
            frameon=False,
            fontsize=9,
            labelcolor=COLORS["text"],
        )

        ax.set_title("Consultas por Especialidade", color=COLORS["text"], fontsize=10, pad=8)
        ax.axis("equal")
        fig.subplots_adjust(left=0.02, right=0.76, top=0.9, bottom=0.08)

        canvas = FigureCanvasTkAgg(fig, master=self._specialty_canvas_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=0, pady=0)
        self._specialty_canvas = canvas

        specialty_tooltip = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox={"boxstyle": "round,pad=0.4", "fc": COLORS["card"], "ec": COLORS["border"], "alpha": 0.96},
            fontsize=9,
            color=COLORS["text"],
            zorder=10,
            visible=False,
        )

        def _on_specialty_hover(event):
            if event.inaxes != ax:
                specialty_tooltip.set_visible(False)
                canvas.draw_idle()
                return

            for index, (wedge, row) in enumerate(zip(wedges, specialty_data)):
                contains, _ = wedge.contains(event)
                if contains:
                    total_value = int(row[1] or 0)
                    participation = int(round((total_value / total) * 100))
                    specialty_tooltip.set_text(
                        f"{labels[index]}\n"
                        f"Total: {total_value}\n"
                        f"Agendadas: {int(row[2] or 0)}\n"
                        f"Realizadas: {int(row[3] or 0)}\n"
                        f"Canceladas: {int(row[4] or 0)}\n"
                        f"Faltas: {int(row[5] or 0)}\n"
                        f"Participação: {participation}%"
                    )
                    offset_x = -155 if event.x > ax.bbox.x1 - 170 else 18
                    is_upper_region = event.y > ax.bbox.y1 - 105
                    offset_y = -10 if is_upper_region else 10
                    specialty_tooltip.set_verticalalignment("top" if is_upper_region else "bottom")
                    specialty_tooltip.xytext = (offset_x, offset_y)
                    specialty_tooltip.xy = (event.xdata, event.ydata)
                    specialty_tooltip.set_visible(True)
                    canvas.draw_idle()
                    return

            specialty_tooltip.set_visible(False)
            canvas.draw_idle()

        canvas.mpl_connect("motion_notify_event", _on_specialty_hover)

    def _render_productivity(self, productivity_rows):
        for child in self._productivity_rows_frame.winfo_children():
            child.destroy()

        if not productivity_rows:
            empty_label = ctk.CTkLabel(
                self._productivity_rows_frame,
                text="Nenhum médico encontrado para o período selecionado.",
                font=font("small"),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(anchor="w", pady=12)
            return

        for index, row_data in enumerate(productivity_rows):
            medico, especialidade, consultas = row_data
            consultas_value = int(consultas or 0)
            row_bg = COLORS["bg_soft"] if index % 2 == 0 else COLORS["card"]

            row = ctk.CTkFrame(self._productivity_rows_frame, fg_color=row_bg, corner_radius=12)
            row.pack(fill="x", padx=0, pady=8)
            row.grid_columnconfigure(0, weight=1, uniform="ranking_cols")
            row.grid_columnconfigure(1, weight=4, uniform="ranking_cols")
            row.grid_columnconfigure(2, weight=3, uniform="ranking_cols")
            row.grid_columnconfigure(3, weight=1, uniform="ranking_cols")
            row.grid_rowconfigure(0, weight=1)

            medal = ["🥇", "🥈", "🥉"][index] if index < 3 else f"#{index + 1}"
            ctk.CTkLabel(row, text=medal, font=font("text", "bold"), text_color=COLORS["text"], anchor="center").grid(row=0, column=0, sticky="nsew", padx=(12, 8), pady=(10, 10))
            ctk.CTkLabel(row, text=medico or "-", font=font("text", "bold"), text_color=COLORS["text"], anchor="w").grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=(10, 10))

            specialty_cell = ctk.CTkFrame(row, fg_color="transparent")
            specialty_cell.grid(row=0, column=2, sticky="nsew", padx=(0, 8), pady=(10, 10))
            specialty_cell.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(specialty_cell, text=especialidade or "-", font=font("text", "bold"), text_color=COLORS["text_secondary"], anchor="w", justify="left").grid(row=0, column=0, sticky="nsew", padx=(12, 0))

            consult_cell = ctk.CTkFrame(row, fg_color="transparent")
            consult_cell.grid(row=0, column=3, sticky="nsew", padx=(0, 12), pady=(10, 10))
            consult_cell.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(consult_cell, text=str(consultas_value), font=font("text", "bold"), text_color=COLORS["text"], anchor="center", justify="center").grid(row=0, column=0, sticky="nsew")

    def _update_filter_options(self, medicos, especialidades):
        if medicos:
            values = ["Todos"] + [medico[1] for medico in medicos]
            self._medicos_map = {"Todos": None}
            self._medicos_map.update({medico[1]: medico[0] for medico in medicos})
            try:
                self.medico_combo.configure(values=values)
            except Exception:
                pass

        if especialidades:
            values = ["Todos"] + [especialidade[1] for especialidade in especialidades]
            self._especialidades_map = {"Todos": None}
            self._especialidades_map.update({especialidade[1]: especialidade[0] for especialidade in especialidades})
            try:
                self.especialidade_combo.configure(values=values)
            except Exception:
                pass

    def _apply_loaded_data(self, summary, chart_period, specialty_data, productivity_rows, medicos, especialidades):
        if summary is None:
            return

        self._stat_value_labels["Pacientes Únicos Atendidos"].configure(text=str(summary["pacientes_unicos_atendidos"]))
        self._stat_value_labels["Faltas"].configure(text=str(summary["faltas"]))
        self._stat_value_labels["Novos Pacientes"].configure(text=str(summary["novos_pacientes"]))
        self._stat_value_labels["Consultas Agendadas"].configure(text=str(summary["consultas_agendadas"]))

        self._current_report_data = self._build_export_payload(summary, chart_period, specialty_data, productivity_rows)
        if self.export_button is not None:
            self.export_button.configure(state="normal")

        self._update_kpi_cards(summary, productivity_rows)

        if medicos is not None or especialidades is not None:
            self._update_filter_options(medicos or [], especialidades or [])

        if chart_period:
            self._render_bar_chart(chart_period)
        if specialty_data is not None:
            self._render_pie_chart(specialty_data)
        if productivity_rows is not None:
            self._render_productivity(productivity_rows)

    def _update_kpi_cards(self, summary, productivity_rows):
        total_consultas = summary.get("total_consultas", 0)
        cancelamentos = summary.get("cancelamentos", 0)
        comparecimento_pct = summary.get("comparecimento", 0)

        if self._kpi_card_labels.get("total_consultas"):
            self._kpi_card_labels["total_consultas"]["value"].configure(text=str(total_consultas))

        if self._kpi_card_labels.get("taxa_comparecimento"):
            comparecimento_text = f"{int(comparecimento_pct)}%" if total_consultas else "--"
            self._kpi_card_labels["taxa_comparecimento"]["value"].configure(text=comparecimento_text)

        if self._kpi_card_labels.get("taxa_cancelamento"):
            if total_consultas:
                taxa_cancelamento = round((cancelamentos / total_consultas) * 100)
                self._kpi_card_labels["taxa_cancelamento"]["value"].configure(text=f"{taxa_cancelamento}%")
            else:
                self._kpi_card_labels["taxa_cancelamento"]["value"].configure(text="--")

        if self._kpi_card_labels.get("medico_mais_produtivo"):
            if productivity_rows:
                best_medico = productivity_rows[0][0] or "Nenhum"
                consultas = productivity_rows[0][2] or 0
                self._kpi_card_labels["medico_mais_produtivo"]["value"].configure(text=best_medico)
                self._kpi_card_labels["medico_mais_produtivo"]["description"].configure(text=f"{consultas} consultas")
            else:
                self._kpi_card_labels["medico_mais_produtivo"]["value"].configure(text="Nenhum")
                self._kpi_card_labels["medico_mais_produtivo"]["description"].configure(text="Nenhuma consulta encontrada")

    def _process_load_queue(self):
        processed_item = None

        while True:
            try:
                item = self._load_queue.get_nowait()
            except queue.Empty:
                break

            thread_id, summary, chart_period, specialty_data, productivity_rows, medicos, especialidades, error_msg = item
            if thread_id == self._current_thread_id:
                processed_item = item
                break

        if processed_item is None:
            if self._loading:
                self.after(100, self._process_load_queue)
            return

        thread_id, summary, chart_period, specialty_data, productivity_rows, medicos, especialidades, error_msg = processed_item

        if self._timeout_id is not None:
            try:
                self.winfo_toplevel().after_cancel(self._timeout_id)
            except Exception:
                pass
            self._timeout_id = None

        self._loading = False
        self._stop_loading_animation()
        self.update_button.configure(state="normal")
        if self.export_button is not None:
            self.export_button.configure(state="disabled")
        self._loading_label.pack_forget()

        if error_msg:
            self._loading_label.configure(text=f"Erro ao carregar: {error_msg}")
            self._loading_label.pack(anchor="w", padx=20, pady=(0, 10))
            self._notify_initialization(error_msg)
            return

        self._apply_loaded_data(summary, chart_period, specialty_data, productivity_rows, medicos, especialidades)
        self._notify_initialization(None)

    def _notify_initialization(self, error=None):
        if self._initialization_reported:
            return
        if self._initialization_thread and self._initialization_thread.is_alive():
            if self.winfo_exists():
                self.after(10, lambda: self._notify_initialization(error))
            return
        self._initialization_reported = True
        if callable(self._on_initialization_complete):
            self._on_initialization_complete(error)

    def create_transactions_section(self):
        container = ctk.CTkFrame(self.main_container, fg_color=COLORS["card"],
                                corner_radius=12, border_width=1, border_color=COLORS["border"])
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(header, text="🧾 Transações",
                     font=font("subtitle", "bold")).pack(side="left")

        self.render_table(container)

    def render_table(self, container):
        table_container = ctk.CTkFrame(container, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuração de colunas
        def configure_table_grid(frame):
            frame.columnconfigure(0, weight=1, uniform="col")  # Data
            frame.columnconfigure(1, weight=4, uniform="col")  # Descrição
            frame.columnconfigure(2, weight=1, uniform="col")  # Tipo
            frame.columnconfigure(3, weight=1, uniform="col")  # Valor
        
        # ========== CABEÇALHO ==========
        headers_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 5))
        configure_table_grid(headers_frame)
        
        # Data
        ctk.CTkLabel(
            headers_frame, 
            text="Data", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=8)
        
        # Descrição
        ctk.CTkLabel(
            headers_frame, 
            text="Descrição", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=15, pady=8)
        
        # Tipo
        ctk.CTkLabel(
            headers_frame, 
            text="Tipo", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="center"
        ).grid(row=0, column=2, sticky="we", padx=0, pady=8)
        
        # Valor
        ctk.CTkLabel(
            headers_frame, 
            text="Valor", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="e"
        ).grid(row=0, column=3, sticky="e", padx=15, pady=8)
        
        # Linha separadora
        ctk.CTkFrame(table_container, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=5)
        
        # ========== DADOS DA TABELA ==========
        for i, (data, descricao, tipo, valor) in enumerate(self.transacoes):
            # Definir cor baseado no tipo
            cor = COLORS["primary"] if tipo.lower() == "receita" else COLORS["danger"]
            
            # Cor de fundo alternada
            bg = COLORS["bg_soft"] if i % 2 == 0 else "transparent"
            row_frame = ctk.CTkFrame(table_container, fg_color=bg, corner_radius=8)
            row_frame.pack(fill="x", pady=2)
            configure_table_grid(row_frame)
            
            # Data
            ctk.CTkLabel(
                row_frame, 
                text=data, 
                font=font("small"),
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=15, pady=8)
            
            # Descrição
            ctk.CTkLabel(
                row_frame, 
                text=descricao, 
                font=font("small"),
                anchor="w"
            ).grid(row=0, column=1, sticky="w", padx=15, pady=8)
            
            # Tipo (com badge)
            ctk.CTkLabel(
                row_frame, 
                text=tipo, 
                font=font("small", "bold"),
                text_color=("white", "white"),
                fg_color=cor,
                corner_radius=10,
                anchor="center",
                width=55,
                height=22
            ).grid(row=0, column=2, sticky="we", padx=0, pady=8)
            
            # Valor
            ctk.CTkLabel(
                row_frame, 
                text=f"R$ {valor:,.2f}".replace(",", "."), 
                font=font("small", "bold"), 
                text_color=cor,
                anchor="e"
            ).grid(row=0, column=3, sticky="e", padx=15, pady=8)

    def adicionar_transacao(self, data, descricao, tipo, valor):
        """Adiciona uma nova transação e sincroniza a interface"""
        self.transacoes.append((data, descricao, tipo, valor))
        self.atualizar_interface()
    
    def remover_transacao(self, indice):
        """Remove uma transação pelo índice e sincroniza a interface"""
        if 0 <= indice < len(self.transacoes):
            del self.transacoes[indice]
            self.atualizar_interface()
    
    def atualizar_interface(self):
        """Sincroniza todos os componentes da interface com os dados atuais"""
        # Limpar e reconstruir a interface
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def obter_transacoes(self):
        """Retorna a lista de transações"""
        return self.transacoes
    
    def obter_totais(self):
        """Retorna os totais de receita e despesa"""
        total_receita, total_despesa, lucro = self.calcular_kpis()
        return {
            "receita": total_receita,
            "despesa": total_despesa,
            "lucro": lucro
        }