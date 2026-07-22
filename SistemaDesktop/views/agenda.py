import threading
import os
from datetime import datetime, date
import time
import queue

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from config.database import get_connection

from .base import BaseScreen
from .theme import font, COLORS
from controllers.consulta_controller import ConsultaController
from .paciente_search_combo import PacienteSearchComboBox
from .date_picker_utils import build_month_days, format_month_label, parse_br_date


LOCAL_STATUS_COLORS = {
    'realizada': {'bg': '#D1FAE5', 'text': '#065F46'},
    'agendada': {'bg': '#FEF3C7', 'text': '#92400E'},
    'cancelada': {'bg': '#FEE2E2', 'text': '#991B1B'},
    'confirmada': {'bg': '#DBEAFE', 'text': '#1D4ED8'},
}


class CustomOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, *args, text_color_override=None, arrow_color=None, **kwargs):
        self._text_color_override = text_color_override
        self._arrow_color_override = arrow_color
        super().__init__(*args, **kwargs)

    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)

        if self._text_color_override is not None:
            self._text_label.configure(fg=self._text_color_override)

        if self._arrow_color_override is not None:
            self._canvas.itemconfig('dropdown_arrow', fill=self._arrow_color_override)

        self._canvas.delete("divider")
        self._canvas.create_line(
            self._current_width - 28, 6,
            self._current_width - 28, self._current_height - 6,
            fill=COLORS['divider'],
            width=1,
            tags="divider"
        )


class MonthlyDatePickerPopup(ctk.CTkToplevel):
    def __init__(self, master, target_widget, data_var, available_dates, on_select):
        super().__init__(master)
        self.withdraw()
        self.title("")
        self.overrideredirect(True)
        self.configure(fg_color=COLORS['card'])
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.transient(master)

        self.data_var = data_var
        self.available_dates = available_dates or []
        self.on_select = on_select
        self.current_year = date.today().year
        self.current_month = date.today().month
        self.selected_date = parse_br_date(self.data_var.get()) if self.data_var.get() else None
        self.parent_window = master
        self.target_widget = target_widget

        self._build_ui()
        self._position_popup()
        self.deiconify()
        self.lift()
        self.focus_set()

        self.bind("<Escape>", lambda _event: self.destroy())
        self.parent_window.bind("<Configure>", self._handle_parent_configure, add='+')
        self.target_widget.bind("<Configure>", self._handle_target_configure, add='+')
        self.parent_window.bind("<Button-1>", self._handle_global_click, add='+')

    def _handle_parent_configure(self, _event=None):
        self.after(10, self._position_popup)

    def _handle_target_configure(self, _event=None):
        self.after(10, self._position_popup)

    def _handle_global_click(self, event):
        if not self.winfo_exists():
            return
        try:
            widget = event.widget
            if widget is self:
                return
            if self.winfo_containing(event.x_root, event.y_root) is self:
                return
            if widget is self.target_widget or self.target_widget.winfo_containing(event.x_root, event.y_root) is self.target_widget:
                return
            self.destroy()
        except Exception:
            pass

    def _position_popup(self):
        if not self.winfo_exists():
            return
        try:
            self.update_idletasks()
            popup_width = self.winfo_reqwidth()
            popup_height = self.winfo_reqheight()

            field_x = self.target_widget.winfo_rootx()
            field_y = self.target_widget.winfo_rooty()
            field_width = self.target_widget.winfo_width()
            field_height = self.target_widget.winfo_height()

            parent_x = self.parent_window.winfo_rootx()
            parent_y = self.parent_window.winfo_rooty()
            parent_width = self.parent_window.winfo_width()
            parent_height = self.parent_window.winfo_height()

            below_y = field_y + field_height + 4
            above_y = field_y - popup_height - 4

            if below_y + popup_height <= parent_y + parent_height:
                x = field_x
                y = below_y
            elif above_y >= parent_y:
                x = field_x
                y = above_y
            else:
                x = field_x
                y = max(parent_y, min(below_y, parent_y + parent_height - popup_height))

            x = max(parent_x, min(x, parent_x + parent_width - popup_width))
            y = max(parent_y, min(y, parent_y + parent_height - popup_height))

            if popup_width > parent_width:
                x = parent_x
            if popup_height > parent_height:
                y = parent_y

            self.geometry(f"+{x}+{y}")
        except Exception:
            self.geometry("+0+0")

    def _build_ui(self):
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.header_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.header_frame.grid(row=0, column=0, columnspan=7, sticky='ew', padx=12, pady=(10, 8))

        self.prev_btn = ctk.CTkButton(
            self.header_frame,
            text='◀',
            width=28,
            height=24,
            fg_color='transparent',
            text_color=COLORS['text_primary'],
            hover_color=COLORS['bg_soft'],
            border_width=1,
            border_color=COLORS['border'],
            corner_radius=8,
            command=self._go_previous_month,
        )
        self.prev_btn.pack(side='left')

        self.month_label = ctk.CTkLabel(
            self.header_frame,
            text=format_month_label(self.current_year, self.current_month),
            font=font('text', 'bold'),
            text_color=COLORS['text_primary'],
        )
        self.month_label.pack(side='left', expand=True)

        self.next_btn = ctk.CTkButton(
            self.header_frame,
            text='▶',
            width=28,
            height=24,
            fg_color='transparent',
            text_color=COLORS['text_primary'],
            hover_color=COLORS['bg_soft'],
            border_width=1,
            border_color=COLORS['border'],
            corner_radius=8,
            command=self._go_next_month,
        )
        self.next_btn.pack(side='right')

        weekday_names = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S']
        self.weekday_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.weekday_frame.grid(row=1, column=0, columnspan=7, padx=8, pady=(0, 4))
        for idx, name in enumerate(weekday_names):
            ctk.CTkLabel(
                self.weekday_frame,
                text=name,
                font=font('small'),
                text_color=COLORS['text_muted'],
            ).grid(row=0, column=idx, padx=2)

        self.days_grid_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.days_grid_frame.grid(row=2, column=0, columnspan=7, padx=8, pady=(0, 10))

        self._render_days()

    def _render_days(self):
        self.month_label.configure(text=format_month_label(self.current_year, self.current_month))
        for widget in self.days_grid_frame.winfo_children():
            widget.destroy()

        cells = build_month_days(
            self.current_year,
            self.current_month,
            self.available_dates,
            self.selected_date,
        )

        row = 0
        col = 0
        for cell in cells:
            if cell['day'] is None:
                ctk.CTkLabel(self.days_grid_frame, text='').grid(row=row, column=col, padx=2, pady=2)
            else:
                is_selected = bool(cell['selected'])
                is_enabled = bool(cell['enabled'])
                btn = ctk.CTkButton(
                    self.days_grid_frame,
                    text=str(cell['day']),
                    width=30,
                    height=28,
                    corner_radius=8,
                    fg_color=COLORS['primary'] if is_selected else 'transparent',
                    text_color=COLORS['primary'] if is_selected else COLORS['text_primary'],
                    hover_color=COLORS['primary_soft'],
                    border_width=1,
                    border_color=COLORS['border'],
                    state='normal' if is_enabled else 'disabled',
                    command=lambda d=cell['date']: self._select_date(d) if is_enabled else None,
                )
                btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col == 7:
                col = 0
                row += 1

    def _go_previous_month(self):
        if self.current_month == 1:
            self.current_year -= 1
            self.current_month = 12
        else:
            self.current_month -= 1
        self._render_days()

    def _go_next_month(self):
        if self.current_month == 12:
            self.current_year += 1
            self.current_month = 1
        else:
            self.current_month += 1
        self._render_days()

    def _select_date(self, selected_date):
        if not selected_date:
            return
        formatted = selected_date.strftime('%d/%m/%Y')
        self.data_var.set(formatted)
        if self.on_select:
            self.on_select(formatted)
        self.destroy()


class HourSelectionPopup(ctk.CTkToplevel):
    def __init__(self, master, target_widget, hora_var, horarios, on_select):
        super().__init__(master)
        self.withdraw()
        self.title("")
        self.overrideredirect(True)
        self.configure(fg_color=COLORS['card'])
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.transient(master)

        self.master_window = master
        self.target_widget = target_widget
        self.hora_var = hora_var
        self.horarios = horarios or []
        self.on_select = on_select

        self._build_ui()
        self._position_popup()
        self.deiconify()
        self.lift()
        self.focus_set()

        self.bind("<Escape>", lambda _event: self.destroy())
        self.master_window.bind("<Button-1>", self._handle_global_click, add='+')
        self.target_widget.bind("<Configure>", self._handle_target_configure, add='+')

    def _handle_target_configure(self, _event=None):
        self.after(10, self._position_popup)

    def _handle_global_click(self, event):
        if not self.winfo_exists():
            return
        try:
            widget = event.widget
            if widget is self.target_widget or self.target_widget.winfo_containing(event.x_root, event.y_root) is self.target_widget:
                return
            if self.winfo_containing(event.x_root, event.y_root) is self:
                return
            self.destroy()
        except Exception:
            pass

    def _position_popup(self):
        if not self.winfo_exists():
            return
        try:
            self.update_idletasks()
            popup_width = self.winfo_reqwidth()
            popup_height = self.winfo_reqheight()
            field_x = self.target_widget.winfo_rootx()
            field_y = self.target_widget.winfo_rooty()
            field_height = self.target_widget.winfo_height()

            parent_x = self.master_window.winfo_rootx()
            parent_y = self.master_window.winfo_rooty()
            parent_width = self.master_window.winfo_width()
            parent_height = self.master_window.winfo_height()

            below_y = field_y + field_height + 4
            above_y = field_y - popup_height - 4

            if below_y + popup_height <= parent_y + parent_height:
                y = below_y
            elif above_y >= parent_y:
                y = above_y
            else:
                y = max(parent_y, min(below_y, parent_y + parent_height - popup_height))

            x = max(parent_x, min(field_x, parent_x + parent_width - popup_width))
            y = max(parent_y, min(y, parent_y + parent_height - popup_height))

            self.geometry(f"+{x}+{y}")
        except Exception:
            self.geometry("+0+0")

    def _build_ui(self):
        card = ctk.CTkFrame(
            self,
            fg_color=COLORS['card'],
            corner_radius=12,
            border_width=1,
            border_color=COLORS['border'],
        )
        card.pack(fill='both', expand=True, padx=8, pady=8)

        if not self.horarios:
            ctk.CTkLabel(
                card,
                text='Nenhum horário disponível para esta data.',
                font=font('text'),
                text_color=COLORS['text_muted'],
                justify='left',
            ).pack(anchor='w', padx=12, pady=12)
            return

        buttons_frame = ctk.CTkFrame(card, fg_color='transparent')
        buttons_frame.pack(padx=10, pady=10)

        for idx, horario in enumerate(self.horarios):
            btn = ctk.CTkButton(
                buttons_frame,
                text=horario,
                width=78,
                height=36,
                corner_radius=8,
                fg_color='transparent',
                border_width=1,
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
                hover_color=COLORS['primary_soft'],
                command=lambda value=horario: self._select_horario(value),
            )
            btn.grid(row=idx // 4, column=idx % 4, padx=4, pady=4)

    def _select_horario(self, horario):
        self.hora_var.set(horario)
        if self.on_select:
            self.on_select(horario)
        self.destroy()


class Agenda(BaseScreen):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, 'Agenda')

        self.clinica_id = clinica_id
        if self.clinica_id is None:
            print("[AGENDA] AVISO: clinica_id não fornecido; usando fallback 1")
            self.clinica_id = 1

        # --- DEFINIÇÃO DO LIMITE DE USUÁRIOS POR ABA ---
        self.limite_por_pagina = 7 
        # -----------------------------------------------

        self.data_var = ctk.StringVar(value='Todos')
        self.medico_var = ctk.StringVar(value='Todos')
        self.status_var = ctk.StringVar(value='Todos')
        self.especialidade_var = ctk.StringVar(value='Todos')

        # Flag para prevenir loops de trace_add durante inicialização
        self._trace_enabled = False
        
        # Proteção contra threads concorrentes
        self._loading = False
        self._current_thread_id = None
        self._timeout_id = None
        self._refresh_pending = False

        self.data_var.trace_add('write', self.aplicar_filtros)
        self.medico_var.trace_add('write', self.aplicar_filtros)
        self.status_var.trace_add('write', self.aplicar_filtros)
        self.especialidade_var.trace_add('write', self.aplicar_filtros)

        self.filtro_data = None
        self.filtro_medico = None
        self.filtro_status = None
        self.filtro_especialidade = None
        self.filtro_medico_id = None
        self.filtro_especialidade_id = None

        self.pagina_atual = 0
        self.paciente_selecionado = None
        self.current_snapshot = None
        self._auto_refresh_ms = 10000
        self.details_panel = None
        self.row_widgets = {}
        self._update_details_pending = False
        self._detail_update_id = None
        self._thread_count = 0
        self._render_start_time = None
        self._load_queue = queue.Queue()

        self.colors = {
            'page_bg': COLORS['bg'],
            'bg_card': COLORS['card'],
            'bg_soft': COLORS['bg_soft'],
            'bg_header': COLORS['bg_header'],
            'bg_main': COLORS['content_bg'],
            'text_primary': COLORS['text_primary'],
            'text_secondary': COLORS['text_secondary'],
            'text_muted': COLORS['text_muted'],
            'primary': COLORS['primary'],
            'primary_dark': COLORS['primary_dark'],
            'primary_soft': COLORS['primary_soft'],
            'hover': COLORS['hover'],
            'selected': COLORS['selected_row'],
            'border': COLORS['border'],
            'border_soft': COLORS['border'],
            'shadow': COLORS['shadow'] if 'shadow' in COLORS else COLORS['border'],
            'avatar_colors': ['#F59E0B', '#EF4444', '#EC4899', '#10B981', '#3B82F6']
        }

        # Configuração das colunas
        self.col_config = [
            {'key': 'avatar',        'minsize': 52,  'weight': 0, 'title': '',               'anchor': 'center', 'padx_left': 12, 'padx_right': 4},
            {'key': 'nome',          'minsize': 150, 'weight': 1, 'title': 'Nome',           'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'especialidade', 'minsize': 120, 'weight': 1, 'title': 'Especialidade', 'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'medico',        'minsize': 130, 'weight': 1, 'title': 'Médico',         'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'data',          'minsize': 100, 'weight': 0, 'title': 'Data',           'anchor': 'center', 'padx_left': 12, 'padx_right': 8},
            {'key': 'hora',          'minsize': 80,  'weight': 0, 'title': 'Hora',           'anchor': 'center', 'padx_left': 12, 'padx_right': 8},
            {'key': 'status',        'minsize': 130, 'weight': 0, 'title': 'Status',         'anchor': 'center', 'padx_left': 12, 'padx_right': 12},
        ]

        self.col_widths = {conf['key']: conf['minsize'] for conf in self.col_config}

        print(f"[Agenda] __init__ concluído. Iniciando render()")
        self._trace_enabled = True
        self.render()
        # Desabilitar auto-refresh por enquanto - causa loops infinitos
        # self.after(self._auto_refresh_ms, self._auto_check)

    def _get_data_sql(self):
        if not self.filtro_data or self.filtro_data in ['Todos', 'Data', '']:
            return None
        try:
            if isinstance(self.filtro_data, datetime):
                return self.filtro_data.date()
            if isinstance(self.filtro_data, date):
                return self.filtro_data
            if isinstance(self.filtro_data, str):
                if '-' in self.filtro_data and len(self.filtro_data) == 10:
                    return datetime.strptime(self.filtro_data, '%Y-%m-%d').date()
                d, m, y = self.filtro_data.split('/')
                return date(int(y), int(m), int(d))
        except Exception:
            print(f"[AGENDA] _get_data_sql: formato de data inválido ({self.filtro_data})")
            return None
        return None

    def set_column_spacing(self, column_key, minsize=None, weight=None):
        pass

    def set_column_padding(self, column_key, padx_left=None, padx_right=None):
        pass 

    def set_column_width(self, column_key, minsize=None):
        pass

    def aplicar_filtros(self, *_):
        # Prevenir execução durante inicialização
        if not self._trace_enabled:
            print(f"[Agenda] aplicar_filtros chamado mas trace_enabled=False, ignorando")
            return

        print(f"[Agenda] aplicar_filtros acionado")
        data_valor = self.data_var.get() or ''
        medico_valor = self.medico_var.get() or ''
        status_valor = self.status_var.get() or ''
        especialidade_valor = self.especialidade_var.get() or ''

        self.filtro_data = None if data_valor in ['Todos', 'Data', ''] else data_valor
        self.filtro_medico = None if medico_valor in ['Todos', 'Médico', ''] else medico_valor
        self.filtro_medico_id = None
        if self.filtro_medico:
            for medico_id, nome in self.medico_opcoes:
                if nome == self.filtro_medico:
                    self.filtro_medico_id = medico_id
                    break

        self.filtro_status = None if status_valor in ['Todos', 'Status', ''] else status_valor.lower()
        self.filtro_especialidade = None if especialidade_valor in ['Todos', 'Especialidade', ''] else especialidade_valor
        self.filtro_especialidade_id = None
        if self.filtro_especialidade:
            for especialidade_id, nome in self.especialidade_opcoes:
                if nome == self.filtro_especialidade:
                    self.filtro_especialidade_id = especialidade_id
                    break

        print(f"[FILTRO DATA] Valor selecionado: {self.filtro_data}")
        print(f"[FILTRO MÉDICO] Valor selecionado: {self.filtro_medico} (id={self.filtro_medico_id})")
        print(f"[FILTRO ESPECIALIDADE] Valor selecionado: {self.filtro_especialidade} (id={self.filtro_especialidade_id})")
        print(f"[FILTRO STATUS] Valor selecionado: {self.filtro_status}")

        self.pagina_atual = 0
        print(f"[Agenda] Filtros aplicados. Chamando refresh_data()")
        self.refresh_data()

    def _on_filtro_selected(self, var_name, value):
        print(f"[Agenda] _on_filtro_selected: {var_name} = {value}")
        # Avoid duplicate refresh calls: the StringVar trace already triggers aplicar_filtros.
        var = getattr(self, var_name)
        if var.get() != value:
            var.set(value)

    def _limpar_filtros(self):
        self.data_var.set('Todos')
        self.medico_var.set('Todos')
        self.status_var.set('Todos')
        self.especialidade_var.set('Todos')
        self.filtro_data = None
        self.filtro_medico = None
        self.filtro_medico_id = None
        self.filtro_status = None
        self.filtro_especialidade = None
        self.filtro_especialidade_id = None
        self.pagina_atual = 0
        print("[AGENDA] Filtros limpos")
        self.refresh_data()

    def _auto_check(self):
        """Auto-refresh desabilitado - usar refresh_data() manual"""
        pass

    def refresh_data(self):
        """Carrega dados em thread segura com proteção contra concorrência"""
        print(f"\n[AGENDA] ========== REFRESH_DATA INICIADO ==========")
        
        if self._loading:
            print(f"[AGENDA] refresh_data: BUSY, marcando refresh pendente")
            self._refresh_pending = True
            return
        
        print(f"[AGENDA] refresh_data: ativando _loading")
        self._loading = True
        self._thread_count += 1
        self._current_thread_id = self._thread_count
        thread_id = self._current_thread_id
        
        print(f"[AGENDA] refresh_data: iniciando thread #{thread_id}")
        
        def thread_wrapper():
            print(f"[AGENDA] thread #{thread_id}: INICIADA")
            try:
                self._load_data_thread()
            finally:
                print(f"[AGENDA] thread #{thread_id}: TERMINADA")
        
        thread = threading.Thread(target=thread_wrapper, daemon=False)  # NÃO daemon!
        thread.start()
        
        # Cancelar timeout anterior se existir
        if self._timeout_id is not None:
            try:
                self.after_cancel(self._timeout_id)
                print(f"[AGENDA] refresh_data: timeout anterior cancelado")
            except:
                pass
        
        # Agendar novo timeout
        print(f"[AGENDA] refresh_data: agendando timeout de 40s para thread #{thread_id}")
        self._timeout_id = self.winfo_toplevel().after(40000, lambda: self._timeout_loading(thread_id))
        self.winfo_toplevel().after(100, self._process_load_queue)

    def _timeout_loading(self, thread_id):
        """Força reset se carregamento demorar muito"""
        print(f"\n[AGENDA] ⏱️  TIMEOUT: carregamento da thread #{thread_id} demorou > 40s")
        
        if self._current_thread_id == thread_id:
            print(f"[AGENDA] ⏱️  TIMEOUT: ressetando _loading (era thread atual)")
            self._loading = False
            self._timeout_id = None
            self._render_after_load([], 0, [], [], [], "0-0-0-0")
        else:
            print(f"[AGENDA] ⏱️  TIMEOUT: ignorando (thread #{thread_id} não é thread atual #{self._current_thread_id})")

    def render(self):
        """Renderiza tela inicial de carregamento"""
        print(f"\n[AGENDA] ========== RENDER INICIADO ==========")
        
        if self._loading:
            print(f"[AGENDA] render: IGNORADO (já em carregamento)")
            return

        self._thread_count += 1
        self._current_thread_id = self._thread_count
        thread_id = self._current_thread_id
        print(f"[AGENDA] ======= RENDER ======= thread_id={thread_id} _current_thread_id={self._current_thread_id} _loading={self._loading}")
        print(f"[AGENDA] render: ativando _loading")
        self._loading = True
        self._render_start_time = time.time()

        print(f"[AGENDA] render: limpando widgets")
        for w in self.content_card.winfo_children():
            w.destroy()

        self.content_card.configure(fg_color=COLORS['card'])

        loading_wrap = ctk.CTkFrame(self.content_card, fg_color='transparent')
        loading_wrap.pack(fill='both', expand=True, padx=20, pady=20)

        loading_card = ctk.CTkFrame(
            loading_wrap,
            fg_color=self.colors['bg_card'],
            corner_radius=24,
            border_width=1,
            border_color=self.colors['border_soft']
        )
        loading_card.place(relx=0.5, rely=0.5, anchor='center')

        loading_lbl = ctk.CTkLabel(
            loading_card,
            text='Carregando consultas...',
            font=font("subtitle", "bold"),
            text_color=self.colors['text_secondary']
        )
        loading_lbl.pack(padx=40, pady=28)

        print(f"[AGENDA] render: iniciando thread #{thread_id} para carregar dados")
        
        def thread_wrapper():
            print(f"[AGENDA] thread render #{thread_id}: INICIADA")
            try:
                self._load_data_thread()
            finally:
                print(f"[AGENDA] thread render #{thread_id}: TERMINADA")
        
        thread = threading.Thread(target=thread_wrapper, daemon=False)  # NÃO daemon!
        thread.start()
        
        # Cancelar timeout anterior se existir
        if self._timeout_id is not None:
            try:
                self.after_cancel(self._timeout_id)
                print(f"[AGENDA] render: timeout anterior cancelado")
            except:
                pass
        
        # Agendar novo timeout
        print(f"[AGENDA] render: agendando timeout de 40s para thread #{thread_id}")
        self._timeout_id = self.winfo_toplevel().after(40000, lambda: self._timeout_loading(thread_id))
        self.winfo_toplevel().after(100, self._process_load_queue)

    def _load_data_thread(self):
        """Carrega dados de consultas - envia resultados para o thread principal via fila"""
        print(f"[AGENDA] _load_data_thread: INICIADA")
        
        thread_id = self._current_thread_id
        data_sql = self._get_data_sql()
        consultas = []
        total = 0
        datas = []
        medicos = []
        especialidades = []
        snapshot = "0-0-0-0"
        error_msg = None
        
        try:
            print(f"[AGENDA] _load_data_thread: analisando filtros")
            print(f"[AGENDA]   - data={self.filtro_data}")
            print(f"[AGENDA]   - medico={self.filtro_medico}")
            print(f"[AGENDA]   - status={self.filtro_status}")
            print(f"[AGENDA]   - especialidade={self.filtro_especialidade}")
            
            # ============================================
            # 1. listar_por_clinica
            # ============================================
            print(f"====== CHAMADA listar_por_clinica ======")
            print(f"data = {self.filtro_data}")
            print(f"medico_id = {self.filtro_medico_id}")
            print(f"status = {self.filtro_status}")
            print(f"especialidade_id = {self.filtro_especialidade_id}")
            print(f"[AGENDA] → Chamando ConsultaController.listar_por_clinica()")
            start_call = time.time()
            
            try:
                consultas = ConsultaController.listar_por_clinica(
                    self.clinica_id,
                    pagina=self.pagina_atual,
                    limite=self.limite_por_pagina,
                    data=data_sql,
                    status=self.filtro_status,
                    medico=self.filtro_medico,
                    especialidade=self.filtro_especialidade,
                    medico_id=self.filtro_medico_id,
                    especialidade_id=self.filtro_especialidade_id,
                )
                
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ✓ listar_por_clinica OK ({elapsed_call:.3f}s) - retornou {len(consultas) if consultas else 0} registros")
            except Exception as e:
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ❌ listar_por_clinica FALHOU ({elapsed_call:.3f}s): {e}")
                import traceback
                traceback.print_exc()
                raise
            
            # ============================================
            # 2. contar_por_clinica
            # ============================================
            print(f"[AGENDA] → Chamando ConsultaController.contar_por_clinica()")
            start_call = time.time()
            
            try:
                total = ConsultaController.contar_por_clinica(
                    self.clinica_id,
                    data=data_sql,
                    status=self.filtro_status,
                    medico=self.filtro_medico,
                    especialidade=self.filtro_especialidade,
                    medico_id=self.filtro_medico_id,
                    especialidade_id=self.filtro_especialidade_id,
                )
                
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ✓ contar_por_clinica OK ({elapsed_call:.3f}s) - total={total}")
            except Exception as e:
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ❌ contar_por_clinica FALHOU ({elapsed_call:.3f}s): {e}")
                import traceback
                traceback.print_exc()
                raise
            
            # ============================================
            # 3. listar_opcoes_filtro
            # ============================================
            print(f"[AGENDA] → Chamando ConsultaController.listar_opcoes_filtro()")
            start_call = time.time()
            
            try:
                datas, medicos, especialidades = ConsultaController.listar_opcoes_filtro(self.clinica_id)
                
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ✓ listar_opcoes_filtro OK ({elapsed_call:.3f}s)")
            except Exception as e:
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ❌ listar_opcoes_filtro FALHOU ({elapsed_call:.3f}s): {e}")
                import traceback
                traceback.print_exc()
                raise
            
            # ============================================
            # 4. snapshot_por_clinica
            # ============================================
            print(f"[AGENDA] → Chamando ConsultaController.snapshot_por_clinica()")
            start_call = time.time()
            
            try:
                snapshot = ConsultaController.snapshot_por_clinica(
                    self.clinica_id,
                    data=data_sql,
                    status=self.filtro_status,
                    medico=self.filtro_medico,
                    especialidade=self.filtro_especialidade,
                    medico_id=self.filtro_medico_id,
                    especialidade_id=self.filtro_especialidade_id,
                )
                
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ✓ snapshot_por_clinica OK ({elapsed_call:.3f}s)")
            except Exception as e:
                elapsed_call = time.time() - start_call
                print(f"[AGENDA] ❌ snapshot_por_clinica FALHOU ({elapsed_call:.3f}s): {e}")
                import traceback
                traceback.print_exc()
                raise

            # ============================================
            # SUCESSO: Todos os dados carregados
            # ============================================
            print(f"[AGENDA] ✅ TODOS OS DADOS CARREGADOS COM SUCESSO")
            print(f"[AGENDA] → Agendando _render_after_load() no thread principal")
            
            self._load_queue.put((thread_id, consultas, total, datas, medicos, especialidades, snapshot, None))
            print(f"[AGENDA] ✓ _load_data_thread: resultado enviado para UI thread")

        except Exception as e:
            # Qualquer erro em qualquer método do controller
            error_msg = str(e)
            print(f"\n[AGENDA] ❌ ERRO FATAL em _load_data_thread: {error_msg}")
            import traceback
            traceback.print_exc()
            
            self._load_queue.put((thread_id, [], 0, [], [], [], "0-0-0-0", error_msg))
            print(f"[AGENDA] ✓ _load_data_thread: erro enviado para UI thread")
        
        finally:
            # ============================================
            # FINALIZAR thread de dados sem tocar na UI diretamente
            # ============================================
            print(f"[AGENDA] _load_data_thread: FINALIZANDO (finally block)")
            print(f"[AGENDA] _loading antes: {self._loading}")
            print(f"[AGENDA] _load_data_thread: FINALIZADA\n")


    def _render_error(self, message):
        """Exibe erro na tela com garantia de reset"""
        print(f"[AGENDA] _render_error: {message}")
        
        try:
            print(f"[AGENDA] _render_error: destruindo widgets")
            for w in self.content_card.winfo_children():
                w.destroy()

            print(f"[AGENDA] _render_error: criando card de erro")
            wrapper = ctk.CTkFrame(self.content_card, fg_color='transparent')
            wrapper.pack(fill='both', expand=True, padx=20, pady=20)

            card = ctk.CTkFrame(
                wrapper,
                fg_color=self.colors['bg_card'],
                corner_radius=24,
                border_width=2,
                border_color=COLORS["danger"]
            )
            card.place(relx=0.5, rely=0.5, anchor='center')

            ctk.CTkLabel(
                card,
                text='❌ Falha ao carregar Agenda',
                text_color=COLORS["danger"],
                font=font("subtitle", "bold"),
                justify='center'
            ).pack(padx=32, pady=(28, 12))
            
            ctk.CTkLabel(
                card,
                text=f'{message}',
                text_color=self.colors['text_secondary'],
                font=font("text"),
                justify='center',
                wraplength=300
            ).pack(padx=32, pady=(0, 20))
            
            # Botão para tentar novamente
            ctk.CTkButton(
                card,
                text='↻ Tentar Novamente',
                fg_color=COLORS['primary'],
                hover_color=COLORS['primary_dark'],
                text_color='white',
                command=self.refresh_data
            ).pack(padx=32, pady=(0, 28))
            
            print(f"[AGENDA] _render_error: card exibido com sucesso")
            
        except Exception as e:
            print(f"[AGENDA] ❌ _render_error: ERRO ao renderizar error card: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # CRÍTICO: SEMPRE garantir que loading seja False
            print(f"[AGENDA] _render_error: finally block - resetando _loading")
            self._loading = False

    def _process_load_queue(self):
        print(f"[AGENDA] _process_load_queue chamado; _loading={self._loading} queue_size={self._load_queue.qsize()}")
        try:
            item = self._load_queue.get_nowait()
        except queue.Empty:
            print(f"[AGENDA] _process_load_queue: fila vazia")
            if self._loading:
                self.after(100, self._process_load_queue)
            return

        thread_id, consultas, total, datas, medicos, especialidades, snapshot, error_msg = item
        if thread_id != self._current_thread_id:
            print(f"[AGENDA] _process_load_queue: ignorando resultado de thread #{thread_id} (atual #{self._current_thread_id})")
            return

        if self._timeout_id is not None:
            try:
                self.winfo_toplevel().after_cancel(self._timeout_id)
            except Exception:
                pass
            self._timeout_id = None

        self._loading = False
        refresh_pending = self._refresh_pending
        self._refresh_pending = False

        print(f"[AGENDA] _process_load_queue: thread_id={thread_id} _current_thread_id={self._current_thread_id} consultas_id={id(consultas)} len={len(consultas)} refresh_pending={refresh_pending}")
        if consultas:
            try:
                print(f"[AGENDA] _process_load_queue: primeira data={consultas[0][2]}")
            except Exception:
                pass

        if error_msg:
            print(f"[AGENDA] _process_load_queue: erro na carga, exibindo mensagem de erro")
            self._render_error(error_msg)
            return

        self._render_after_load(consultas, total, datas, medicos, especialidades, snapshot)

        if refresh_pending:
            print(f"[AGENDA] _process_load_queue: refresh pendente detectado após render, chamando refresh_data()")
            self.refresh_data()

    def _render_after_load(self, consultas, total, datas, medicos, especialidades, snapshot):
        """Renderiza tela com dados carregados - GARANTE sempre resetar _loading"""
        print(f"\n[AGENDA] ========== _RENDER_AFTER_LOAD INICIADA ==========")
        
        try:
            print(f"[AGENDA] ======= _RENDER_AFTER_LOAD ======= consultas_id={id(consultas)} len={len(consultas)}")
            if consultas:
                try:
                    print(f"[AGENDA] _render_after_load: primeira data={consultas[0][2]}")
                except Exception:
                    pass
            print(f"[AGENDA] _render_after_load: resetando _loading IMEDIATAMENTE")
            self._loading = False
            self.current_snapshot = snapshot

            print(f"[AGENDA] _render_after_load: destruindo widgets antigos")
            for w in self.content_card.winfo_children():
                w.destroy()

            print(f"[AGENDA] _render_after_load: configurando grid")
            self.content_card.grid_columnconfigure(0, weight=4)
            self.content_card.grid_columnconfigure(1, weight=1)
            self.content_card.grid_rowconfigure(0, weight=1)

            print(f"[AGENDA] _render_after_load: criando frames esquerdo e direito")
            left = ctk.CTkFrame(self.content_card, fg_color='transparent')
            left.grid(row=0, column=0, sticky='nsew', padx=(20, 10), pady=20)
            left.grid_columnconfigure(0, weight=1)
            left.grid_rowconfigure(3, weight=1)

            right = ctk.CTkFrame(self.content_card, fg_color=COLORS['bg_soft'], corner_radius=15)
            right.grid(row=0, column=1, sticky='nsew', padx=(10, 20), pady=20)
            right.grid_columnconfigure(0, weight=1)
            self.details_panel = right

            print(f"[AGENDA] _render_after_load: renderizando filtros")
            self._render_filtros(left, datas, medicos, especialidades)
            
            print(f"[AGENDA] _render_after_load: renderizando info")
            self._render_info_top(left, total)

            print(f"[AGENDA] _render_after_load: criando tabela")
            # ==============================
            # TABELA (SEM CABEÇALHO)
            # ==============================
            content_frame = ctk.CTkFrame(
                left,
                fg_color=COLORS['card'],
                corner_radius=15,
                border_width=1,
                border_color=COLORS['border']
            )
            content_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)

            table_container = ctk.CTkFrame(content_frame, fg_color='transparent')
            table_container.grid(row=0, column=0, sticky='nsew', padx=8)
            table_container.grid_columnconfigure(0, weight=1)
            table_container.grid_rowconfigure(0, weight=1)

            # LISTA APENAS - SEM CABEÇALHO
            list_area = ctk.CTkFrame(
                table_container,
                fg_color='transparent',
            )
            list_area.grid(row=0, column=0, sticky='nsew')
            list_area.grid_columnconfigure(0, weight=1)

            if not consultas:
                print(f"[AGENDA] _render_after_load: sem consultas, exibindo empty state")
                empty_box = ctk.CTkFrame(list_area, fg_color='transparent')
                empty_box.grid(row=0, column=0, sticky='nsew', pady=50)

                ctk.CTkLabel(
                    empty_box,
                    text='Nenhuma consulta encontrada.',
                    text_color=self.colors['text_secondary'],
                    font=ctk.CTkFont(size=16, weight='bold')
                ).pack(pady=(20, 6))

                ctk.CTkLabel(
                    empty_box,
                    text='Tente ajustar os filtros.',
                    text_color=self.colors['text_muted'],
                    font=ctk.CTkFont(size=13)
                ).pack()
            else:
                print(f"[AGENDA] _render_after_load: renderizando {len(consultas)} linhas")
            self._render_rows(list_area, consultas)

            print(f"[AGENDA] _render_after_load: renderizando paginação")
            self.render_pagination(left, total)
            
            print(f"[AGENDA] _render_after_load: renderizando painel de detalhes")
            self.render_details_panel(right)
            
            elapsed = time.time() - (self._render_start_time or time.time())
            print(f"[AGENDA] ✅ _render_after_load CONCLUÍDA em {elapsed:.3f}s\n")

        except Exception as e:
            print(f"[AGENDA] ❌ _render_after_load ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentar exibir erro
            try:
                self._render_error(f"Falha ao renderizar agenda: {str(e)}")
            except:
                pass
        
        finally:
            # CRÍTICO: SEMPRE garantir que loading seja False
            print(f"[AGENDA] _render_after_load: finally block - garantindo _loading=False")
            self._loading = False

    def _render_filtros(self, parent, datas, medicos, especialidades):
        filtros_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['card'],
            corner_radius=18,
            border_width=1,
            border_color=COLORS['border']
        )
        filtros_card.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        filtros_card.grid_columnconfigure(0, weight=1)

        linha = ctk.CTkFrame(filtros_card, fg_color='transparent')
        linha.pack(fill='x', padx=12, pady=12)

        def filtro(texto, values, var_name):
            frame = ctk.CTkFrame(linha, fg_color=COLORS['card'], corner_radius=12)

            partes = texto.split(' ', 1)
            icone = partes[0] if partes else ""
            texto_label = partes[1] if len(partes) > 1 else ""

            cores_icones = {
                "📅": "#06B6D4",
                "🩺": "#06B6D4",
                "📊": "#06B6D4",
                "🦷": "#06B6D4",
            }
            cor_icone = cores_icones.get(icone, self.colors['text_primary'])

            header = ctk.CTkFrame(frame, fg_color="transparent")
            header.pack(anchor='w', padx=10, pady=(12, 0))

            ctk.CTkLabel(
                header,
                text=icone,
                font=ctk.CTkFont(size=28, weight='normal'),
                text_color=cor_icone,
            ).pack(side='left', padx=(0, 6))

            ctk.CTkLabel(
                header,
                text=texto_label,
                font=ctk.CTkFont(size=14, weight='normal'),
                text_color=self.colors['text_primary'],
            ).pack(side='left')

            combo = ctk.CTkComboBox(
                frame,
                values=values,
                height=34,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                button_color=COLORS['primary'],
                button_hover_color=COLORS['primary_dark'],
                corner_radius=8,
                variable=getattr(self, var_name),
                command=lambda value, var_name=var_name: self._on_filtro_selected(var_name, value)
            )
            combo.pack(fill='x', padx=10, pady=(6, 10))

            return frame

        self.medico_opcoes = []
        if medicos:
            self.medico_opcoes = list(medicos)
        self.especialidade_opcoes = []
        if especialidades:
            self.especialidade_opcoes = list(especialidades)

        medico_labels = ['Todos'] + [nome for _, nome in self.medico_opcoes]
        especialidade_labels = ['Todos'] + [nome for _, nome in self.especialidade_opcoes]

        filtro_data = filtro("📅 Data", ['Todos'] + [d.strftime('%d/%m/%Y') for d in datas], 'data_var')
        filtro_medico = filtro("🩺 Médico", medico_labels, 'medico_var')
        filtro_status = filtro("📊 Status", ['Todos', 'Agendada', 'Confirmada', 'Realizada', 'Cancelada'], 'status_var')
        filtro_especialidade = filtro("🦷 Especialidade", especialidade_labels, 'especialidade_var')

        filtro_data.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        filtro_medico.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        filtro_status.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        filtro_especialidade.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        button_width = 140
        button_wrap = ctk.CTkFrame(linha, fg_color='transparent')
        button_wrap.pack(side='left', padx=(4, 0), pady=(12, 4), anchor='n')
        button_wrap.pack_propagate(True)

        botao_limpar = ctk.CTkButton(
            button_wrap,
            text='🗑 Limpar',
            width=button_width,
            height=30,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger"],
            text_color='white',
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight='bold'),
            command=self._limpar_filtros
        )
        botao_limpar.pack(fill='x', pady=(2, 2))

        botao = ctk.CTkButton(
            button_wrap,
            text='↻ Atualizar',
            width=button_width,
            height=30,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight='bold'),
            command=self.refresh_data
        )
        botao.pack(fill='x', pady=(2, 2))

        botao_marcar = ctk.CTkButton(
            button_wrap,
            text='➕ Marcar Consulta',
            width=button_width,
            height=32,
            fg_color=COLORS["success"],
            hover_color=COLORS["success"],
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight='bold'),
            command=self.abrir_dialogo_marcar_consulta
        )
        botao_marcar.pack(fill='x', pady=(2, 2))

    def _render_info_top(self, parent, total):
        info_wrap = ctk.CTkFrame(parent, fg_color='transparent')
        info_wrap.grid(row=1, column=0, sticky='ew', pady=(0, 10))

        ctk.CTkLabel(
            info_wrap,
            text=f'Total de consultas: {total}',
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color=self.colors['text_secondary']
        ).pack(anchor='w', padx=4)

    def _render_rows(self, container, consultas):
        print(f"[AGENDA] _render_rows: consultas_id={id(consultas)} len={len(consultas)}")
        if consultas:
            try:
                print(f"[AGENDA] _render_rows: primeira data={consultas[0][2]}")
            except Exception:
                pass
        self.image_cache = []
        self.row_widgets = {}

        for idx, item in enumerate(consultas):
            (
                consulta_id, nome, data_hora, status, telefone, email, sexo,
                data_nascimento, cpf, foto, observacoes, medico_nome, especialidade
            ) = item

            status_key = (status or '').lower()
            row_color = self.colors['selected'] if self.paciente_selecionado == consulta_id else COLORS['card']

            row = ctk.CTkFrame(
                container,
                fg_color=row_color,
                corner_radius=14,
                height=58,
                border_width=0
            )
            row.grid(row=idx, column=0, sticky='ew', pady=4)
            row.grid_propagate(False)
            row.grid_rowconfigure(0, weight=1)
            
            for col_idx, conf in enumerate(self.col_config):
                row.grid_columnconfigure(col_idx, minsize=conf['minsize'], weight=conf['weight'])

            self.row_widgets[consulta_id] = row

            row.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            row.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            row.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            avatar_conf = self.col_config[0]
            padx_left = avatar_conf.get('padx_left', 8)
            padx_right = avatar_conf.get('padx_right', 8)
            
            avatar = ctk.CTkLabel(
                row,
                width=36,
                height=36,
                corner_radius=18,
                fg_color='transparent',
                text='',
                compound='center'
            )
            avatar.grid(row=0, column=0, sticky='nsew', padx=(padx_left, padx_right), pady=0)

            avatar_img = self._create_avatar_image(nome, foto, 36)
            avatar.configure(image=avatar_img)
            avatar.image = avatar_img
            self.image_cache.append(avatar_img)

            avatar.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            avatar.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            avatar.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            nome_conf = self.col_config[1]
            padx_left = nome_conf.get('padx_left', 8)
            padx_right = nome_conf.get('padx_right', 8)
            nome_label = ctk.CTkLabel(
                row,
                text=(nome or 'Não informado'),
                font=ctk.CTkFont(size=13, weight='bold'),
                text_color=self.colors['text_primary'],
                anchor=nome_conf['anchor']
            )
            nome_label.grid(row=0, column=1, sticky='ew', padx=(padx_left, padx_right), pady=0)
            nome_label.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            nome_label.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            nome_label.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            espec_conf = self.col_config[2]
            padx_left = espec_conf.get('padx_left', 8)
            padx_right = espec_conf.get('padx_right', 8)
            espec_label = ctk.CTkLabel(
                row,
                text=(especialidade or '-'),
                font=ctk.CTkFont(size=13),
                text_color=self.colors['text_secondary'],
                anchor=espec_conf['anchor']
            )
            espec_label.grid(row=0, column=2, sticky='ew', padx=(padx_left, padx_right), pady=0)
            espec_label.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            espec_label.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            espec_label.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            med_conf = self.col_config[3]
            padx_left = med_conf.get('padx_left', 8)
            padx_right = med_conf.get('padx_right', 8)
            med_label = ctk.CTkLabel(
                row,
                text=(medico_nome or '-'),
                font=ctk.CTkFont(size=13),
                text_color=self.colors['text_secondary'],
                anchor=med_conf['anchor']
            )
            med_label.grid(row=0, column=3, sticky='ew', padx=(padx_left, padx_right), pady=0)
            med_label.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            med_label.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            med_label.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            data_conf = self.col_config[4]
            padx_left = data_conf.get('padx_left', 8)
            padx_right = data_conf.get('padx_right', 8)
            data_label = ctk.CTkLabel(
                row,
                text=data_hora.strftime('%d/%m/%Y') if data_hora else '-',
                font=ctk.CTkFont(size=13),
                text_color=self.colors['text_secondary'],
                anchor=data_conf['anchor']
            )
            data_label.grid(row=0, column=4, sticky='ew', padx=(padx_left, padx_right), pady=0)
            data_label.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            data_label.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            data_label.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            hora_conf = self.col_config[5]
            padx_left = hora_conf.get('padx_left', 8)
            padx_right = hora_conf.get('padx_right', 8)
            hora_label = ctk.CTkLabel(
                row,
                text=data_hora.strftime('%H:%M') if data_hora else '-',
                font=ctk.CTkFont(size=13),
                text_color=self.colors['text_secondary'],
                anchor=hora_conf['anchor']
            )
            hora_label.grid(row=0, column=5, sticky='ew', padx=(padx_left, padx_right), pady=0)
            hora_label.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            hora_label.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            hora_label.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

            status_conf = self.col_config[6]
            padx_left = status_conf.get('padx_left', 8)
            padx_right = status_conf.get('padx_right', 8)
            
            estilo_status = LOCAL_STATUS_COLORS.get(status_key, {'bg': COLORS['border'], 'text': COLORS['text_secondary']})

            status_wrap = ctk.CTkFrame(row, fg_color="transparent")
            status_wrap.grid(row=0, column=6, sticky='ew', padx=(padx_left, padx_right), pady=0)

            badge = ctk.CTkFrame(
                status_wrap,
                fg_color=estilo_status['bg'],
                corner_radius=12,
                height=30
            )
            
            if status_conf['anchor'] == 'center':
                badge.pack(expand=True, pady=14)
            else:
                badge.pack(side='left', pady=14)

            badge.pack_propagate(False)

            lbl_badge = ctk.CTkLabel(
                badge,
                text=status or '-',
                text_color=estilo_status['text'],
                font=ctk.CTkFont(size=11, weight='bold')
            )
            lbl_badge.pack(padx=12, pady=6)
            
            lbl_badge.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            badge.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            badge.bind('<Enter>', lambda e, r=row, cid=consulta_id: self._on_row_enter(r, cid))
            badge.bind('<Leave>', lambda e, r=row, cid=consulta_id: self._on_row_leave(r, cid))

    def _on_row_enter(self, row, cid):
        if self.paciente_selecionado == cid:
            row.configure(fg_color=self.colors['selected'])
        else:
            row.configure(fg_color=COLORS['hover'])

    def _on_row_leave(self, row, cid):
        if self.paciente_selecionado == cid:
            row.configure(fg_color=self.colors['selected'])
        else:
            row.configure(fg_color=COLORS['card'])

    def _create_avatar_image(self, nome, foto, size):
        if foto:
            try:
                root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                path = os.path.join(root, 'media', foto)
                if os.path.exists(path):
                    img = Image.open(path).convert('RGB')
                    min_d = min(img.size)
                    img = img.crop((
                        (img.width - min_d) // 2,
                        (img.height - min_d) // 2,
                        (img.width + min_d) // 2,
                        (img.height + min_d) // 2
                    ))
                    img = img.resize((size, size), Image.Resampling.LANCZOS)

                    mask = Image.new('L', (size, size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, size, size), fill=255)
                    img.putalpha(mask)

                    return ctk.CTkImage(light_image=img, size=(size, size))
            except Exception:
                pass

        inicial = (nome or '?')[0].upper() if nome else '?'
        color = self.colors['avatar_colors'][hash(nome) % len(self.colors['avatar_colors'])] if nome else self.colors['avatar_colors'][0]

        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill=color)

        try:
            fonte = ImageFont.truetype('arial.ttf', int(size * 0.50))
        except Exception:
            fonte = ImageFont.load_default()

        draw.text((size / 2, size / 2), inicial, fill='white', font=fonte, anchor='mm')
        return ctk.CTkImage(light_image=img, size=(size, size))

    def render_pagination(self, parent, total_items):
        pag_wrap = ctk.CTkFrame(parent, fg_color='transparent')
        pag_wrap.grid(row=4, column=0, sticky='e', pady=(4, 2))

        paginas = max(1, (total_items + self.limite_por_pagina - 1) // self.limite_por_pagina)

        pag_frame = ctk.CTkFrame(
            pag_wrap,
            fg_color='transparent'
        )
        pag_frame.pack(anchor='e')

        for i in range(paginas):
            ativo = i == self.pagina_atual

            ctk.CTkButton(
                pag_frame,
                text=str(i + 1),
                width=36,
                height=36,
                corner_radius=10,
                fg_color=self.colors['primary'] if ativo else COLORS['card'],
                hover_color=self.colors['primary_dark'] if ativo else COLORS['bg_soft'],
                border_width=1,
                border_color=self.colors['primary'] if ativo else self.colors['border'],
                text_color='white' if ativo else self.colors['text_secondary'],
                font=ctk.CTkFont(size=12, weight='bold'),
                command=lambda p=i: self.mudar_pagina(p)
            ).pack(side='left', padx=3)

    def render_details_panel(self, parent):
        # Limpa o painel sem destruição abrupta
        for w in parent.winfo_children():
            w.destroy()
        
        # Força atualização da UI para evitar flicker
        parent.update_idletasks()

        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors['bg_card'],
            corner_radius=22,
            border_width=1,
            border_color=self.colors['border_soft']
        )
        card.pack(fill='both', expand=True)

        if not self.paciente_selecionado:
            empty = ctk.CTkFrame(card, fg_color='transparent')
            empty.place(relx=0.5, rely=0.5, anchor='center')

            ctk.CTkLabel(
                empty,
                text='Selecione uma consulta',
                font=ctk.CTkFont(size=18, weight='bold'),
                text_color=self.colors['text_secondary']
            ).pack(pady=(0, 6))

            ctk.CTkLabel(
                empty,
                text='Os detalhes da consulta aparecerão aqui.',
                font=ctk.CTkFont(size=13),
                text_color=self.colors['text_muted']
            ).pack()
            return

        consulta = ConsultaController.buscar_por_id(self.paciente_selecionado)
        if not consulta:
            ctk.CTkLabel(
                card,
                text='Consulta não encontrada.',
                text_color=COLORS["danger"]
            ).pack(pady=20)
            return

        (
            consulta_id, nome, data_hora, status, telefone, email, sexo,
            data_nascimento, cpf, foto, observacoes, medico_nome, especialidade
        ) = consulta

        status_key = (status or '').lower()
        estilo_status = LOCAL_STATUS_COLORS.get(status_key, {'bg': COLORS['border'], 'text': COLORS['text_secondary']})

        top = ctk.CTkFrame(card, fg_color='transparent')
        top.pack(fill='x', pady=(18, 10))
        top.pack_propagate(False)
        top.configure(height=90)

        top_inner = ctk.CTkFrame(top, fg_color='transparent')
        top_inner.pack(fill='both', expand=True, padx=18)

        avatar_img = self._create_avatar_image(nome, foto, 64)
        avatar_lbl = ctk.CTkLabel(top_inner, image=avatar_img, text='', width=64, height=64, corner_radius=32)
        avatar_lbl.image = avatar_img
        avatar_lbl.grid(row=0, column=0, rowspan=2, padx=(0, 12))

        ctk.CTkLabel(
            top_inner,
            text=nome or 'Paciente',
            font=ctk.CTkFont(size=20, weight='bold'),
            text_color=self.colors['text_primary']
        ).grid(row=0, column=1, sticky='w')

        status_blk = ctk.CTkFrame(top_inner, fg_color=estilo_status['bg'], corner_radius=12)
        status_blk.grid(row=1, column=1, sticky='w', pady=(6, 0))

        ctk.CTkLabel(
            status_blk,
            text=(status or '-'),
            text_color=estilo_status['text'],
            font=ctk.CTkFont(size=11, weight='bold')
        ).pack(padx=12, pady=5)

        info_container = ctk.CTkFrame(card, fg_color='transparent')
        info_container.pack(fill='x', pady=(0, 8))

        info_inner = ctk.CTkFrame(info_container, fg_color='transparent')
        info_inner.pack(fill='x', padx=18)

        self._detail_item(info_inner, f'Médico: {medico_nome or "-"}')
        self._detail_item(info_inner, f'Especialidade: {especialidade or "-"}')
        self._detail_item(info_inner, f'Data e Hora: {data_hora.strftime("%d/%m/%Y %H:%M") if data_hora else "-"}')
        self._detail_item(info_inner, f'Telefone: {telefone or "-"}')
        self._detail_item(info_inner, f'E-mail: {email or "-"}')
        self._detail_item(info_inner, f'Sexo: {sexo or "-"}')
        self._detail_item(info_inner, f'Idade: {self.calcular_idade(data_nascimento) or "-"}')
        self._detail_item(info_inner, f'CPF: {cpf or "-"}')

        obs_title_container = ctk.CTkFrame(card, fg_color='transparent')
        obs_title_container.pack(fill='x', pady=(10, 6))

        obs_title_inner = ctk.CTkFrame(obs_title_container, fg_color='transparent')
        obs_title_inner.pack(fill='x', padx=18)

        ctk.CTkLabel(
            obs_title_inner,
            text='Observações',
            font=ctk.CTkFont(size=15, weight='bold'),
            text_color=self.colors['text_primary']
        ).pack(anchor='w')

        obs_container = ctk.CTkFrame(card, fg_color='transparent')
        obs_container.pack(fill='x', pady=(0, 18), padx=18)

        obs = ctk.CTkTextbox(
            obs_container,
            height=140,
            fg_color=COLORS['bg_soft'],
            border_width=1,
            border_color=self.colors['border'],
            corner_radius=12
        )
        obs.pack(fill='both', expand=True)
        obs.insert('1.0', observacoes or 'Sem observações registradas.')
        obs.configure(state='disabled')

    def _detail_item(self, parent, text):
        row = ctk.CTkFrame(parent, fg_color=COLORS['bg_soft'], corner_radius=12)
        row.pack(fill='x', pady=4)

        ctk.CTkLabel(
            row,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color=self.colors['text_secondary']
        ).pack(anchor='w', padx=12, pady=10)

    def selecionar_paciente(self, consulta_id):
        self.paciente_selecionado = consulta_id

        for cid, row in self.row_widgets.items():
            row.configure(fg_color=self.colors['selected'] if cid == consulta_id else COLORS['card'])

        # Cancela qualquer atualização pendente
        if self._detail_update_id is not None:
            self.after_cancel(self._detail_update_id)
        
        # Agenda a atualização do painel com debounce (reduz flicker)
        if self.details_panel:
            self._detail_update_id = self.after(50, lambda: self.render_details_panel(self.details_panel))

    def mudar_pagina(self, pagina):
        self.pagina_atual = pagina
        self.render()

    def calcular_idade(self, data_nascimento):
        if not data_nascimento:
            return ''
        if isinstance(data_nascimento, str):
            from datetime import datetime
            data_nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()

        hoje = date.today()
        anos = hoje.year - data_nascimento.year

        if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
            anos -= 1

        return f'{anos} anos'

    def abrir_dialogo_marcar_consulta(self):
        """Abre uma janela de diálogo para marcar uma nova consulta com integração ao banco"""
        from datetime import datetime
        from tkinter import messagebox
        
        dialogo = ctk.CTkToplevel(self.master)
        dialogo.title("Marcar Consulta")
        dialogo.geometry("650x800")
        dialogo.resizable(False, False)
        dialogo.grab_set()

        db_conn = None
        db_lock = threading.Lock()
        cache_especialidades = []
        cache_medicos_por_especialidade = {}
        cache_agenda = {}

        def get_db_connection():
            nonlocal db_conn
            if db_conn is None:
                db_conn = get_connection()
            return db_conn

        def close_db_connection():
            nonlocal db_conn
            if db_conn is not None:
                try:
                    db_conn.close()
                except Exception:
                    pass
                db_conn = None

        def on_dialog_close():
            close_db_connection()
            dialogo.destroy()

        dialogo.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        # Frame principal
        main_frame = ctk.CTkFrame(dialogo, fg_color=COLORS['bg'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="➕ Marcar Nova Consulta",
            font=font("large_title", "bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=(0, 20))
        
        # Frame com scroll
        canvas_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=COLORS['card'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
        canvas_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # ===================== CAMPO PACIENTE (SEARCH COMBOBOX) =====================
        paciente_header = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        paciente_header.pack(anchor='w', padx=15, pady=(15, 5))

        ctk.CTkLabel(
            paciente_header,
            text="👤",
            font=font("subtitle"),
            text_color=COLORS['primary']
        ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            paciente_header,
            text="Paciente",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(side='left')
        
        paciente_id_selecionado = {'id': None}
        paciente_info_selecionado = {'data': None}
        
        def ao_selecionar_paciente(id_pac, nome, cpf, email, telefone, data_nasc):
            """Callback ao selecionar um paciente."""
            paciente_id_selecionado['id'] = id_pac
            paciente_info_selecionado['data'] = (id_pac, nome, cpf, email, telefone, data_nasc)
        
        paciente_combo = PacienteSearchComboBox(
            canvas_frame,
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            corner_radius=8,
            command=ao_selecionar_paciente
        )
        paciente_combo.pack(fill='x', padx=15, pady=(0, 15))
        
        # ===================== CAMPO ESPECIALIDADE (SELETOR) =====================
        especialidade_header = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        especialidade_header.pack(anchor='w', padx=15, pady=(0, 5))

        ctk.CTkLabel(
            especialidade_header,
            text="🦷",
            font=font("subtitle"),
            text_color=COLORS['primary']
        ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            especialidade_header,
            text="Especialidade",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(side='left')
        
        especialidade_var = ctk.StringVar(value="")
        especialidade_id_selecionado = {'id': None}
        especialidade_status_var = ctk.StringVar(value="")
        especialidades_carregadas = []

        def _preencher_medicos(medicos, especialidade_nome, expected_especialidade_id):
            if especialidade_id_selecionado['id'] != expected_especialidade_id:
                return

            medico_display.clear()
            valores_medicos = []
            for id_med, nome_med in medicos:
                display_text = f"{nome_med} - {especialidade_nome}" if especialidade_nome else nome_med
                medico_display[display_text] = id_med
                valores_medicos.append(display_text)

            if valores_medicos:
                medico_combo.configure(values=valores_medicos, state='normal')
                medico_var.set("")
            else:
                medico_combo.configure(values=[], state='disabled')
                medico_var.set("Nenhum médico disponível")

        def _carregar_medicos_por_especialidade_thread(especialidade_id, especialidade_nome):
            if not especialidade_id:
                return

            if especialidade_id in cache_medicos_por_especialidade:
                _preencher_medicos(cache_medicos_por_especialidade[especialidade_id], especialidade_nome, especialidade_id)
                return

            medico_combo.configure(values=[], state='disabled')
            medico_var.set("Carregando médicos...")

            def _task():
                start_ms = time.perf_counter()
                conn = get_db_connection()
                with db_lock:
                    medicos_por_especialidade = ConsultaController.carregar_medicos_por_especialidade(
                        especialidade_id,
                        self.clinica_id,
                        conn=conn
                    )
                elapsed_ms = (time.perf_counter() - start_ms) * 1000
                print(f"[agenda] Médicos para especialidade {especialidade_id} carregados em {elapsed_ms:.0f} ms")
                cache_medicos_por_especialidade[especialidade_id] = medicos_por_especialidade
                dialogo.after(0, _preencher_medicos, medicos_por_especialidade, especialidade_nome, especialidade_id)

            threading.Thread(target=_task, daemon=True).start()

        def atualizar_especialidade_selecionada(value):
            """Atualiza o ID interno com base na lista já carregada."""
            for especialidade_id, nome in especialidades_carregadas:
                if nome == value:
                    especialidade_id_selecionado['id'] = especialidade_id
                    break
            else:
                especialidade_id_selecionado['id'] = None

            medico_id_selecionado['id'] = None
            medico_display.clear()
            medico_combo.configure(values=[], state='disabled')
            medico_var.set("")
            limpar_data_e_hora()

            if especialidade_id_selecionado['id'] is not None:
                _carregar_medicos_por_especialidade_thread(
                    especialidade_id_selecionado['id'],
                    value or ""
                )

            especialidade_status_var.set("")

        def _set_especialidades(values):
            if values:
                especialidade_combo.configure(values=values, state='normal')
                especialidade_var.set("")
                especialidade_id_selecionado['id'] = None
                especialidade_status_var.set("")
            else:
                especialidade_combo.configure(values=[], state='disabled')
                especialidade_var.set("")
                especialidade_id_selecionado['id'] = None
                especialidade_status_var.set("Nenhuma especialidade cadastrada.")

        def _carregar_especialidades():
            nonlocal especialidades_carregadas
            start_ms = time.perf_counter()
            conn = get_db_connection()
            with db_lock:
                especialidades_db = ConsultaController.listar_especialidades(conn=conn)
            especialidades = ConsultaController.preparar_especialidades_para_combo(especialidades_db)
            elapsed_ms = (time.perf_counter() - start_ms) * 1000
            print(f"[agenda] Especialidades carregadas em {elapsed_ms:.0f} ms")
            especialidades_carregadas = especialidades
            valores = [nome for _, nome in especialidades]
            dialogo.after(0, _set_especialidades, valores)

        def carregar_especialidades_combo():
            especialidade_combo.configure(values=[], state='disabled')
            especialidade_var.set("Carregando especialidades...")
            threading.Thread(target=_carregar_especialidades, daemon=True).start()

        especialidade_combo = ctk.CTkComboBox(
            canvas_frame,
            variable=especialidade_var,
            values=[],
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_dark'],
            corner_radius=8,
            command=atualizar_especialidade_selecionada
        )
        especialidade_combo.pack(fill='x', padx=15, pady=(0, 5))
        carregar_especialidades_combo()

        especialidade_status_label = ctk.CTkLabel(
            canvas_frame,
            textvariable=especialidade_status_var,
            font=font("text"),
            text_color=COLORS['warning'] if 'warning' in COLORS else '#FFA500'
        )
        especialidade_status_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        # ===================== CAMPO MÉDICO (VINCULADO À CLÍNICA) =====================
        medico_header = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        medico_header.pack(anchor='w', padx=15, pady=(0, 5))

        ctk.CTkLabel(
            medico_header,
            text="🩺",
            font=font("subtitle"),
            text_color=COLORS['primary']
        ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            medico_header,
            text="Médico",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(side='left')
        
        medico_display = {}
        medico_id_selecionado = {'id': None}
        datas_disponiveis = []
        horarios_disponiveis = []
        hora_selecionada = {'value': None}
        
        medico_var = ctk.StringVar(value="")

        def limpar_data_e_hora():
            data_var.set("")
            try:
                data_entry.configure(state='disabled')
            except Exception:
                pass
            hora_var.set("")
            try:
                hora_entry.configure(state='disabled')
            except Exception:
                pass
            try:
                if hora_popup is not None and hora_popup.winfo_exists():
                    hora_popup.destroy()
            except Exception:
                pass
            info_label.configure(text="")
            datas_disponiveis.clear()
            horarios_disponiveis.clear()
            hora_selecionada['value'] = None

        def atualizar_datas_disponiveis():
            medico_id = medico_id_selecionado.get('id')
            if not medico_id:
                limpar_data_e_hora()
                return

            data_var.set("")
            hora_var.set("")
            hora_selecionada['value'] = None

            agenda = cache_agenda.get(medico_id)
            if not agenda:
                _carregar_agenda_medico_thread(medico_id)
                return

            datas = agenda.get('datas', [])
            datas_disponiveis.clear()
            datas_disponiveis.extend(datas)

            if not datas:
                try:
                    data_entry.configure(state='disabled')
                except Exception:
                    pass
                return

            try:
                data_entry.configure(state='normal')
            except Exception:
                pass

        def _carregar_agenda_medico_thread(medico_id):
            if not medico_id:
                return

            if medico_id in cache_agenda:
                dialogo.after(0, atualizar_datas_disponiveis)
                return

            limpar_data_e_hora()
            data_var.set("")
            data_entry.configure(state='disabled')

            def _task():
                start_ms = time.perf_counter()
                conn = get_db_connection()
                with db_lock:
                    agenda = ConsultaController.carregar_agenda_disponivel(
                        medico_id,
                        self.clinica_id,
                        dias_ahead=60,
                        conn=conn
                    )
                elapsed_ms = (time.perf_counter() - start_ms) * 1000
                print(f"[agenda] Agenda do médico {medico_id} carregada em {elapsed_ms:.0f} ms")
                cache_agenda[medico_id] = agenda
                dialogo.after(0, atualizar_datas_disponiveis)

            threading.Thread(target=_task, daemon=True).start()

        def selecionar_medico(display_text):
            medico_id_selecionado['id'] = medico_display.get(display_text)
            _carregar_agenda_medico_thread(medico_id_selecionado['id'])

        medico_combo = ctk.CTkComboBox(
            canvas_frame,
            values=[],
            variable=medico_var,
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            button_color=COLORS['primary'],
            button_hover_color=COLORS['primary_dark'],
            corner_radius=8,
            state='disabled',
            command=selecionar_medico
        )
        medico_combo.pack(fill='x', padx=15, pady=(0, 15))

        data_header = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        data_header.pack(anchor='w', padx=15, pady=(0, 5))

        ctk.CTkLabel(
            data_header,
            text="📅",
            font=font("subtitle"),
            text_color=COLORS['primary']
        ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            data_header,
            text="Data da Consulta",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(side='left')
        
        data_var = ctk.StringVar(value="")

        def abrir_calendario_data(*args):
            if data_entry.cget('state') == 'disabled' or not datas_disponiveis:
                return
            popup = MonthlyDatePickerPopup(
                dialogo,
                target_widget=data_entry,
                data_var=data_var,
                available_dates=datas_disponiveis,
                on_select=lambda value: atualizar_horarios_disponiveis(),
            )

        data_entry = ctk.CTkEntry(
            canvas_frame,
            textvariable=data_var,
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            corner_radius=8,
            state='disabled',
        )
        data_entry.pack(fill='x', padx=15, pady=(0, 5))
        data_entry.bind('<Button-1>', abrir_calendario_data)
        data_entry.bind('<Return>', abrir_calendario_data)
        
        # ===================== CAMPO HORA =====================
        hora_header = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        hora_header.pack(anchor='w', padx=15, pady=(0, 5))

        ctk.CTkLabel(
            hora_header,
            text="🕐",
            font=font("subtitle"),
            text_color=COLORS['primary']
        ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            hora_header,
            text="Hora da Consulta",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(side='left')
        
        hora_var = ctk.StringVar(value="")
        hora_popup = None

        def abrir_popup_horas(*args):
            nonlocal hora_popup
            if not data_var.get().strip():
                return
            if hora_popup is not None and hora_popup.winfo_exists():
                hora_popup.destroy()
            hora_popup = HourSelectionPopup(
                dialogo,
                target_widget=hora_entry,
                hora_var=hora_var,
                horarios=horarios_disponiveis,
                on_select=lambda value: atualizar_hora_selecionada(),
            )

        hora_entry = ctk.CTkEntry(
            canvas_frame,
            textvariable=hora_var,
            height=40,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            corner_radius=8,
            state='disabled',
        )
        hora_entry.pack(fill='x', padx=15, pady=(0, 5))
        hora_entry.bind('<Button-1>', abrir_popup_horas)
        hora_entry.bind('<Return>', abrir_popup_horas)
        
        # Info de horários ocupados
        info_label = ctk.CTkLabel(
            canvas_frame,
            text="",
            font=font("text"),
            text_color=COLORS['text_muted'],
            justify='left'
        )
        info_label.pack(anchor='w', padx=15, pady=(0, 10))
        
        def atualizar_horarios_disponiveis(*args):
            medico_id = medico_id_selecionado.get('id')
            if not medico_id:
                horarios_disponiveis.clear()
                hora_var.set("")
                hora_selecionada['value'] = None
                return

            raw_data = data_var.get().strip()
            if not raw_data:
                horarios_disponiveis.clear()
                hora_var.set("")
                hora_selecionada['value'] = None
                return

            agenda = cache_agenda.get(medico_id)
            if not agenda:
                _carregar_agenda_medico_thread(medico_id)
                return

            horarios = agenda.get('horarios_por_data', {}).get(raw_data, [])
            horarios_disponiveis.clear()
            horarios_disponiveis.extend(horarios)
            hora_var.set("")
            hora_selecionada['value'] = None

            if not horarios:
                try:
                    hora_entry.configure(state='normal')
                except Exception:
                    pass
                return

            try:
                hora_entry.configure(state='normal')
            except Exception:
                pass

        def atualizar_hora_selecionada(*args):
            selecionado = hora_var.get().strip()
            if selecionado in horarios_disponiveis:
                hora_selecionada['value'] = selecionado
            else:
                hora_selecionada['value'] = None

        data_var.trace_add('write', atualizar_horarios_disponiveis)
        hora_var.trace_add('write', atualizar_hora_selecionada)
        
        # ===================== CAMPO OBSERVAÇÕES =====================
        obs_header = ctk.CTkFrame(canvas_frame, fg_color="transparent")
        obs_header.pack(anchor='w', padx=15, pady=(0, 5))

        ctk.CTkLabel(
            obs_header,
            text="📝",
            font=font("subtitle"),
            text_color=COLORS['primary']
        ).pack(side='left', padx=(0, 6))

        ctk.CTkLabel(
            obs_header,
            text="Observações (opcional)",
            font=font("subtitle"),
            text_color=COLORS['text_primary']
        ).pack(side='left')
        
        obs_text = ctk.CTkTextbox(
            canvas_frame,
            height=100,
            fg_color=COLORS['input_bg'],
            border_color=COLORS['border'],
            border_width=1,
            corner_radius=8
        )
        obs_text.pack(fill='x', padx=15, pady=(0, 15))
        
        # ===================== VALIDAÇÃO E SALVAMENTO =====================
        def validar_e_salvar():
            """Valida todos os campos e salva a consulta"""
            
            # Validação 1: Paciente
            if not paciente_id_selecionado.get('id'):
                messagebox.showerror("Validação", "❌ Selecione um paciente válido")
                return
            
            # Validação 2: Médico
            if not medico_id_selecionado.get('id'):
                messagebox.showerror("Validação", "❌ Selecione um médico")
                return
            
            # Validação 3: Data
            if not data_var.get():
                messagebox.showerror("Validação", "❌ Preencha a data")
                return
            
            valido_data, msg_data, data_obj = ConsultaController.validar_data_consulta(data_var.get())
            if not valido_data:
                messagebox.showerror("Validação", f"❌ {msg_data}")
                return
            
            # Validação 4: Hora
            if not hora_var.get():
                messagebox.showerror("Validação", "❌ Preencha a hora")
                return
            
            valido_hora, msg_hora, hora_obj = ConsultaController.validar_hora_consulta(hora_var.get())
            if not valido_hora:
                messagebox.showerror("Validação", f"❌ {msg_hora}")
                return
            
            # Validação 5: Especialidade
            if not especialidade_id_selecionado.get('id'):
                messagebox.showerror("Validação", "❌ Selecione uma especialidade")
                return
            
            # Validação 6: Verificar disponibilidade de horário
            from datetime import datetime as dt
            data_hora = dt.combine(data_obj.date(), hora_obj)
            
            disponivel, msg_horario = ConsultaController.verificar_disponibilidade_horario(
                medico_id_selecionado['id'],
                data_hora.date(),
                data_hora.time()
            )
            
            if not disponivel:
                messagebox.showerror("Horário Indisponível", f"❌ {msg_horario}")
                return
            
            # ============ SALVAR CONSULTA ============
            resultado = ConsultaController.salvar_nova_consulta(
                self.clinica_id,
                paciente_id_selecionado['id'],
                medico_id_selecionado['id'],
                data_hora,
                especialidade_var.get(),
                status='agendada',
                observacoes=obs_text.get('1.0', 'end-1c'),
                especialidade_id=especialidade_id_selecionado['id']
            )
            
            if resultado.get('sucesso'):
                messagebox.showinfo(
                    "Sucesso",
                    "✓ Consulta marcada com sucesso!"
                )
                self.refresh_data()
                try:
                    app = getattr(self.master, 'master', None)
                    if app and hasattr(app, 'frames') and 'painel' in app.frames:
                        app.frames['painel'].refresh()
                except Exception as e:
                    print(f"Erro ao atualizar Painel após salvar consulta: {e}")
                dialogo.destroy()
            else:
                messagebox.showerror(
                    "Erro ao Salvar",
                    f"❌ {resultado.get('mensagem', 'Erro desconhecido')}"
                )
        
        # Frame de botões
        button_frame = ctk.CTkFrame(main_frame, fg_color='transparent')
        button_frame.pack(fill='x', pady=(0, 0))
        
        btn_salvar = ctk.CTkButton(
            button_frame,
            text="✓ Salvar Consulta",
            height=40,
            fg_color=COLORS['primary'],
            hover_color=COLORS['primary_dark'],
            font=font("button", "bold"),
            command=validar_e_salvar
        )
        btn_salvar.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        btn_cancelar = ctk.CTkButton(
            button_frame,
            text="✕ Cancelar",
            height=40,
            fg_color="#DC3545",
            hover_color="#C82333",
            text_color="#FFFFFF",
            font=font("button", "bold"),
            command=dialogo.destroy
        )
        btn_cancelar.pack(side='left', fill='x', expand=True, padx=(5, 0))
    
    def _atualizar_especialidade_auto(self, medico_display_text, medico_display_dict, especialidade_var):
        """Atualiza automaticamente a especialidade quando médico é selecionado"""
        if not especialidade_var:
            return
        
        try:
            medico_id = medico_display_dict.get(medico_display_text)
            if medico_id:
                especialidade = ConsultaController.obter_especialidade_medico(medico_id)
                if especialidade:
                    especialidade_var.set(especialidade)
        except Exception as e:
            print(f"Erro ao atualizar especialidade: {e}")