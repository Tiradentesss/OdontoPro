import threading
import os
from datetime import date

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from .base import BaseScreen
from models.data import LIMITE_CONSULTAS
from controllers.consulta_controller import ConsultaController

LOCAL_STATUS_COLORS = {
    'realizada': {'bg': '#D1FAE5', 'text': '#065F46'},
    'agendada': {'bg': '#FEF3C7', 'text': '#92400E'},
    'cancelada': {'bg': '#FEE2E2', 'text': '#991B1B'},
    'confirmada': {'bg': '#DBEAFE', 'text': '#1D4ED8'},
}


class Agenda(BaseScreen):
    def __init__(self, parent, clinica_id):
        super().__init__(parent, 'Agenda')

        self.clinica_id = clinica_id

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
            'bg_card': '#FFFFFF',
            'bg_main': '#F3F4F6',
            'text_primary': '#111827',
            'text_secondary': '#6B7280',
            'primary': '#0EA5E9',
            'hover': '#F0F9FF',
            'selected': '#EFF6FF',
            'border': '#E5E7EB',
            'avatar_colors': ['#F59E0B', '#EF4444', '#EC4899', '#10B981', '#3B82F6']
        }

        self.col_widths = {
            'avatar': 52,
            'nome': 180,
            'especialidade': 150,
            'medico': 150,
            'data': 100,
            'hora': 80,
            'status': 120,
        }

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

    def aplicar_filtros(self, *_):
        self.filtro_data = None if self.data_var.get() in ['Todos', 'Data'] else self.data_var.get()
        self.filtro_medico = None if self.medico_var.get() in ['Todos', 'Médico'] else self.medico_var.get()
        self.filtro_status = None if self.status_var.get() in ['Todos', 'Status'] else self.status_var.get()
        self.filtro_especialidade = None if self.especialidade_var.get() in ['Todos', 'Especialidade'] else self.especialidade_var.get()

        self.pagina_atual = 0
        # mantemos paciente_selecionado se ainda fizer sentido, para não perder o detalhe visível
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
        # manter a consulta selecionada para exibir detalhes ao atualizar a lista
        # self.paciente_selecionado = None
        for w in self.content_card.winfo_children():
            w.destroy()

        loading_lbl = ctk.CTkLabel(
            self.content_card,
            text='Carregando consultas...',
            font=ctk.CTkFont(size=16, weight='bold'),
            text_color=self.colors['text_secondary']
        )
        loading_lbl.pack(expand=True)

        threading.Thread(target=self._load_data_thread, daemon=True).start()

    def _load_data_thread(self):
        data_sql = self._get_data_sql()

        try:
            consultas = ConsultaController.listar_por_clinica(
                self.clinica_id,
                pagina=self.pagina_atual,
                limite=LIMITE_CONSULTAS,
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

        ctk.CTkLabel(
            self.content_card,
            text=f'Erro ao carregar agenda: {message}',
            text_color='#EF4444',
            font=ctk.CTkFont(size=14, weight='bold')
        ).pack(expand=True, padx=20, pady=20)

    def _render_after_load(self, consultas, total, datas, medicos, especialidades, snapshot):
        try:
            self._loading = False
            self.current_snapshot = snapshot

            for w in self.content_card.winfo_children():
                w.destroy()

            self.content_card.configure(fg_color='transparent')
        except Exception as e:
            print(f"[Agenda] _render_after_load error: {e}")
            self._render_error(f"Falha ao renderizar agenda: {e}")
            return

        # Conteúdo em duas colunas
        panel_main = ctk.CTkFrame(self.content_card, fg_color='transparent')
        panel_main.pack(fill='both', expand=True)
        panel_main.grid_columnconfigure(0, weight=2)
        panel_main.grid_columnconfigure(1, weight=1)
        panel_main.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(panel_main, fg_color='white', corner_radius=18, border_width=1, border_color=self.colors['border'])
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 12), pady=10)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(3, weight=1)

        right = ctk.CTkFrame(panel_main, fg_color='white', corner_radius=18, border_width=1, border_color=self.colors['border'])
        right.grid(row=0, column=1, sticky='nsew', pady=10)
        right.grid_columnconfigure(0, weight=1)
        self.details_panel = right

        # Filtros (apenas botão/option menu estilizado; container transparente)
        filtros = ctk.CTkFrame(left, fg_color='transparent', corner_radius=0, border_width=0)
        filtros.grid(row=0, column=0, sticky='ew', padx=15, pady=(15, 10))
        filtros.grid_columnconfigure(7, weight=1)

        ctk.CTkLabel(filtros, text='Filtros', font=ctk.CTkFont(size=15, weight='bold'), text_color=self.colors['text_primary']).grid(row=0, column=0, padx=(0, 10))

        option_kwargs = {
            'fg_color': '#FFFFFF',
            'button_color': self.colors['primary'],
            'button_hover_color': '#0b86af',
            'text_color': self.colors['primary'],
            'corner_radius': 8,
            'width': 150
        }

        self.data_option = ctk.CTkOptionMenu(filtros, values=['Todos'] + [d.strftime('%d/%m/%Y') for d in datas], variable=self.data_var, **option_kwargs)
        self.data_option.grid(row=0, column=1, padx=4)

        self.medico_option = ctk.CTkOptionMenu(filtros, values=['Todos'] + medicos, variable=self.medico_var, **option_kwargs)
        self.medico_option.grid(row=0, column=2, padx=4)

        self.status_option = ctk.CTkOptionMenu(filtros, values=['Todos', 'Agendada', 'Confirmada', 'Realizada', 'Cancelada'], variable=self.status_var, **option_kwargs)
        self.status_option.grid(row=0, column=3, padx=4)

        self.especialidade_option = ctk.CTkOptionMenu(filtros, values=['Todos'] + especialidades, variable=self.especialidade_var, **option_kwargs)
        self.especialidade_option.grid(row=0, column=4, padx=4)

        btn_reload = ctk.CTkButton(filtros, text='↻ Recarregar', command=self.render, width=140, corner_radius=8, fg_color=self.colors['primary'], text_color='#FFFFFF')
        btn_reload.grid(row=0, column=5, padx=(14, 0))

        ctk.CTkLabel(left, text=f'Total de consultas: {total}', font=ctk.CTkFont(size=13, weight='bold'), text_color=self.colors['text_secondary']).grid(row=1, column=0, sticky='w', padx=15, pady=(0, 8))

        # Cabeçalho
        header = ctk.CTkFrame(left, fg_color='#F9FAFB', corner_radius=8)
        header.grid(row=2, column=0, sticky='ew', padx=15, pady=(0, 8))
        cols = [('Nome', 1), ('Especialidade', 1), ('Médico', 1), ('Data', 0), ('Hora', 0), ('Status', 0)]
        for i, (title, weight) in enumerate(cols):
            header.grid_columnconfigure(i, weight=weight, minsize=[self.col_widths['nome'], self.col_widths['especialidade'], self.col_widths['medico'], self.col_widths['data'], self.col_widths['hora'], self.col_widths['status']][i])
            ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=13, weight='bold'), text_color=self.colors['text_secondary']).grid(row=0, column=i, padx=8, pady=8, sticky='w')

        content_scroll = ctk.CTkScrollableFrame(left, fg_color='transparent')
        content_scroll.grid(row=3, column=0, sticky='nsew', padx=15, pady=(0, 10))
        content_scroll.grid_columnconfigure(0, weight=1)

        if not consultas:
            ctk.CTkLabel(content_scroll, text='Nenhuma consulta encontrada.', text_color=self.colors['text_secondary']).pack(pady=40)
        else:
            self._render_rows(content_scroll, consultas)

        # Exibir detalhes da seleção anterior (se houver)
        if self.paciente_selecionado and self.details_panel:
            self.render_details_panel(self.details_panel)

        # Paginação
        self.render_pagination(left, total)

        # Detalhes lateral
        self.render_details_panel(right)

    def _render_rows(self, container, consultas):
        self.image_cache = []
        self.row_widgets = {}

        for idx, item in enumerate(consultas):
            (consulta_id, nome, data_hora, status, telefone, email, sexo, data_nascimento, cpf, foto, observacoes, medico_nome, especialidade) = item
            status_key = (status or '').lower()
            row_color = self.colors['selected'] if self.paciente_selecionado == consulta_id else 'transparent'

            row = ctk.CTkFrame(container, fg_color=row_color, corner_radius=8, height=42)
            row.grid(row=idx, column=0, sticky='ew', pady=2)
            row.grid_propagate(False)
            row.grid_rowconfigure(0, weight=1)
            row.grid_columnconfigure(0, minsize=38, weight=0)
            row.grid_columnconfigure(1, minsize=self.col_widths['nome'], weight=1)
            row.grid_columnconfigure(2, minsize=self.col_widths['especialidade'], weight=1)
            row.grid_columnconfigure(3, minsize=self.col_widths['medico'], weight=1)
            row.grid_columnconfigure(4, minsize=self.col_widths['data'], weight=0)
            row.grid_columnconfigure(5, minsize=self.col_widths['hora'], weight=0)
            row.grid_columnconfigure(6, minsize=self.col_widths['status'], weight=0)

            self.row_widgets[consulta_id] = row

            row.bind('<Button-1>', lambda e, cid=consulta_id: self.selecionar_paciente(cid))
            row.bind('<Enter>', lambda e, r=row: r.configure(fg_color=self.colors['hover']))
            row.bind('<Leave>', lambda e, r=row, cid=consulta_id: r.configure(fg_color=self.colors['selected'] if self.paciente_selecionado == cid else 'transparent'))

            avatar = ctk.CTkLabel(row, width=28, height=28, corner_radius=14, fg_color='transparent')
            avatar.grid(row=0, column=0, padx=6)

            avatar_img = self._create_avatar_image(nome, foto, 28)
            avatar.configure(image=avatar_img)
            avatar.image = avatar_img
            self.image_cache.append(avatar_img)

            ctk.CTkLabel(row, text=(nome or 'Não informado'), font=ctk.CTkFont(size=12, weight='bold'), text_color=self.colors['text_primary']).grid(row=0, column=1, sticky='w', padx=4)
            ctk.CTkLabel(row, text=(especialidade or '-'), font=ctk.CTkFont(size=12), text_color=self.colors['text_secondary']).grid(row=0, column=2, sticky='w', padx=4)
            ctk.CTkLabel(row, text=(medico_nome or '-'), font=ctk.CTkFont(size=12), text_color=self.colors['text_secondary']).grid(row=0, column=3, sticky='w', padx=4)
            ctk.CTkLabel(row, text=data_hora.strftime('%d/%m/%Y') if data_hora else '-', font=ctk.CTkFont(size=12), text_color=self.colors['text_secondary']).grid(row=0, column=4, sticky='w', padx=4)
            ctk.CTkLabel(row, text=data_hora.strftime('%H:%M') if data_hora else '-', font=ctk.CTkFont(size=12), text_color=self.colors['text_secondary']).grid(row=0, column=5, sticky='w', padx=4)

            estilo_status = LOCAL_STATUS_COLORS.get(status_key, {'bg': '#E5E7EB', 'text': '#374151'})
            badge = ctk.CTkFrame(row, fg_color=estilo_status['bg'], corner_radius=10)
            badge.grid(row=0, column=6, sticky='w', padx=6, pady=6)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=status or '-', text_color=estilo_status['text'], font=ctk.CTkFont(size=10, weight='bold')).place(relx=0.5, rely=0.5, anchor='center')

    def _create_avatar_image(self, nome, foto, size):
        if foto:
            try:
                root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                path = os.path.join(root, 'media', foto)
                if os.path.exists(path):
                    img = Image.open(path).convert('RGB')
                    min_d = min(img.size)
                    img = img.crop(((img.width - min_d)//2, (img.height - min_d)//2, (img.width + min_d)//2, (img.height + min_d)//2))
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
        img = Image.new('RGBA', (size, size), color)
        draw = ImageDraw.Draw(img)
        try:
            fonte = ImageFont.truetype('arial.ttf', int(size * 0.55))
        except Exception:
            fonte = ImageFont.load_default()
        draw.text((size/2, size/2), inicial, fill='white', font=fonte, anchor='mm')
        return ctk.CTkImage(light_image=img, size=(size, size))

    def render_pagination(self, parent, total_items):
        pag_frame = ctk.CTkFrame(parent, fg_color='transparent')
        pag_frame.grid(row=4, column=0, sticky='e', padx=16, pady=(0, 12))

        paginas = max(1, (total_items + LIMITE_CONSULTAS - 1)//LIMITE_CONSULTAS)
        for i in range(paginas):
            ctk.CTkButton(
                pag_frame,
                text=str(i+1),
                width=34,
                height=34,
                corner_radius=8,
                fg_color=self.colors['primary'] if i == self.pagina_atual else 'transparent',
                border_width=0 if i == self.pagina_atual else 1,
                border_color=self.colors['border'],
                text_color='white' if i == self.pagina_atual else self.colors['text_secondary'],
                command=lambda p=i: self.mudar_pagina(p)
            ).pack(side='left', padx=2)

    def render_details_panel(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        if not self.paciente_selecionado:
            ctk.CTkLabel(parent, text='Selecione uma consulta para ver detalhes.', text_color=self.colors['text_secondary'], font=ctk.CTkFont(size=13)).place(relx=0.5, rely=0.5, anchor='center')
            return

        consulta = ConsultaController.buscar_por_id(self.paciente_selecionado)
        if not consulta:
            ctk.CTkLabel(parent, text='Consulta não encontrada.', text_color='#EF4444').pack(pady=20)
            return

        (consulta_id, nome, data_hora, status, telefone, email, sexo, data_nascimento, cpf, foto, observacoes, medico_nome, especialidade) = consulta

        ctk.CTkLabel(parent, text=nome or 'Paciente', font=ctk.CTkFont(size=18, weight='bold'), text_color=self.colors['text_primary']).pack(anchor='w', padx=16, pady=(16, 8))
        ctk.CTkLabel(parent, text=f'Status: {status or "-"}', font=ctk.CTkFont(size=14, weight='bold'), text_color=self.colors['text_primary']).pack(anchor='w', padx=16)
        ctk.CTkLabel(parent, text=f'Médico: {medico_nome or "-"}', font=ctk.CTkFont(size=14), text_color=self.colors['text_secondary']).pack(anchor='w', padx=16, pady=(4, 0))
        ctk.CTkLabel(parent, text=f'Especialidade: {especialidade or "-"}', font=ctk.CTkFont(size=14), text_color=self.colors['text_secondary']).pack(anchor='w', padx=16)
        ctk.CTkLabel(parent, text=f'Data e Hora: {data_hora.strftime("%d/%m/%Y %H:%M") if data_hora else "-"}', font=ctk.CTkFont(size=14), text_color=self.colors['text_secondary']).pack(anchor='w', padx=16)

        ctk.CTkLabel(parent, text=f'Telefone: {telefone or "-"}', font=ctk.CTkFont(size=13), text_color=self.colors['text_secondary']).pack(anchor='w', padx=16, pady=(8, 0))
        ctk.CTkLabel(parent, text=f'E-mail: {email or "-"}', font=ctk.CTkFont(size=13), text_color=self.colors['text_secondary']).pack(anchor='w', padx=16)
        ctk.CTkLabel(parent, text=f'Sexo: {sexo or "-"} | Idade: {self.calcular_idade(data_nascimento)} | CPF: {cpf or "-"}', font=ctk.CTkFont(size=13), text_color=self.colors['text_secondary']).pack(anchor='w', padx=16, pady=(0, 10))

        ctk.CTkLabel(parent, text='Observações', font=ctk.CTkFont(size=15, weight='bold'), text_color=self.colors['text_primary']).pack(anchor='w', padx=16, pady=(10, 4))
        obs = ctk.CTkTextbox(parent, height=120, fg_color='#F8FAFC', border_width=1, border_color=self.colors['border'])
        obs.pack(fill='x', padx=16, pady=(0, 18))
        obs.insert('1.0', observacoes or '')
        obs.configure(state='disabled')

    def selecionar_paciente(self, consulta_id):
        self.paciente_selecionado = consulta_id
        # marca a linha selecionada sem recarregar toda a tela
        for cid, row in self.row_widgets.items():
            row.configure(fg_color=self.colors['selected'] if cid == consulta_id else 'transparent')

        # atualiza apenas painel de detalhes
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
