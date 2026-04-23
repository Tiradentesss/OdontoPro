import threading
import os
from datetime import date

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from .base import BaseScreen
from .theme import font, COLORS
from controllers.consulta_controller import ConsultaController


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
            fill='#E5E7EB',
            width=1,
            tags="divider"
        )


class Agenda(BaseScreen):
    def __init__(self, parent, clinica_id):
        super().__init__(parent, 'Agenda')

        self.clinica_id = clinica_id

        # --- DEFINIÇÃO DO LIMITE DE USUÁRIOS POR ABA ---
        self.limite_por_pagina = 7 
        # -----------------------------------------------

        self.data_var = ctk.StringVar(value='Todos')
        self.medico_var = ctk.StringVar(value='Todos')
        self.status_var = ctk.StringVar(value='Todos')
        self.especialidade_var = ctk.StringVar(value='Todos')

        self.data_var.trace_add('write', self.aplicar_filtros)
        self.medico_var.trace_add('write', self.aplicar_filtros)
        self.status_var.trace_add('write', self.aplicar_filtros)
        self.especialidade_var.trace_add('write', self.aplicar_filtros)

        self.filtro_data = None
        self.filtro_medico = None
        self.filtro_status = None
        self.filtro_especialidade = None

        self.pagina_atual = 0
        self.paciente_selecionado = None
        self.current_snapshot = None
        self._loading = False
        self._auto_refresh_ms = 10000
        self.details_panel = None
        self.row_widgets = {}

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
            'shadow': COLORS['shadow'] if 'shadow' in COLORS else '#DCEAF7',
            'avatar_colors': ['#F59E0B', '#EF4444', '#EC4899', '#10B981', '#3B82F6']
        }

        # Configuração limpa e original para renderizar APENAS OS DADOS (as linhas coloridas)
        self.col_config = [
            {'key': 'avatar',        'minsize': 52,  'weight': 0, 'title': '',               'anchor': 'center', 'padx_left': 12, 'padx_right': 4},
            {'key': 'nome',          'minsize': 150, 'weight': 1, 'title': 'Nome',           'anchor': 'w',      'padx_left': 12, 'padx_right': 8}, 
            {'key': 'especialidade', 'minsize': 120, 'weight': 1, 'title': 'Especialidade', 'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'medico',        'minsize': 130, 'weight': 1, 'title': 'Médico',         'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'data',          'minsize': 100, 'weight': 0, 'title': 'Data',           'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'hora',          'minsize': 80,  'weight': 0, 'title': 'Hora',           'anchor': 'w',      'padx_left': 12, 'padx_right': 8},
            {'key': 'status',        'minsize': 130, 'weight': 0, 'title': 'Status',         'anchor': 'center', 'padx_left': 12, 'padx_right': 12}, 
        ]

        self.col_widths = {conf['key']: conf['minsize'] for conf in self.col_config}

        self.render()
        self.after(self._auto_refresh_ms, self._auto_check)

    def _get_data_sql(self):
        if not self.filtro_data or self.filtro_data in ['Todos', 'Data']:
            return None
        try:
            d, m, y = self.filtro_data.split('/')
            return f'{y}-{m.zfill(2)}-{d.zfill(2)}'
        except Exception:
            return None

    def set_column_spacing(self, column_key, minsize=None, weight=None):
        pass # Ignorado temporariamente para evitar loops desnecessários no exemplo

    def set_column_padding(self, column_key, padx_left=None, padx_right=None):
        pass 

    def set_column_width(self, column_key, minsize=None):
        pass

    def aplicar_filtros(self, *_):
        self.filtro_data = None if self.data_var.get() == 'Todos' else self.data_var.get()
        self.filtro_medico = None if self.medico_var.get() in ['Todos', 'Médico'] else self.medico_var.get()
        self.filtro_status = None if self.status_var.get() in ['Todos', 'Status'] else self.status_var.get()
        self.filtro_especialidade = None if self.especialidade_var.get() in ['Todos', 'Especialidade'] else self.especialidade_var.get()

        self.pagina_atual = 0
        self.refresh_data()

    def _limpar_filtros(self):
        self.data_var.set('Todos')
        self.medico_var.set('Todos')
        self.status_var.set('Todos')
        self.especialidade_var.set('Todos')
        self.filtro_data = None
        self.filtro_medico = None
        self.filtro_status = None
        self.filtro_especialidade = None
        self.pagina_atual = 0
        self.refresh_data()

    def _auto_check(self):
        try:
            snapshot = ConsultaController.snapshot_por_clinica(
                self.clinica_id,
                data=self._get_data_sql(),
                status=self.filtro_status,
                medico=self.filtro_medico,
                especialidade=self.filtro_especialidade,
            )

            if snapshot != self.current_snapshot:
                self.refresh_data()
        except Exception:
            pass
        finally:
            self.after(self._auto_refresh_ms, self._auto_check)

    def refresh_data(self):
        if self._loading:
            return
        self._loading = True
        threading.Thread(target=self._load_data_thread, daemon=True).start()

    def render(self):
        if self._loading:
            return

        self._loading = True

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

        threading.Thread(target=self._load_data_thread, daemon=True).start()

    def _load_data_thread(self):
        data_sql = self._get_data_sql()

        try:
            consultas = ConsultaController.listar_por_clinica(
                self.clinica_id,
                pagina=self.pagina_atual,
                limite=self.limite_por_pagina,
                data=data_sql,
                status=self.filtro_status,
                medico=self.filtro_medico,
                especialidade=self.filtro_especialidade,
            )
            total = ConsultaController.contar_por_clinica(
                self.clinica_id,
                data=data_sql,
                status=self.filtro_status,
                medico=self.filtro_medico,
                especialidade=self.filtro_especialidade,
            )

            datas, medicos, especialidades = ConsultaController.listar_opcoes_filtro(self.clinica_id)
            snapshot = ConsultaController.snapshot_por_clinica(
                self.clinica_id,
                data=data_sql,
                status=self.filtro_status,
                medico=self.filtro_medico,
                especialidade=self.filtro_especialidade,
            )

            self.after(0, lambda: self._render_after_load(consultas, total, datas, medicos, especialidades, snapshot))

        except Exception as e:
            print(f"[Agenda] _load_data_thread error: {e}")
            self.after(0, lambda: self._render_error(f"Erro na carga de dados: {e}"))

    def _render_error(self, message):
        self._loading = False
        for w in self.content_card.winfo_children():
            w.destroy()

        wrapper = ctk.CTkFrame(self.content_card, fg_color='transparent')
        wrapper.pack(fill='both', expand=True, padx=20, pady=20)

        card = ctk.CTkFrame(
            wrapper,
            fg_color=self.colors['bg_card'],
            corner_radius=24,
            border_width=1,
            border_color=self.colors['border']
        )
        card.place(relx=0.5, rely=0.5, anchor='center')

        ctk.CTkLabel(
            card,
            text=f'Erro ao carregar agenda:\n{message}',
            text_color='#EF4444',
            font=font("text", "bold"),
            justify='center'
        ).pack(padx=32, pady=28)

    def _render_after_load(self, consultas, total, datas, medicos, especialidades, snapshot):
        try:
            self._loading = False
            self.current_snapshot = snapshot

            for w in self.content_card.winfo_children():
                w.destroy()
        except Exception as e:
            print(f"[Agenda] _render_after_load error: {e}")
            self._render_error(f"Falha ao renderizar agenda: {e}")
            return

        self.content_card.grid_columnconfigure(0, weight=4)
        self.content_card.grid_columnconfigure(1, weight=1)
        self.content_card.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(self.content_card, fg_color='transparent')
        left.grid(row=0, column=0, sticky='nsew', padx=(20, 10), pady=20)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(3, weight=1)

        right = ctk.CTkFrame(self.content_card, fg_color='#f8fafc', corner_radius=15)
        right.grid(row=0, column=1, sticky='nsew', padx=(10, 20), pady=20)
        right.grid_columnconfigure(0, weight=1)
        self.details_panel = right

        self._render_filtros(left, datas, medicos, especialidades)
        self._render_info_top(left, total)

        content_frame = ctk.CTkFrame(
            left,
            fg_color='#ffffff',
            corner_radius=15,
            border_width=1,
            border_color='#e2e8f0'
        )
        content_frame.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)  

        table_container = ctk.CTkFrame(content_frame, fg_color='transparent')
        table_container.grid(row=0, column=0, sticky='nsew', padx=8, pady=0)
        table_container.grid_columnconfigure(0, weight=1)
        
        table_container.grid_rowconfigure(0, weight=0) # Cabeçalho
        table_container.grid_rowconfigure(1, weight=1) # Lista

        # =========================================================================
        # 1. CABEÇALHO 100% MANUAL, INDEPENDENTE E AJUSTÁVEL
        # =========================================================================
        header_frame = ctk.CTkFrame(table_container, fg_color='transparent', height=35, border_width=0)
        header_frame.grid(row=0, column=0, sticky='ew', padx=0, pady=(12, 4))
        header_frame.grid_propagate(False)
        header_frame.grid_rowconfigure(0, weight=1)

        # Configuramos a grade matemática exatamente igual à da lista para acompanhar telas
        header_frame.grid_columnconfigure(0, minsize=52,  weight=0)
        header_frame.grid_columnconfigure(1, minsize=150, weight=1)
        header_frame.grid_columnconfigure(2, minsize=120, weight=1)
        header_frame.grid_columnconfigure(3, minsize=130, weight=1)
        header_frame.grid_columnconfigure(4, minsize=100, weight=0)
        header_frame.grid_columnconfigure(5, minsize=80,  weight=0)
        header_frame.grid_columnconfigure(6, minsize=130, weight=0)

        h_font = ctk.CTkFont(size=13, weight='bold')
        h_color = self.colors.get('text_muted', '#9CA3AF')

        # COLUNA 0: Fica vazia para compensar o espaço da bolinha (Avatar)

        # COLUNA 1: Nome 
        lbl_nome = ctk.CTkLabel(header_frame, text="Nome", font=h_font, text_color=h_color, anchor='w')
        # <- MUDE O VALOR AQUI: Se "Nome" estiver para a esquerda, aumente o 58. Se estiver para direita, diminua.
        lbl_nome.grid(row=0, column=1, sticky='ew', padx=(58, 8)) 

        # COLUNA 2: Especialidade
        lbl_esp = ctk.CTkLabel(header_frame, text="Especialidade", font=h_font, text_color=h_color, anchor='w')
        # <- MUDE O VALOR AQUI
        lbl_esp.grid(row=0, column=2, sticky='ew', padx=(12, 8))

        # COLUNA 3: Médico
        lbl_med = ctk.CTkLabel(header_frame, text="Médico", font=h_font, text_color=h_color, anchor='w')
        # <- MUDE O VALOR AQUI
        lbl_med.grid(row=0, column=3, sticky='ew', padx=(12, 8))

        # COLUNA 4: Data
        lbl_data = ctk.CTkLabel(header_frame, text="Data", font=h_font, text_color=h_color, anchor='w')
        # <- MUDE O VALOR AQUI
        lbl_data.grid(row=0, column=4, sticky='ew', padx=(12, 8))

        # COLUNA 5: Hora
        lbl_hora = ctk.CTkLabel(header_frame, text="Hora", font=h_font, text_color=h_color, anchor='w')
        # <- MUDE O VALOR AQUI
        lbl_hora.grid(row=0, column=5, sticky='ew', padx=(12, 8))

        # COLUNA 6: Status
        lbl_status = ctk.CTkLabel(header_frame, text="Status", font=h_font, text_color=h_color, anchor='center')
        # <- MUDE O VALOR AQUI: O status foi colocado como 'center' para se alinhar com a cor de fundo do status.
        lbl_status.grid(row=0, column=6, sticky='ew', padx=(12, 12))


        # ==========================================
        # 2. LISTA DE CONSULTAS
        # ==========================================
        list_area = ctk.CTkFrame(
            table_container,
            fg_color='transparent',
        )
        list_area.grid(row=1, column=0, sticky='nsew', padx=0, pady=0)
        list_area.grid_columnconfigure(0, weight=1)

        if not consultas:
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
                text='Tente ajustar os filtros ou recarregar a agenda.',
                text_color=self.colors['text_muted'],
                font=ctk.CTkFont(size=13)
            ).pack()
        else:
            self._render_rows(list_area, consultas)

        if self.paciente_selecionado and self.details_panel:
            self.render_details_panel(self.details_panel)

        self.render_pagination(left, total)
        self.render_details_panel(right)

    def _render_filtros(self, parent, datas, medicos, especialidades):
        filtros_card = ctk.CTkFrame(
            parent,
            fg_color="#f3f6fb",
            corner_radius=18,
            border_width=1,
            border_color="#e2e8f0"
        )
        filtros_card.grid(row=0, column=0, sticky='ew', pady=(0, 12))
        filtros_card.grid_columnconfigure(0, weight=1)

        linha = ctk.CTkFrame(filtros_card, fg_color='transparent')
        linha.pack(fill='x', padx=12, pady=12)

        def filtro(texto, values, var_name):
            frame = ctk.CTkFrame(linha, fg_color="#ffffff", corner_radius=12)

            partes = texto.split(' ', 1)
            icone = partes[0] if partes else ""
            texto_label = partes[1] if len(partes) > 1 else ""

            cores_icones = {
                "📅": "#FF6B6B",
                "🩺": "#4ECDC4",
                "📊": "#FFE66D",
                "🦷": "#95E1D3",
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
                fg_color="white",
                border_color="#4db8ff",
                button_color="#4db8ff",
                button_hover_color="#3399ff",
                corner_radius=8,
                variable=getattr(self, var_name)
            )
            combo.pack(fill='x', padx=10, pady=(6, 10))

            return frame

        filtro_data = filtro("📅 Data", ['Todos'] + [d.strftime('%d/%m/%Y') for d in datas], 'data_var')
        filtro_medico = filtro("🩺 Médico", ['Todos'] + medicos, 'medico_var')
        filtro_status = filtro("📊 Status", ['Todos', 'Agendada', 'Confirmada', 'Realizada', 'Cancelada'], 'status_var')
        filtro_especialidade = filtro("🦷 Especialidade", ['Todos'] + especialidades, 'especialidade_var')

        filtro_data.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        filtro_medico.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        filtro_status.pack(side='left', expand=True, fill='x', padx=5, pady=5)
        filtro_especialidade.pack(side='left', expand=True, fill='x', padx=5, pady=5)

        button_wrap = ctk.CTkFrame(linha, fg_color='transparent', width=120, height=110)
        button_wrap.pack(side='left', padx=10, pady=(30, 5), anchor='center')
        button_wrap.pack_propagate(False)

        botao_limpar = ctk.CTkButton(
            button_wrap,
            text='🗑 Limpar',
            width=120,
            height=32,
            fg_color='#EF4444',
            hover_color='#DC2626',
            text_color='white',
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight='bold'),
            command=self._limpar_filtros
        )
        botao_limpar.pack(fill='x', padx=10, pady=(6, 6))

        botao = ctk.CTkButton(
            button_wrap,
            text='↻ Atualizar',
            width=120,
            height=32,
            fg_color='#4db8ff',
            hover_color='#3399ff',
            corner_radius=10,
            font=ctk.CTkFont(size=12, weight='bold'),
            command=self.refresh_data
        )
        botao.pack(fill='x', padx=10, pady=(0, 10))

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
            
            estilo_status = LOCAL_STATUS_COLORS.get(status_key, {'bg': '#E5E7EB', 'text': '#374151'})

            status_wrap = ctk.CTkFrame(row, fg_color="transparent")
            status_wrap.grid(row=0, column=6, sticky='ew', padx=(padx_left, padx_right), pady=0)

            badge = ctk.CTkFrame(
                status_wrap,
                fg_color=estilo_status['bg'],
                corner_radius=12,
                height=30
            )
            
            # Como alteramos o anchor de status para 'center', essa badge será centralizada na coluna
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
            row.configure(fg_color=self.colors['hover'])

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
        for w in parent.winfo_children():
            w.destroy()

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
                text_color='#EF4444'
            ).pack(pady=20)
            return

        (
            consulta_id, nome, data_hora, status, telefone, email, sexo,
            data_nascimento, cpf, foto, observacoes, medico_nome, especialidade
        ) = consulta

        status_key = (status or '').lower()
        estilo_status = LOCAL_STATUS_COLORS.get(status_key, {'bg': '#E5E7EB', 'text': '#374151'})

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
            fg_color='#F8FAFC',
            border_width=1,
            border_color=self.colors['border'],
            corner_radius=12
        )
        obs.pack(fill='both', expand=True)
        obs.insert('1.0', observacoes or 'Sem observações registradas.')
        obs.configure(state='disabled')

    def _detail_item(self, parent, text):
        row = ctk.CTkFrame(parent, fg_color='#F8FAFC', corner_radius=12)
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
            row.configure(fg_color=self.colors['selected'] if cid == consulta_id else '#FFFFFF')

        if self.details_panel:
            self.render_details_panel(self.details_panel)

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