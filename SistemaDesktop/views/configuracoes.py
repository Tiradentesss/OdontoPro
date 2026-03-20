import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from .base import BaseScreen
from .theme import font, ICON_SIZE
import os

class ModernInput(ctk.CTkFrame):
    """Componente de input padronizado com ícone e validação"""
    def __init__(self, parent, label="", placeholder="", icon=None, required=False, **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        self.required = required
        
        # Label com indicador de obrigatório
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 3)) # ALINHAMENTO: pady=(0, 3) idêntico ao CODE 1
        
        lbl = ctk.CTkLabel(
            label_frame,
            text=label,
            font=("Poppins", 14), # ALINHAMENTO: Fonte 14 idêntica ao CODE 1
            text_color="#4B5563"
        )
        lbl.pack(side="left")
        
        if required:
            required_lbl = ctk.CTkLabel(
                label_frame,
                text="*",
                font=("Poppins", 14, "bold"),
                text_color="#EF4444"
            )
            required_lbl.pack(side="left", padx=(2, 0))
        
        # Container do input com ícone
        input_container = ctk.CTkFrame(self, fg_color="transparent")
        input_container.pack(fill="x")
        
        if icon:
            icon_lbl = ctk.CTkLabel(
                input_container,
                text=icon,
                font=("Poppins", 14),
                width=30
            )
            icon_lbl.pack(side="left", padx=(0, 5))
        
        self.entry = ctk.CTkEntry(
            input_container,
            placeholder_text=placeholder,
            height=44,           # ALINHAMENTO CRÍTICO: Altura travada em 44 (Igual CODE 1)
            corner_radius=5,     # ALINHAMENTO CRÍTICO: Raio travado em 5 (Igual CODE 1)
            border_width=1,
            border_color="#E5E7EB",
            fg_color="#F9FAFB",
            text_color="#111827",
            placeholder_text_color="#9CA3AF",
            font=("Poppins", 14),
            **kwargs
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        self.entry.bind("<FocusOut>", self._validate)
    
    def _validate(self, event=None):
        if self.required and not self.entry.get().strip():
            self.entry.configure(border_color="#EF4444") 
            return False
        else:
            self.entry.configure(border_color="#E5E7EB")
            return True
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

class Configuracoes(BaseScreen):
    def __init__(self, parent, tipo_usuario="clinica", clinica_id=None, usuario_id=None):
        super().__init__(parent, "Configurações")
        
        # Tipo de usuário: "clinica", "gerenciamento", "dentista", etc.
        self.tipo_usuario = tipo_usuario
        # ID da clínica (necessário para carregar/salvar dados quando tipo_usuario=="clinica")
        self.clinica_id = clinica_id
        # ID do usuário logado (necessário para carregar dados de perfil)
        self.usuario_id = usuario_id

        self.colors = {
            "bg_main": "#FFFFFF",
            "bg_card": "#FFFFFF",
            "text_primary": "#111827",
            "text_secondary": "#6B7280",
            "text_muted": "#9CA3AF",
            "accent": "#0EA5E9",
            "accent_hover": "#0284C7",
            "accent_light": "#EFF6FF",
            "border": "#E5E7EB",
            "border_focus": "#0EA5E9",
            "success": "#10B981",
            "error": "#EF4444",
            "input_bg": "#F9FAFB",
            "tab_active": "#FFFFFF",
            "tab_inactive": "transparent"
        }

        self.current_tab = "Perfil"
        self.tab_buttons = {}
        self.images = {}
        self.loading_states = {}
        self.clinic_entries = {}  # Inicializar vazio, preenchido apenas se tipo_usuario=="clinica"
        self.profile_entries = {}  # Inicializar vazio, preenchido apenas se tipo_usuario="gerenciamento" ou "dentista"

        self.setup_ui()

    def setup_ui(self):
        # =============================
        # 1. BARRA DE ABAS (TOPO)
        # =============================
        self.tab_bar = ctk.CTkFrame(self.content_card, fg_color="transparent", height=44)
        self.tab_bar.pack(fill="x", padx=125, pady=(9, 0), anchor="nw") # Exatamente igual ao CODE 1

        self._build_tabs()

        # =============================
        # 2. ÁREA DE CONTEÚDO (CORPO BRANCO)
        # =============================
        self.container_outer = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent",
            corner_radius=20
        )
        # CORREÇÃO CRÍTICA: padx alterado de 98 para 80. 
        # Isso impede que o fundo branco "pule" ou mude de tamanho ao trocar de tela.
        self.container_outer.pack(fill="both", expand=True, padx=100, pady=(6, 20))

        self.container_conteudo = ctk.CTkFrame(
            self.container_outer,
            fg_color=self.colors["bg_card"],
            corner_radius=12
        )
        self.container_conteudo.pack(fill="both", expand=True, padx=2, pady=(2, 1))

        self.content_area = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True) 

        self._build_footer(self.container_conteudo)

        self.switch_tab(self.current_tab)

    def _build_tabs(self):
        # Todas as abas disponíveis
        todas_abas = [
            {"name": "Perfil", "text": "👤   Perfil", "tipo_acesso": ["gerenciamento", "dentista"]},
            {"name": "Segurança", "text": "🔒   Segurança", "tipo_acesso": ["clinica", "gerenciamento", "dentista"]},
            {"name": "Minha Clínica", "text": "🏥   Minha Clínica", "tipo_acesso": ["clinica"]}
        ]
        
        # Filtrar abas baseado no tipo de usuário
        tabs_disponiveis = [tab for tab in todas_abas if self.tipo_usuario in tab["tipo_acesso"]]
        
        # Definir primeira aba disponível como padrão
        if tabs_disponiveis:
            self.current_tab = tabs_disponiveis[0]["name"]
        
        for i, tab in enumerate(tabs_disponiveis):
            btn = ctk.CTkButton(
                self.tab_bar,
                text=tab["text"],
                font=("Poppins", 15, "bold"),
                width=135, height=37, corner_radius=6,
                command=lambda t=tab["name"]: self.switch_tab(t)
            )
            padx_val = (0, 5) if i < len(tabs_disponiveis) - 1 else 0
            btn.pack(side="left", padx=padx_val)
            self.tab_buttons[tab["name"]] = btn

    def switch_tab(self, tab_name):
        self.current_tab = tab_name
        
        estilo_ativo = {
            "fg_color": self.colors["tab_active"],
            "text_color": self.colors["accent"],
            "hover_color": self.colors["tab_active"]
        }
        estilo_inativo = {
            "fg_color": self.colors["tab_inactive"],
            "text_color": self.colors["text_secondary"],
            "hover_color": "#D1D5DB"
        }

        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.configure(**estilo_ativo)
            else:
                btn.configure(**estilo_inativo)

        for widget in self.content_area.winfo_children():
            widget.destroy()

        render_methods = {
            "Perfil": self._render_profile,
            "Segurança": self._render_security,
            "Minha Clínica": self._render_preferences
        }
        
        if tab_name in render_methods:
            render_methods[tab_name](self.content_area)

    # =====================================================
    # COMPONENTES REUTILIZÁVEIS (IDÊNTICOS AO CODE 1)
    # =====================================================
    def _titulo(self, parent, texto):
        """Mantém a mesma altura e margem do título do CODE 1 (padx=60)."""
        ctk.CTkLabel(
            parent, text=texto, font=("Poppins", 24, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=60, pady=(24, 17))

    def _secao_titulo(self, parent, texto, padx=60):
        """Mantém a linha azul e a fonte idênticas ao CODE 1."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=padx, pady=(16, 8))

        ctk.CTkLabel(
            container,
            text=texto,
            font=("Poppins", 16, "bold"),
            text_color="#374151"
        ).pack(anchor="w")

        linha = ctk.CTkFrame(container, height=2, width=52, fg_color=self.colors["accent"], corner_radius=1)
        linha.pack(anchor="w", pady=(4, 0))

    # ==================== SEGURANÇA ====================
    def _render_security(self, parent):
        self._titulo(parent, "Segurança da Conta")

        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, 20), anchor="w")
        
        self._secao_titulo(password_frame, "Alterar Senha", padx=60)

        form_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=60, anchor="w") 

        current_pwd = ModernInput(
            form_frame, label="Senha Atual", placeholder="Digite sua senha atual",
            icon="🔑", required=True
        )
        current_pwd.pack(fill="x", pady=5, anchor="w")
        current_pwd.entry.configure(show="•")

        new_pwd = ModernInput(
            form_frame, label="Nova Senha", placeholder="Digite a nova senha",
            icon="🔒", required=True
        )
        new_pwd.pack(fill="x", pady=5, anchor="w")
        new_pwd.entry.configure(show="•")

        confirm_pwd = ModernInput(
            form_frame, label="Confirmar Nova Senha", placeholder="Digite novamente a nova senha",
            icon="✓", required=True
        )
        confirm_pwd.pack(fill="x", pady=5, anchor="w")
        confirm_pwd.entry.configure(show="•")

        strength_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        strength_frame.pack(fill="x", pady=(10, 0), anchor="w")
        
        ctk.CTkLabel(
            strength_frame, text="Força da senha:", font=("Poppins", 12),
            text_color=self.colors["text_secondary"]
        ).pack(side="left")
        
        self.strength_bar = ctk.CTkProgressBar(
            strength_frame, width=200, height=6, corner_radius=3,
            progress_color=self.colors["accent"]
        )
        self.strength_bar.pack(side="left", padx=(10, 0))
        self.strength_bar.set(0)
        
        new_pwd.entry.bind("<KeyRelease>", lambda e: self._check_password_strength(new_pwd.entry.get()))

    def _check_password_strength(self, password):
        strength = 0
        if len(password) >= 8: strength += 0.25
        if any(c.isupper() for c in password): strength += 0.25
        if any(c.isdigit() for c in password): strength += 0.25
        if any(c in "!@#$%&*" for c in password): strength += 0.25
            
        self.strength_bar.set(strength)
        if strength < 0.5: self.strength_bar.configure(progress_color="#EF4444")
        elif strength < 0.75: self.strength_bar.configure(progress_color="#F59E0B")
        else: self.strength_bar.configure(progress_color="#10B981")

    # ==================== PREFERÊNCIAS ====================
    def _render_preferences(self, parent):
        self._titulo(parent, "Configurações da Clínica")

        sub_tabs = ["Geral", "Serviços", "Descrição"]
        self.sub_tab_buttons = {}
        
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", padx=60, pady=(0, 10), anchor="w") 
        
        for tab in sub_tabs:
            btn = ctk.CTkButton(
                tab_frame, text=tab, fg_color="transparent",
                hover_color=self.colors["accent_light"],
                font=("Poppins", 14, "bold"),
                text_color=self.colors["text_secondary"],
                anchor="w", command=lambda t=tab.lower(): self._switch_sub_tab(parent, t)
            )
            btn.pack(side="left", padx=(0, 25))
            self.sub_tab_buttons[tab.lower()] = btn
        
        divider = ctk.CTkFrame(parent, height=1, fg_color=self.colors["border"])
        divider.pack(fill="x", padx=60, pady=(0, 15)) 
        
        self.sub_tab_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.sub_tab_content.pack(fill="both", expand=True, anchor="w")
        
        self._switch_sub_tab(parent, "geral")

    def _switch_sub_tab(self, parent, tab_name):
        for name, btn in self.sub_tab_buttons.items():
            if name == tab_name:
                btn.configure(text_color=self.colors["accent"])
            else:
                btn.configure(text_color=self.colors["text_secondary"])
        
        for widget in self.sub_tab_content.winfo_children():
            widget.destroy()
        
        if tab_name == "geral": self._render_preferences_geral(self.sub_tab_content)
        elif tab_name == "serviços": self._render_preferences_services(self.sub_tab_content)
        elif tab_name == "descrição": self._render_preferences_description(self.sub_tab_content)

    def _render_preferences_geral(self, parent):
        scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent",
            scrollbar_button_color="#D1D5DB", scrollbar_button_hover_color="#9CA3AF"
        )
        scroll.pack(fill="both", expand=True, anchor="w")
        
        # Carregar dados da clínica do BD (se for conta da clínica)
        clinica_data = None
        endereco_data = None
        if self.tipo_usuario == "clinica" and self.clinica_id:
            clinica_data = self._load_clinic_data()
            endereco_data = self._load_endereco_data()

        # ========== LOGO DA CLÍNICA (apenas para conta da clínica) ==========
        if self.tipo_usuario == "clinica":
            logo_section = ctk.CTkFrame(scroll, fg_color="transparent")
            logo_section.pack(fill="x", padx=60, pady=(0, 25), anchor="w")
            
            self._secao_titulo(logo_section, "Logo da Clínica", padx=0)
            
            logo_container = ctk.CTkFrame(
                logo_section, fg_color="transparent", width=140, height=140
            )
            logo_container.pack(anchor="w", pady=(0, 15))
            logo_container.pack_propagate(False)
            
            # Preview da logo (círculo)
            self.logo_canvas = tk.Canvas(
                logo_container, width=140, height=140, bg="white", 
                highlightthickness=0, bd=0
            )
            self.logo_canvas.pack()
            self.logo_canvas.create_oval(5, 5, 135, 135, 
                fill=self.colors["accent_light"], outline=self.colors["accent"], width=2)
            self.logo_canvas.create_text(70, 70, text="LOGO", 
                font=("Arial", 18, "bold"), fill=self.colors["accent"])
            
            self.logo_upload_btn = ctk.CTkButton(
                logo_section, text="📷 Alterar Logo",
                font=("Poppins", 14), fg_color=self.colors["accent"],
                hover_color=self.colors["accent_hover"], height=44, corner_radius=5,
                command=self._load_clinic_logo, width=200
            )
            self.logo_upload_btn.pack(anchor="w")
            
            # Informações da Clínica
            clinic_section = ctk.CTkFrame(scroll, fg_color="transparent")
            clinic_section.pack(fill="x", padx=60, pady=(0, 25), anchor="w")
            
            self._secao_titulo(clinic_section, "Informações da Clínica", padx=0)
            
            clinic_form = ctk.CTkFrame(clinic_section, fg_color="transparent")
            clinic_form.pack(fill="x", anchor="w")
            clinic_form.grid_columnconfigure((0, 1), weight=1)
            
            fields = [
                {"label": "Nome da Clínica", "placeholder": "Nome oficial", "row": 0, "col": 0, "required": True},
                {"label": "CNPJ", "placeholder": "00.000.000/0000-00", "row": 0, "col": 1, "required": True},
                {"label": "E-mail Clínica", "placeholder": "email@clinica.com", "row": 1, "col": 0, "required": True},
                {"label": "Telefone", "placeholder": "(00) 0000-0000", "row": 1, "col": 1, "required": True},
            ]
            
            for field in fields:
                padx_val = (0, 5) if field["col"] == 0 else (5, 0)
                
                input_widget = ModernInput(
                    clinic_form, label=field["label"], placeholder=field["placeholder"],
                    required=field.get("required", False)
                )
                input_widget.grid(
                    row=field["row"], column=field["col"], sticky="ew",
                    padx=padx_val, pady=5
                )
                self.clinic_entries[field["label"]] = input_widget
            
            # Preencher campos com dados existentes
            if clinica_data:
                self.clinic_entries["Nome da Clínica"].set(clinica_data.get("nome", ""))
                self.clinic_entries["CNPJ"].set(clinica_data.get("cnpj", ""))
                self.clinic_entries["E-mail Clínica"].set(clinica_data.get("email", ""))
                self.clinic_entries["Telefone"].set(clinica_data.get("telefone", ""))

        # ========== FOTOS DA CLÍNICA ==========
        photos_section = ctk.CTkFrame(scroll, fg_color="transparent")
        photos_section.pack(fill="x", padx=60, pady=(0, 25), anchor="w") 

        self._secao_titulo(photos_section, "Fotos da Clínica", padx=0)

        ctk.CTkLabel(
            photos_section, text="Foto Principal da Fachada", font=("Poppins", 14),
            text_color=self.colors["text_primary"], anchor="w"
        ).pack(anchor="w")

        self.main_photo_container = ctk.CTkFrame(
            photos_section, fg_color="#F9FAFB", corner_radius=5,
            height=150, border_width=1, border_color=self.colors["border"]
        )
        self.main_photo_container.pack(fill="x", pady=(8, 20), anchor="w")
        self.main_photo_container.pack_propagate(False)

        self.main_photo_btn = ctk.CTkButton(
            self.main_photo_container, text="📷 Carregar Foto da Fachada",
            font=("Poppins", 14), fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"], height=44, corner_radius=5,
            command=self._load_main_photo
        )
        self.main_photo_btn.pack(expand=True)

        address_section = ctk.CTkFrame(scroll, fg_color="transparent")
        address_section.pack(fill="x", padx=60, pady=(0, 10), anchor="w") 

        self._secao_titulo(address_section, "Endereço da Clínica", padx=0)

        address_form = ctk.CTkFrame(address_section, fg_color="transparent")
        address_form.pack(fill="x", anchor="w")
        address_form.grid_columnconfigure((0, 1), weight=1)

        fields = [
            {"label": "Rua", "col": 0, "row": 0, "placeholder": "Nome da rua"},
            {"label": "Número", "col": 1, "row": 0, "placeholder": "123"},
            {"label": "Bairro", "col": 0, "row": 1, "placeholder": "Nome do bairro"},
            {"label": "Cidade", "col": 1, "row": 1, "placeholder": "Nome da cidade"},
            {"label": "Estado", "col": 0, "row": 2, "placeholder": "UF"},
            {"label": "CEP", "col": 1, "row": 2, "placeholder": "00000-000"}
        ]

        for field in fields:
            # ALINHAMENTO: Lógica de padding idêntica ao _campo_duplo do CODE 1
            padx_val = (0, 5) if field["col"] == 0 else (5, 0)
            
            lbl = ctk.CTkLabel(
                address_form, text=field["label"], font=("Poppins", 14),
                text_color=self.colors["text_secondary"], anchor="w"
            )
            lbl.grid(row=field["row"]*2, column=field["col"], sticky="w", pady=(8, 2), padx=padx_val)
            
            entry = ctk.CTkEntry(
                address_form, placeholder_text=field["placeholder"],
                height=44, corner_radius=5, border_width=1,
                border_color=self.colors["border"], fg_color="#F9FAFB", font=("Poppins", 14)
            )
            entry.grid(row=field["row"]*2 + 1, column=field["col"], sticky="ew", padx=padx_val)
            
            # Preencher com dados existentes
            if endereco_data:
                if field["label"] == "Rua" and endereco_data.get("rua"):
                    entry.insert(0, endereco_data["rua"])
                elif field["label"] == "Número" and endereco_data.get("numero"):
                    entry.insert(0, endereco_data["numero"])
                elif field["label"] == "Bairro" and endereco_data.get("bairro"):
                    entry.insert(0, endereco_data["bairro"])
                elif field["label"] == "Cidade" and endereco_data.get("cidade"):
                    entry.insert(0, endereco_data["cidade"])
                elif field["label"] == "Estado" and endereco_data.get("estado"):
                    entry.insert(0, endereco_data["estado"])
                elif field["label"] == "CEP" and endereco_data.get("cep"):
                    entry.insert(0, endereco_data["cep"])

    def _render_preferences_services(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, anchor="w")
        
        self._secao_titulo(scroll, "Serviços Oferecidos", padx=60)

        self.services_text = ctk.CTkTextbox(
            scroll, height=180, corner_radius=5, border_width=1,
            border_color=self.colors["border"], fg_color="#F9FAFB", font=("Poppins", 14)
        )
        self.services_text.pack(fill="both", expand=True, anchor="w", padx=60, pady=(10, 0))
        self.services_text.insert("1.0", "• Limpeza profissional\n• Clareamento dental\n• Implantes\n• Aparelhos ortodônticos")

    def _render_preferences_description(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, anchor="w")
        
        self._secao_titulo(scroll, "Sobre a Clínica", padx=60)

        self.description_text = ctk.CTkTextbox(
            scroll, height=280, corner_radius=5, border_width=1,
            border_color=self.colors["border"], fg_color="#F9FAFB", font=("Poppins", 14)
        )
        self.description_text.pack(fill="both", expand=True, anchor="w", padx=60, pady=(10, 0))
        self.description_text.insert("1.0", "Bem-vindo à nossa clínica! Somos uma equipe dedicada a proporcionar o melhor cuidado para seu sorriso...")

    # ==================== PERFIL ====================
    def _render_profile(self, parent):
        self._titulo(parent, "Meu Perfil")

        profile_container = ctk.CTkFrame(parent, fg_color="transparent")
        profile_container.pack(fill="both", expand=True, padx=60) 
        profile_container.grid_columnconfigure(0, weight=0)
        profile_container.grid_columnconfigure(1, weight=1)

        self._render_avatar(profile_container)
        self._render_profile_form(profile_container)

    def _render_avatar(self, parent):
        avatar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        avatar_frame.grid(row=0, column=0, sticky="nw", padx=(0, 25))

        self._secao_titulo(avatar_frame, "Foto de Perfil", padx=0)

        avatar_container = ctk.CTkFrame(avatar_frame, fg_color="transparent", width=140, height=140)
        avatar_container.pack(anchor="w", pady=(0, 25))
        avatar_container.pack_propagate(False)

        self.avatar_canvas = tk.Canvas(
            avatar_container, width=140, height=140, bg="white", highlightthickness=0, bd=0
        )
        self.avatar_canvas.pack()
        self.avatar_canvas.create_oval(5, 5, 135, 135, fill=self.colors["accent_light"], outline=self.colors["accent"], width=2)
        self.avatar_canvas.create_text(70, 70, text="GG", font=("Arial", 36, "bold"), fill=self.colors["accent"])

        upload_btn = ctk.CTkButton(
            avatar_frame, text="Alterar foto", fg_color="transparent",
            hover_color=self.colors["accent_light"], text_color=self.colors["accent"],
            border_width=1, border_color=self.colors["accent"],
            height=44, corner_radius=5, font=("Poppins", 14),
            anchor="center", command=self._change_avatar
        )
        upload_btn.pack(anchor="w", fill="x")

    def _render_profile_form(self, parent):
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.grid(row=0, column=1, sticky="nsew")
        form_frame.grid_columnconfigure((0, 1), weight=1)

        title_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, columnspan=2, sticky="w")
        self._secao_titulo(title_container, "Informações Pessoais", padx=0)

        fields = [
            {"label": "Nome Completo", "placeholder": "Gabriel Gomes", "row": 1, "col": 0, "icon": "👤", "required": True},
            {"label": "CPF", "placeholder": "000.000.000-00", "row": 1, "col": 1, "icon": "📄", "required": True},
            {"label": "E-mail", "placeholder": "gabriel@email.com", "row": 2, "col": 0, "icon": "✉️", "required": True},
            {"label": "Telefone", "placeholder": "(00) 00000-0000", "row": 2, "col": 1, "icon": "📞", "required": True},
            {"label": "Data de Nascimento", "placeholder": "24/05/2002", "row": 3, "col": 0, "icon": "🎂", "required": False},
            {"label": "Profissão", "placeholder": "Dentista", "row": 3, "col": 1, "icon": "💼", "required": False}
        ]

        self.profile_entries = {}
        for field in fields:
            input_widget = ModernInput(
                form_frame, label=field["label"], placeholder=field["placeholder"],
                icon=field["icon"], required=field.get("required", False)
            )
            # ALINHAMENTO: Lógica de padding idêntica ao _campo_duplo do CODE 1
            padx_val = (0, 5) if field["col"] == 0 else (5, 0)
            
            input_widget.grid(
                row=field["row"], column=field["col"], sticky="ew",
                padx=padx_val, pady=5
            )
            self.profile_entries[field["label"]] = input_widget
        
        # Carregar dados do perfil do gerente/dentista
        profile_data = self._load_user_profile_data()
        if profile_data:
            self.profile_entries["Nome Completo"].set(profile_data.get("nome", ""))
            self.profile_entries["E-mail"].set(profile_data.get("email", ""))

    # ==================== FOOTER ====================
    def _build_footer(self, parent):
        """ALINHAMENTO CRÍTICO: Rodapé perfeitamente alinhado com o CODE 1 (padx=60, pady=14)"""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=60, pady=14)

        # Botão Principal (Salvar) - Tamanho e fonte idênticos ao CODE 1
        save_btn = ctk.CTkButton(
            footer, text="SALVAR ALTERAÇÕES", fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"], text_color="white",
            height=44, width=220, corner_radius=5,
            font=("Poppins", 15, "bold"),
            command=self._save
        )
        save_btn.pack(side="left", padx=(0, 8))

        # Botão Secundário (Cancelar) - Tamanho e fonte idênticos ao CODE 1
        cancel_btn = ctk.CTkButton(
            footer, text="CANCELAR", fg_color="transparent",
            hover_color="#F3F4F6", text_color=self.colors["text_secondary"],
            border_width=1, border_color=self.colors["border"],
            height=44, width=125, corner_radius=5,
            font=("Poppins", 15),
            command=self._cancel
        )
        cancel_btn.pack(side="left")

    # ==================== CARREGAMENTO DE DADOS ====================
    def _load_clinic_data(self):
        """
        Carrega dados da clínica do banco de dados
        Retorna dicionário com nome, cnpj, email, telefone
        """
        try:
            from config.database import get_connection
            
            conn = None
            cursor = None
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT nome, cnpj, email, telefone, logo
                    FROM odontoPro_clinica
                    WHERE id = %s
                """, (self.clinica_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "nome": result[0] or "",
                        "cnpj": result[1] or "",
                        "email": result[2] or "",
                        "telefone": result[3] or "",
                        "logo": result[4] or ""
                    }
                return None
            
            except Exception as e:
                print(f"[ERRO] Falha ao carregar dados da clínica: {e}")
                return None
            
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        except ImportError as e:
            print(f"[ERRO] Falha ao importar módulos: {e}")
            return None
    
    def _load_endereco_data(self):
        """
        Carrega dados de endereço da clínica do banco de dados
        Retorna dicionário com rua, numero, bairro, cidade, estado, cep
        """
        try:
            from config.database import get_connection
            
            conn = None
            cursor = None
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Buscar endereço da clínica
                cursor.execute("""
                    SELECT e.rua, e.numero, e.bairro, e.cidade, e.estado, e.cep
                    FROM odontoPro_clinica c
                    LEFT JOIN odontoPro_endereco e ON c.endereco_id = e.id
                    WHERE c.id = %s
                """, (self.clinica_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "rua": result[0] or "",
                        "numero": result[1] or "",
                        "bairro": result[2] or "",
                        "cidade": result[3] or "",
                        "estado": result[4] or "",
                        "cep": result[5] or ""
                    }
                return None
            
            except Exception as e:
                print(f"[ERRO] Falha ao carregar dados de endereço: {e}")
                return None
            
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        except ImportError as e:
            print(f"[ERRO] Falha ao importar módulos: {e}")
            return None
    
    def _load_user_profile_data(self):
        """
        Carrega dados do perfil do gerente/dentista logado
        Retorna dicionário com nome e email
        """
        try:
            from config.database import get_connection
            
            # Se não for gerenciamento/dentista, não há dados para carregar
            if self.tipo_usuario not in ["gerenciamento", "dentista"]:
                return None
            
            conn = None
            cursor = None
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Buscar dados do gerente/usuário
                cursor.execute("""
                    SELECT nome, email
                    FROM odontoPro_gerenciamento
                    WHERE id = %s
                """, (self.usuario_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        "nome": result[0] or "",
                        "email": result[1] or ""
                    }
                return None
            
            except Exception as e:
                print(f"[ERRO] Falha ao carregar dados do perfil: {e}")
                return None
            
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        except ImportError as e:
            print(f"[ERRO] Falha ao importar módulos: {e}")
            return None
    def _load_clinic_logo(self):
        """Carrega logo da clínica"""
        file_path = filedialog.askopenfilename(
            title="Selecionar logo da clínica", 
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.logo_upload_btn.configure(text="⏳ Carregando...", state="disabled")
            self.after(100, lambda: self._finish_load_clinic_logo(file_path))
    
    def _finish_load_clinic_logo(self, file_path):
        """Finaliza carregamento da logo"""
        self.images['logo'] = file_path
        self.logo_upload_btn.configure(
            text="✓ Logo carregada", 
            fg_color=self.colors["success"], 
            state="normal"
        )

    def _load_main_photo(self):
        file_path = filedialog.askopenfilename(title="Selecionar foto da fachada", filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            self.main_photo_btn.configure(text="⏳ Carregando...", state="disabled")
            self.after(100, lambda: self._finish_load_main_photo(file_path))

    def _finish_load_main_photo(self, file_path):
        self.images['main'] = file_path
        self.main_photo_btn.configure(text="✓ Foto carregada", fg_color=self.colors["success"], state="normal")

    def _change_avatar(self):
        file_path = filedialog.askopenfilename(title="Selecionar foto de perfil", filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")])
        if file_path: messagebox.showinfo("Sucesso", "Foto de perfil atualizada com sucesso!")

    def _cancel(self):
        result = messagebox.askyesno("Cancelar", "Tem certeza que deseja cancelar? Todas as alterações não salvas serão perdidas.")
        if result: pass

    def _save(self):
        all_valid = True
        
        # Validar Perfil (gerentes/dentistas)
        if self.current_tab == "Perfil":
            for field_name, input_widget in self.profile_entries.items():
                if not input_widget._validate(): 
                    all_valid = False
        
        # Validar Clínica (conta da clínica)
        if self.current_tab == "Minha Clínica" and self.tipo_usuario == "clinica":
            for field_name, input_widget in self.clinic_entries.items():
                if not input_widget._validate(): 
                    all_valid = False
        
        if all_valid:
            # Se é clínica, salvar dados no BD
            if self.tipo_usuario == "clinica" and self.clinica_id:
                self._save_clinic_data()
            else:
                messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")
    
    def _save_clinic_data(self):
        """Salva dados da clínica no banco de dados"""
        try:
            from config.database import get_connection
            import os
            from datetime import datetime
            
            conn = None
            cursor = None
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Preparar dados
                nome = self.clinic_entries["Nome da Clínica"].get().strip()
                cnpj = self.clinic_entries["CNPJ"].get().strip()
                email = self.clinic_entries["E-mail Clínica"].get().strip()
                telefone = self.clinic_entries["Telefone"].get().strip()
                
                # Atualizar informações da clínica
                cursor.execute("""
                    UPDATE odontoPro_clinica 
                    SET nome = %s, cnpj = %s, email = %s, telefone = %s
                    WHERE id = %s
                """, (nome, cnpj, email, telefone, self.clinica_id))
                
                # Se carregou uma nova logo, salvar arquivo
                if 'logo' in self.images:
                    logo_path = self.images['logo']
                    # Copicar arquivo para pasta de uploads
                    import shutil
                    upload_dir = os.path.join(os.path.dirname(__file__), "../assets/clinicas/logo")
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    filename = f"clinica_{self.clinica_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    dest_path = os.path.join(upload_dir, filename)
                    shutil.copy(logo_path, dest_path)
                    
                    # Salvar caminho da logo no BD
                    cursor.execute("""
                        UPDATE odontoPro_clinica 
                        SET logo = %s
                        WHERE id = %s
                    """, (dest_path, self.clinica_id))
                
                conn.commit()
                messagebox.showinfo("Sucesso", "✓ Dados da clínica atualizados com sucesso!")
                
            except Exception as e:
                if conn:
                    conn.rollback()
                messagebox.showerror("Erro", f"Erro ao salvar dados da clínica: {str(e)}")
                print(f"[ERRO] {str(e)}")
            
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        
        except ImportError as e:
            messagebox.showerror("Erro", f"Erro ao importar módulos: {str(e)}")