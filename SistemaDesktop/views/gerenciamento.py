import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from .base import BaseScreen
from .theme import COLORS, INNER_CARD_BORDER, INNER_CARD_RADIUS
from config.database import get_connection
from controllers.consulta_controller import ConsultaController
from controllers.medico_controller import MedicoController
from models.auth import verificar_senha
from services.medico_service import MedicoService


class MedicosDisponibilidadeScreen(ctk.CTkFrame):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, fg_color="transparent")

        self.clinica_id = clinica_id
        self.selected_medico = None
        self.selected_date = datetime.now().date()
        self.selected_dates = set()
        self.last_selected_date = None
        self.selected_slots = set()
        self.last_selected_slot = None
        self.saved_slots_by_date = {}
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

        self.medicos = []
        self.slot_buttons = {}

        print("========== GERENCIAMENTO ===========")
        print(f"Instância da tela Gerenciamento criada id(self): {id(self)}")
        self._load_medicos()
        self._build_ui()

    def _load_medicos(self):
        print("load_medicos_async() iniciado")
        self.medicos = []
        self.total_medicos_filtrados = 0
        self.pagina_atual = 0

        if not self.clinica_id:
            print("Nenhuma clínica definida, não buscando médicos.")
            return

        print(f"Buscando médicos para clinica_id={self.clinica_id}...")
        medicos_bd = ConsultaController.listar_medicos_por_clinica(self.clinica_id)
        print(f"Quantidade encontrada: {len(medicos_bd)}")
        self.medicos = [
            {
                "id": medico[0],
                "nome": medico[1] or "",
                "email": medico[2] or "",
                "especialidade": medico[3] or "Geral",
                "status": "Ativo"
            }
            for medico in medicos_bd
        ]

    def refresh(self):
        print("Atualizando lista de médicos no Gerenciamento...")
        self._load_medicos()
        print("Chamando _render_medicos()")
        self._render_medicos()

    

    def _build_ui(self):
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)

        self._build_left_panel(main_container)
        self._build_right_panel(main_container)

    def _build_left_panel(self, parent):
        left_card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=10)
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
            row.grid_columnconfigure(1, weight=1, minsize=200)
            row.grid_columnconfigure(2, weight=1, minsize=220)
            row.grid_columnconfigure(3, weight=2, minsize=280)
            row.grid_rowconfigure(0, weight=1)
            
            avatar_img = self._create_avatar(medico["nome"], 32)
            avatar = ctk.CTkLabel(row, image=avatar_img, text="")
            avatar.image = avatar_img
            avatar.grid(row=0, column=0, sticky="w", padx=(12, 8), pady=14)
            
            nome = ctk.CTkLabel(
                row,
                text=MedicoService.formatar_nome_visual(medico["nome"]),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text"],
                anchor="w",
                justify="left"
            )
            nome.grid(row=0, column=1, sticky="ew", padx=(0, 12))
            
            email = ctk.CTkLabel(
                row,
                text=medico["email"],
                font=ctk.CTkFont(size=13),
                text_color=self.colors["muted"],
                anchor="w",
                justify="left"
            )
            email.grid(row=0, column=2, sticky="ew", padx=(0, 12))
            
            especialidade = ctk.CTkLabel(
                row,
                text=medico["especialidade"],
                font=ctk.CTkFont(size=13),
                text_color=self.colors["muted"],
                anchor="w",
                justify="left"
            )
            especialidade.grid(row=0, column=3, sticky="ew", padx=(0, 12))

            excluir = ctk.CTkButton(
                row,
                text="X",
                width=24,
                height=24,
                fg_color="transparent",
                hover_color=self.colors["primary_soft"],
                text_color=self.colors["primary"],
                corner_radius=12,
                border_width=0,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda m=medico: self._confirmar_exclusao_medico(m)
            )
            excluir.place(relx=1.0, rely=0.0, anchor="ne", x=2, y=-5)
            
            for widget in [row, avatar, nome, email, especialidade]:
                widget.bind("<Button-1>", lambda e, m=medico: self._select_medico(m))
                widget.bind("<Enter>", lambda e, r=row, s=is_selected: self._hover_row(r, s, True))
                widget.bind("<Leave>", lambda e, r=row, s=is_selected: self._hover_row(r, s, False))

    def _confirmar_exclusao_medico(self, medico):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar exclusão")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        mensagem = ctk.CTkLabel(
            dialog,
            text=f"Deseja excluir o médico:\n'{medico['nome']}'?",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"],
            justify="center"
        )
        mensagem.pack(padx=28, pady=(24, 18))

        botoes = ctk.CTkFrame(dialog, fg_color="transparent")
        botoes.pack(pady=(0, 20))

        ctk.CTkButton(
            botoes,
            text="Sim",
            width=80,
            height=32,
            command=lambda: self._abrir_modal_senha_exclusao(medico, dialog)
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            botoes,
            text="Não",
            width=80,
            height=32,
            fg_color=self.colors["card_soft"],
            text_color=self.colors["text"],
            hover_color=self.colors["hover"],
            command=dialog.destroy
        ).pack(side="left", padx=6)

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.update_idletasks()
        janela_principal = self.winfo_toplevel()
        pos_x = janela_principal.winfo_rootx() + (janela_principal.winfo_width() - dialog.winfo_width()) // 2
        pos_y = janela_principal.winfo_rooty() + (janela_principal.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{pos_x}+{pos_y}")

    def _abrir_modal_senha_exclusao(self, medico, confirm_dialog):
        confirm_dialog.destroy()
        if hasattr(self, "_password_dialog") and self._password_dialog is not None:
            try:
                if self._password_dialog.winfo_exists():
                    self._password_dialog.focus_set()
                    return
            except Exception:
                pass

        dialog = ctk.CTkToplevel(self)
        self._password_dialog = dialog
        dialog.title("Confirmar senha")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.geometry("360x260")

        ctk.CTkLabel(
            dialog,
            text="Confirme sua senha",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text"]
        ).pack(padx=40, pady=(32, 12))

        senha_entry = ctk.CTkEntry(dialog, width=260, show="*")
        senha_entry.pack(padx=40, pady=(0, 14))

        erro_label = ctk.CTkLabel(dialog, text="", text_color=self.colors["danger"])
        erro_label.pack(padx=40, pady=(0, 12))

        botoes = ctk.CTkFrame(dialog, fg_color="transparent")
        botoes.pack(pady=(0, 28))

        def cancelar():
            self._password_dialog = None
            dialog.destroy()

        def confirmar():
            senha = senha_entry.get()
            if not senha:
                erro_label.configure(text="Informe a senha.")
                return

            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT senha FROM odontoPro_clinica WHERE id = %s", (self.clinica_id,))
                row = cursor.fetchone()
                senha_valida = verificar_senha(senha, row[0]) if row and row[0] else False
            except Exception:
                senha_valida = False
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

            if not senha_valida:
                erro_label.configure(text="Senha incorreta.")
                senha_entry.delete(0, "end")
                senha_entry.focus_set()
                return

            self._password_dialog = None
            self._excluir_medico_confirmado(medico, dialog)

        ctk.CTkButton(botoes, text="Confirmar", width=90, height=32, command=confirmar).pack(side="left", padx=6)
        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=90,
            height=32,
            fg_color=self.colors["card_soft"],
            text_color=self.colors["text"],
            hover_color=self.colors["hover"],
            command=cancelar
        ).pack(side="left", padx=6)

        dialog.protocol("WM_DELETE_WINDOW", cancelar)
        dialog.bind("<Return>", lambda event: confirmar())
        dialog.update_idletasks()
        janela_principal = self.winfo_toplevel()
        largura = 360
        altura = 260
        moldura_x = dialog.winfo_rootx() - dialog.winfo_x()
        moldura_y = dialog.winfo_rooty() - dialog.winfo_y()
        pos_x = janela_principal.winfo_rootx() + (janela_principal.winfo_width() - largura) // 2 - moldura_x
        pos_y = janela_principal.winfo_rooty() + (janela_principal.winfo_height() - altura) // 2 - moldura_y
        dialog.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        senha_entry.focus_set()

    def _excluir_medico_confirmado(self, medico, dialog):
        resultado = MedicoController.desassociar_medico(medico["id"], self.clinica_id)
        dialog.destroy()

        if not resultado.get("sucesso"):
            messagebox.showerror("Erro", resultado.get("mensagem", "Não foi possível remover o médico da clínica."))
            return

        if self.selected_medico and self.selected_medico["id"] == medico["id"]:
            self.selected_medico = None
            self.right_subtitle.configure(text="Selecione um médico para configurar a agenda.")
        self.refresh()

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
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=10)
        self.right_card.grid_rowconfigure(1, weight=1)
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

        self.right_scroll = ctk.CTkScrollableFrame(
            self.right_card,
            fg_color=self.colors["card"],
            corner_radius=0,
            border_width=0
        )
        self.right_scroll.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 0))
        self.right_scroll.grid_columnconfigure(0, weight=1)

        self.calendar_card = ctk.CTkFrame(
            self.right_scroll,
            fg_color=self.colors["card_soft"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.calendar_card.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 16))
        self._build_calendar()

        info_card = ctk.CTkFrame(
            self.right_scroll,
            fg_color=self.colors["primary_soft"],
            corner_radius=12,
            border_width=0
        )
        info_card.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
        
        self.date_info_label = ctk.CTkLabel(
            info_card,
            text=self._format_selected_date(),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["primary"] if self._is_dark_theme() else self.colors["primary_dark"]
        )
        self.date_info_label.pack(padx=16, pady=12, anchor="w")

        slots_container = ctk.CTkFrame(self.right_scroll, fg_color="transparent")
        slots_container.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 20))
        slots_container.grid_rowconfigure(0, weight=0)
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
        self.slots_grid.grid_rowconfigure(0, weight=1)
        self.slots_grid.grid_columnconfigure(0, weight=1)
        
        for i in range(4):
            self.slots_grid.grid_columnconfigure(i, weight=1)
        
        self._build_time_slots()

        footer = ctk.CTkFrame(self.right_scroll, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 28))
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
            is_past = current_date < datetime.now().date()
            is_selected = current_date in self.selected_dates
            has_availability = current_date in self.saved_slots_by_date
            is_sunday = current_date.weekday() == 6
            
            btn = ctk.CTkButton(
                days_frame,
                text=str(day_num),
                width=40,
                height=36,
                corner_radius=10,
                fg_color=self.colors["card_soft"] if is_past else self._get_date_button_color(is_selected, is_today, is_sunday),
                text_color=self.colors["muted"] if is_past else self._get_date_text_color(is_selected, is_sunday),
                border_width=1,
                border_color=self.colors["primary"] if is_selected else self.colors["success"] if has_availability else self.colors["border"],
                hover_color=self.colors["primary_dark"] if not is_sunday else self.colors["card_soft"],
                font=ctk.CTkFont(size=13),
                state="disabled" if is_sunday and not is_past else "normal"
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            
            if not is_sunday or is_past:
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
                hover_color=self.colors["primary_dark"],
                font=ctk.CTkFont(size=13)
            )
            btn.grid(row=row, column=col, padx=6, pady=6, sticky="ew")
            btn.bind("<Button-1>", lambda e, h=horario: self._on_slot_clicked(e, h))
            
            self.slot_buttons[horario] = btn

    def _on_date_clicked(self, event, selected_date):
        shift_pressed = (event.state & 0x1) != 0
        has_availability = selected_date in self.saved_slots_by_date

        if selected_date < datetime.now().date():
            self.selected_dates.clear()
            self.last_selected_date = None
        elif has_availability:
            self.selected_dates = {selected_date}
            self.last_selected_date = None
        elif any(
            date in self.saved_slots_by_date
            for date in self.selected_dates
        ):
            self.selected_dates.clear()
            self.last_selected_date = None

            self.selected_dates.add(selected_date)
        elif shift_pressed and self.last_selected_date:
            self._toggle_date_range(self.last_selected_date, selected_date)
        else:
            if selected_date in self.selected_dates:
                self.selected_dates.remove(selected_date)
            else:
                self.selected_dates.add(selected_date)
        
        self.last_selected_date = None if has_availability else selected_date
        self.selected_date = selected_date
        self.selected_slots = set(self.saved_slots_by_date.get(selected_date, [])) if has_availability else set()
        self.last_selected_slot = None
        self._update_slots_display()
        self._update_calendar_display()
        self._update_date_info()

    def _toggle_date_range(self, start_date, end_date):
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        
        interval_dates = set()
        current = start_date
        while current <= end_date:
            if current.weekday() != 6 and current not in self.saved_slots_by_date:
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
            is_past = date < datetime.now().date()
            has_availability = date in self.saved_slots_by_date
            is_sunday = date.weekday() == 6
            
            btn.configure(
                fg_color=self.colors["card_soft"] if is_past else self._get_date_button_color(is_selected, is_today, is_sunday),
                text_color=self.colors["muted"] if is_past else self._get_date_text_color(is_selected, is_sunday),
                border_color=self.colors["primary"] if is_selected else self.colors["success"] if has_availability else self.colors["border"],
                state="disabled" if is_sunday and not is_past else "normal"
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
        horarios_list = [
            "08:00", "08:30", "09:00", "09:30",
            "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30",
            "14:00", "14:30", "15:00", "15:30",
            "16:00", "16:30", "17:00", "17:30"
        ]
        
        if self.last_selected_slot is None:
            if self.selected_slots:
                self.selected_slots.clear()
            self.selected_slots.add(horario)
            self.last_selected_slot = horario
        else:
            inicio_idx = horarios_list.index(self.last_selected_slot)
            fim_idx = horarios_list.index(horario)
            if inicio_idx > fim_idx:
                inicio_idx, fim_idx = fim_idx, inicio_idx
            self.selected_slots = set(horarios_list[inicio_idx:fim_idx + 1])
            self.last_selected_slot = None

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
        self.selected_dates.clear()
        self.last_selected_date = None
        self.selected_slots.clear()
        self.last_selected_slot = None
        self.saved_slots_by_date = ConsultaController.carregar_disponibilidade_medico_por_data(
            medico["id"],
        )
        self.right_subtitle.configure(
            text=f"Configurando agenda de {medico['nome']}."
        )
        self._build_calendar()
        self._update_slots_display()
        self._render_medicos()

    def _save_disponibilidade(self):
        if not self.selected_medico:
            messagebox.showwarning("Aviso", "Selecione um médico primeiro.")
            return
        
        datas_para_salvar = {
            data for data in self.selected_dates
            if data >= datetime.now().date()
        }

        if not datas_para_salvar:
            messagebox.showwarning("Aviso", "Selecione pelo menos uma data.")
            return
        
        if len(self.selected_slots) < 2:
            messagebox.showwarning("Aviso", "Selecione pelo menos dois horários para definir o período de disponibilidade.")
            return

        disponibilidade_por_data = {}
        for data in datas_para_salvar:
            disponibilidade_por_data[data] = set(self.selected_slots)

        disponibilidade_por_data = {
            data: sorted(slots)
            for data, slots in disponibilidade_por_data.items()
        }

        resultado = ConsultaController.salvar_disponibilidade_medico(
            self.selected_medico["id"],
            disponibilidade_por_data,
            clinica_id=self.clinica_id
        )

        if resultado.get('sucesso'):
            for data in datas_para_salvar:
                self.saved_slots_by_date[data] = sorted(self.selected_slots)

            horarios = ", ".join(sorted(self.selected_slots))
            datas_sorted = sorted(list(datas_para_salvar))
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
        else:
            messagebox.showerror(
                "Erro ao salvar disponibilidade",
                resultado.get('mensagem', 'Não foi possível salvar a disponibilidade.')
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
        bg_color = COLORS["primary"]
        
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
        self.clinica_id = clinica_id

        self.screen = MedicosDisponibilidadeScreen(self.content_card, clinica_id=clinica_id)
        self.screen.pack(fill="both", expand=True, padx=20, pady=20)

    def refresh(self):
        print("Gerenciamento.refresh() chamado")
        if hasattr(self, 'screen') and self.screen:
            print(f"Gerenciamento.refresh: instância interna screen id(self.screen)={id(self.screen)}")
            self.screen.refresh()
            return

        print("Gerenciamento.refresh: nenhuma tela interna de médicos encontrada, recriando instância")
        self.screen = MedicosDisponibilidadeScreen(self.content_card, clinica_id=self.clinica_id)
        self.screen.pack(fill="both", expand=True)
