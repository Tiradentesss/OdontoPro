import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from .base import BaseScreen
from .theme import font, ICON_SIZE, COLORS
import os
from PIL import Image, ImageTk, ImageDraw


class ImagePreview:
    """Classe utilitária para gerenciar previews de imagens"""

    @staticmethod
    def create_circular_preview(canvas, image_path, size=140, placeholder_text="IMG"):
        """Cria preview circular de imagem em um canvas"""
        canvas.delete("all")

        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path).convert("RGBA")
                img = img.resize((size - 10, size - 10), Image.Resampling.LANCZOS)

                mask = Image.new("L", (size - 10, size - 10), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size - 10, size - 10), fill=255)

                img.putalpha(mask)
                photo = ImageTk.PhotoImage(img)

                canvas.create_image(size // 2, size // 2, image=photo)
                canvas.image = photo
                canvas.create_oval(5, 5, size - 5, size - 5, outline=COLORS["primary"], width=2)

            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
                ImagePreview._draw_placeholder_circle(canvas, size, placeholder_text)
        else:
            ImagePreview._draw_placeholder_circle(canvas, size, placeholder_text)

    @staticmethod
    def create_rectangular_preview(canvas, image_path, width=300, height=150, placeholder_text="IMG"):
        """Cria preview retangular de imagem em um canvas"""
        canvas.delete("all")

        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img_ratio = img.width / img.height
                canvas_ratio = width / height

                if img_ratio > canvas_ratio:
                    new_width = width
                    new_height = int(width / img_ratio)
                else:
                    new_height = height
                    new_width = int(height * img_ratio)

                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                x_offset = (width - new_width) // 2
                y_offset = (height - new_height) // 2

                photo = ImageTk.PhotoImage(img)
                canvas.create_image(x_offset + new_width // 2, y_offset + new_height // 2, image=photo)
                canvas.image = photo

                canvas.create_rectangle(2, 2, width - 2, height - 2, outline=COLORS["border"], width=1)

            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
                ImagePreview._draw_placeholder_rectangle(canvas, width, height, placeholder_text)
        else:
            ImagePreview._draw_placeholder_rectangle(canvas, width, height, placeholder_text)

    @staticmethod
    def _draw_placeholder_circle(canvas, size, text):
        colors = {"bg": COLORS["accent_light"], "border": COLORS["primary"], "text": COLORS["primary"]}
        canvas.create_oval(5, 5, size - 5, size - 5, fill=colors["bg"], outline=colors["border"], width=2)
        canvas.create_text(size // 2, size // 2, text=text, font=font("subtitle"), fill=colors["text"])

    @staticmethod
    def _draw_placeholder_rectangle(canvas, width, height, text):
        colors = {"bg": COLORS["input_bg"], "border": COLORS["border"], "text": COLORS["text_secondary"]}
        canvas.create_rectangle(2, 2, width - 2, height - 2, fill=colors["bg"], outline=colors["border"], width=1)
        canvas.create_text(width // 2, height // 2, text=text, font=font("text"), fill=colors["text"])

    @staticmethod
    def _get_initials(name):
        if not name:
            return "U"
        parts = name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1:
            return parts[0][:2].upper()
        return "U"


class ModernInput(ctk.CTkFrame):
    """Componente de input padronizado com ícone e validação"""
    def __init__(self, parent, label="", placeholder="", icon=None, required=False, **kwargs):
        super().__init__(parent, fg_color="transparent")

        self.required = required

        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 3))

        lbl = ctk.CTkLabel(
            label_frame,
            text=label,
            font=font("text"),
            text_color=COLORS["text_secondary"]
        )
        lbl.pack(side="left")

        if required:
            required_lbl = ctk.CTkLabel(
                label_frame,
                text="*",
                font=font("text", "bold"),
                text_color=COLORS["danger"]
            )
            required_lbl.pack(side="left", padx=(2, 0))

        input_container = ctk.CTkFrame(self, fg_color="transparent")
        input_container.pack(fill="x")

        if icon:
            icon_lbl = ctk.CTkLabel(
                input_container,
                text=icon,
                font=font("text"),
                width=30
            )
            icon_lbl.pack(side="left", padx=(0, 5))

        self.entry = ctk.CTkEntry(
            input_container,
            placeholder_text=placeholder,
            height=44,
            corner_radius=5,
            border_width=1,
            border_color=COLORS["border"],
            fg_color=COLORS["input_bg"],
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
            font=font("text"),
            **kwargs
        )
        self.entry.pack(side="left", fill="x", expand=True)

        self.entry.bind("<FocusOut>", self._validate)

    def _validate(self, event=None):
        if self.required and not self.entry.get().strip():
            self.entry.configure(border_color=COLORS["danger"])
            return False
        else:
            self.entry.configure(border_color=COLORS["border"])
            return True

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class Configuracoes(BaseScreen):
    def __init__(self, parent, tipo_usuario="clinica", clinica_id=None, usuario_id=None):
        super().__init__(parent, "Configurações")

        self.tipo_usuario = tipo_usuario
        self.clinica_id = clinica_id
        self.usuario_id = usuario_id

        self.colors = {
            "bg_main": COLORS["content_bg"],
            "bg_card": COLORS["card"],
            "text_primary": COLORS["text"],
            "text_secondary": COLORS["text_secondary"],
            "text_muted": COLORS["text_muted"],
            "accent": COLORS["primary"],
            "accent_hover": COLORS["accent_hover"],
            "accent_light": COLORS["accent_light"],
            "border": COLORS["border"],
            "border_focus": COLORS["primary"],
            "success": COLORS["success"],
            "error": COLORS["danger"],
            "input_bg": COLORS["input_bg"],
            "tab_active": COLORS["tab_active"],
            "tab_inactive": COLORS["tab_inactive"]
        }

        self.current_tab = "Perfil"
        self.tab_buttons = {}
        self.images = {}
        self.loading_states = {}
        self.clinic_entries = {}
        self.profile_entries = {}
        self.address_entries = {}

        self.setup_ui()

    def setup_ui(self):
        self.tab_bar = ctk.CTkFrame(self.content_card, fg_color="transparent", height=44)
        self.tab_bar.pack(fill="x", padx=25, pady=(9, 0), anchor="nw")

        self._build_tabs()

        self.container_outer = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent",
            corner_radius=20
        )
        self.container_outer.pack(fill="both", expand=True, padx=25, pady=(6, 20))

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
        todas_abas = [
            {"name": "Perfil", "text": "👤   Perfil", "tipo_acesso": ["gerenciamento", "dentista"]},
            {"name": "Segurança", "text": "🔒   Segurança", "tipo_acesso": ["clinica", "gerenciamento", "dentista"]},
            {"name": "Minha Clínica", "text": "🏥   Minha Clínica", "tipo_acesso": ["clinica"]}
        ]

        tabs_disponiveis = [tab for tab in todas_abas if self.tipo_usuario in tab["tipo_acesso"]]

        if tabs_disponiveis:
            self.current_tab = tabs_disponiveis[0]["name"]

        for i, tab in enumerate(tabs_disponiveis):
            btn = ctk.CTkButton(
                self.tab_bar,
                text=tab["text"],
                font=font("button_large", "bold"),
                width=135,
                height=37,
                corner_radius=6,
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
            "hover_color": COLORS["hover"]
        }

        for name, btn in self.tab_buttons.items():
            btn.configure(**(estilo_ativo if name == tab_name else estilo_inativo))

        for widget in self.content_area.winfo_children():
            widget.destroy()

        render_methods = {
            "Perfil": self._render_profile,
            "Segurança": self._render_security,
            "Minha Clínica": self._render_preferences
        }

        if tab_name in render_methods:
            render_methods[tab_name](self.content_area)

    def _titulo(self, parent, texto, padx=25):
        ctk.CTkLabel(
            parent,
            text=texto,
            font=font("title", "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=padx, pady=(24, 17))

    def _secao_titulo(self, parent, texto, padx=25):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=padx, pady=(16, 8))

        ctk.CTkLabel(
            container,
            text=texto,
            font=font("subtitle", "bold"),
            text_color="#374151"
        ).pack(anchor="w")

        linha = ctk.CTkFrame(container, height=2, width=52, fg_color=self.colors["accent"], corner_radius=1)
        linha.pack(anchor="w", pady=(4, 0))

    def _create_card_section(self, parent, title, subtitle=None):
        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color=self.colors["border"]
        )
        card.pack(fill="x", padx=25, pady=(0, 20), anchor="w")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=title,
            font=font("card_title", "bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                header,
                text=subtitle,
                font=font("text"),
                text_color=self.colors["text_secondary"]
            ).pack(anchor="w", pady=(2, 0))

        line = ctk.CTkFrame(
            header,
            height=2,
            width=56,
            fg_color=self.colors["accent"],
            corner_radius=1
        )
        line.pack(anchor="w", pady=(8, 0))

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=24, pady=(0, 24))

        return card, body

    # ==================== SEGURANÇA ====================
    def _render_security(self, parent):
        self._titulo(parent, "Segurança da Conta")

        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", pady=(0, 20), anchor="w")

        self._secao_titulo(password_frame, "Alterar Senha", padx=25)

        form_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=25, anchor="w")

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
            strength_frame, text="Força da senha:", font=font("small"),
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
        if len(password) >= 8:
            strength += 0.25
        if any(c.isupper() for c in password):
            strength += 0.25
        if any(c.isdigit() for c in password):
            strength += 0.25
        if any(c in "!@#$%&*" for c in password):
            strength += 0.25

        self.strength_bar.set(strength)
        if strength < 0.5:
            self.strength_bar.configure(progress_color=COLORS["danger"])
        elif strength < 0.75:
            self.strength_bar.configure(progress_color=COLORS["warning"])
        else:
            self.strength_bar.configure(progress_color=COLORS["success"])

    # ==================== MINHA CLÍNICA ====================
    def _render_preferences(self, parent):
        self._titulo(parent, "Configurações da Clínica", padx=25)

        sub_tabs = ["Geral", "Serviços", "Descrição"]
        self.sub_tab_buttons = {}

        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", padx=25, pady=(0, 10), anchor="w")

        for tab in sub_tabs:
            btn = ctk.CTkButton(
                tab_frame,
                text=tab,
                fg_color="transparent",
                hover_color=self.colors["accent_light"],
                font=font("text", "bold"),
                text_color=self.colors["text_secondary"],
                anchor="w",
                command=lambda t=tab.lower(): self._switch_sub_tab(parent, t)
            )
            btn.pack(side="left", padx=(0, 25))
            self.sub_tab_buttons[tab.lower()] = btn

        divider = ctk.CTkFrame(parent, height=1, fg_color=self.colors["border"])
        divider.pack(fill="x", padx=25, pady=(0, 15))

        self.sub_tab_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.sub_tab_content.pack(fill="both", expand=True, anchor="w")

        self._switch_sub_tab(parent, "geral")

    def _switch_sub_tab(self, parent, tab_name):
        for name, btn in self.sub_tab_buttons.items():
            btn.configure(text_color=self.colors["accent"] if name == tab_name else self.colors["text_secondary"])

        for widget in self.sub_tab_content.winfo_children():
            widget.destroy()

        if tab_name == "geral":
            self._render_preferences_geral(self.sub_tab_content)
        elif tab_name == "serviços":
            self._render_preferences_services(self.sub_tab_content)
        elif tab_name == "descrição":
            self._render_preferences_description(self.sub_tab_content)

    def _render_preferences_geral(self, parent):
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["text_muted"]
        )
        scroll.pack(fill="both", expand=True, anchor="w")

        clinica_data = None
        endereco_data = None

        if self.tipo_usuario == "clinica" and self.clinica_id:
            clinica_data = self._load_clinic_data()
            endereco_data = self._load_endereco_data()

        # CARD IDENTIDADE
        if self.tipo_usuario == "clinica":
            _, identidade_body = self._create_card_section(
                scroll,
                "Identidade da Clínica",
                "Gerencie logo e informações principais da clínica"
            )

            identidade_body.grid_columnconfigure(0, weight=0)
            identidade_body.grid_columnconfigure(1, weight=1)

            logo_col = ctk.CTkFrame(identidade_body, fg_color="transparent")
            logo_col.grid(row=0, column=0, sticky="n", padx=(0, 28), pady=(4, 0))

            logo_wrap = ctk.CTkFrame(
                logo_col,
                fg_color="transparent",
                width=150,
                height=150
            )
            logo_wrap.pack()
            logo_wrap.pack_propagate(False)

            self.logo_canvas = tk.Canvas(
                logo_wrap,
                width=140,
                height=140,
                bg="white",
                highlightthickness=0,
                bd=0
            )
            self.logo_canvas.pack(pady=5)

            logo_path = clinica_data.get("logo") if clinica_data else None
            ImagePreview.create_circular_preview(self.logo_canvas, logo_path, 140, "LOGO")

            self.logo_upload_btn = ctk.CTkButton(
                logo_col,
                text="📷 Alterar Logo",
                font=font("text"),
                fg_color=self.colors["accent"],
                hover_color=self.colors["accent_hover"],
                height=44,
                corner_radius=8,
                command=self._load_clinic_logo,
                width=180
            )
            self.logo_upload_btn.pack(pady=(10, 0))

            info_col = ctk.CTkFrame(identidade_body, fg_color="transparent")
            info_col.grid(row=0, column=1, sticky="nsew")
            info_col.grid_columnconfigure((0, 1), weight=1)

            self.clinic_entries = {}

            fields = [
                {"label": "Nome da Clínica", "placeholder": "Nome oficial", "row": 0, "col": 0, "required": True},
                {"label": "CNPJ", "placeholder": "00.000.000/0000-00", "row": 0, "col": 1, "required": True},
                {"label": "E-mail Clínica", "placeholder": "email@clinica.com", "row": 1, "col": 0, "required": True},
                {"label": "Telefone", "placeholder": "(00) 00000-0000", "row": 1, "col": 1, "required": True},
            ]

            for field in fields:
                padx_val = (0, 8) if field["col"] == 0 else (8, 0)

                input_widget = ModernInput(
                    info_col,
                    label=field["label"],
                    placeholder=field["placeholder"],
                    required=field.get("required", False)
                )
                input_widget.grid(
                    row=field["row"],
                    column=field["col"],
                    sticky="ew",
                    padx=padx_val,
                    pady=8
                )
                self.clinic_entries[field["label"]] = input_widget

            if clinica_data:
                self.clinic_entries["Nome da Clínica"].set(clinica_data.get("nome", ""))
                self.clinic_entries["CNPJ"].set(clinica_data.get("cnpj", ""))
                self.clinic_entries["E-mail Clínica"].set(clinica_data.get("email", ""))
                self.clinic_entries["Telefone"].set(clinica_data.get("telefone", ""))

        # CARD FOTOS
        _, fotos_body = self._create_card_section(
            scroll,
            "Fotos da Clínica",
            "Adicione fachada, recepção e ambientes internos"
        )

        self.clinic_photos_container = ctk.CTkFrame(
            fotos_body,
            fg_color=COLORS["input_bg"],
            corner_radius=10,
            height=360,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.clinic_photos_container.pack(fill="both", expand=True, pady=(4, 0))
        self.clinic_photos_container.pack_propagate(False)

        self.clinic_photos = []
        self.current_photo_index = 0

        if clinica_data and clinica_data.get("photos"):
            self.clinic_photos = clinica_data["photos"]

        self._setup_clinic_photos_ui()

        # CARD ENDEREÇO
        _, endereco_body = self._create_card_section(
            scroll,
            "Endereço da Clínica",
            "Mantenha os dados de localização atualizados"
        )

        endereco_body.grid_columnconfigure((0, 1, 2), weight=1)
        self.address_entries = {}

        fields = [
            {"label": "CEP", "placeholder": "00000-000", "row": 0, "col": 0},
            {"label": "Estado", "placeholder": "UF", "row": 0, "col": 1},
            {"label": "Cidade", "placeholder": "Nome da cidade", "row": 0, "col": 2},
            {"label": "Rua", "placeholder": "Nome da rua", "row": 1, "col": 0},
            {"label": "Número", "placeholder": "123", "row": 1, "col": 1},
            {"label": "Bairro", "placeholder": "Nome do bairro", "row": 1, "col": 2},
        ]

        for field in fields:
            input_widget = ModernInput(
                endereco_body,
                label=field["label"],
                placeholder=field["placeholder"]
            )
            input_widget.grid(
                row=field["row"],
                column=field["col"],
                sticky="ew",
                padx=8,
                pady=8
            )
            self.address_entries[field["label"]] = input_widget

        if endereco_data:
            self.address_entries["Rua"].set(endereco_data.get("rua", ""))
            self.address_entries["Número"].set(endereco_data.get("numero", ""))
            self.address_entries["Bairro"].set(endereco_data.get("bairro", ""))
            self.address_entries["Cidade"].set(endereco_data.get("cidade", ""))
            self.address_entries["Estado"].set(endereco_data.get("estado", ""))
            self.address_entries["CEP"].set(endereco_data.get("cep", ""))

    def _render_preferences_services(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, anchor="w")

        self._secao_titulo(scroll, "Serviços Oferecidos", padx=25)

        self.services_text = ctk.CTkTextbox(
            scroll,
            height=180,
            corner_radius=5,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=COLORS["input_bg"],
            font=font("text")
        )
        self.services_text.pack(fill="both", expand=True, anchor="w", padx=25, pady=(10, 0))
        self.services_text.insert("1.0", "• Limpeza profissional\n• Clareamento dental\n• Implantes\n• Aparelhos ortodônticos")

    def _render_preferences_description(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, anchor="w")

        self._secao_titulo(scroll, "Sobre a Clínica", padx=25)

        self.description_text = ctk.CTkTextbox(
            scroll,
            height=280,
            corner_radius=5,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=COLORS["input_bg"],
            font=font("text")
        )
        self.description_text.pack(fill="both", expand=True, anchor="w", padx=25, pady=(10, 0))
        self.description_text.insert("1.0", "Bem-vindo à nossa clínica! Somos uma equipe dedicada a proporcionar o melhor cuidado para seu sorriso...")

    # ==================== PERFIL ====================
    def _render_profile(self, parent):
        self._titulo(parent, "Meu Perfil")

        profile_container = ctk.CTkFrame(parent, fg_color="transparent")
        profile_container.pack(fill="both", expand=True, padx=25)
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

        profile_data = self._load_user_profile_data()
        avatar_path = profile_data.get("avatar_path") if profile_data else None
        nome = profile_data.get("nome", "") if profile_data else ""
        placeholder_text = ImagePreview._get_initials(nome) if nome else "GG"
        ImagePreview.create_circular_preview(self.avatar_canvas, avatar_path, 140, placeholder_text)

        upload_btn = ctk.CTkButton(
            avatar_frame, text="Alterar foto", fg_color="transparent",
            hover_color=self.colors["accent_light"], text_color=self.colors["accent"],
            border_width=1, border_color=self.colors["accent"],
            height=44, corner_radius=5, font=font("text"),
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
            padx_val = (0, 5) if field["col"] == 0 else (5, 0)

            input_widget.grid(
                row=field["row"], column=field["col"], sticky="ew",
                padx=padx_val, pady=5
            )
            self.profile_entries[field["label"]] = input_widget

        profile_data = self._load_user_profile_data()
        if profile_data:
            self.profile_entries["Nome Completo"].set(profile_data.get("nome", ""))
            self.profile_entries["E-mail"].set(profile_data.get("email", ""))

    # ==================== FOOTER ====================
    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=25, pady=14)

        save_btn = ctk.CTkButton(
            footer, text="SALVAR ALTERAÇÕES", fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"], text_color="white",
            height=44, width=220, corner_radius=5,
            font=font("button_large", "bold"),
            command=self._save
        )
        save_btn.pack(side="left", padx=(0, 8))

        cancel_btn = ctk.CTkButton(
            footer, text="CANCELAR", fg_color="transparent",
            hover_color="#F3F4F6", text_color=self.colors["text_secondary"],
            border_width=1, border_color=self.colors["border"],
            height=44, width=125, corner_radius=5,
            font=font("button_large"),
            command=self._cancel
        )
        cancel_btn.pack(side="left")

    # ==================== CARREGAMENTO DE DADOS ====================
    def _load_clinic_data(self):
        try:
            from config.database import get_connection
            import json

            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                print(f"[DEBUG] Carregando dados da clínica ID: {self.clinica_id}")

                cursor.execute("""
                    SELECT nome, cnpj, email, telefone, logo, fotos
                    FROM odontoPro_clinica
                    WHERE id = %s
                """, (self.clinica_id,))

                result = cursor.fetchone()
                if result:
                    fotos = []
                    if len(result) > 5 and result[5]:
                        try:
                            fotos = json.loads(result[5]) if isinstance(result[5], str) else result[5]
                        except Exception:
                            fotos = []

                    data = {
                        "nome": result[0] or "",
                        "cnpj": result[1] or "",
                        "email": result[2] or "",
                        "telefone": result[3] or "",
                        "logo": result[4] or "",
                        "photos": fotos
                    }
                    print(f"[DEBUG] Dados carregados: {data}")
                    return data

                print("[DEBUG] Nenhum resultado encontrado para clinica_id:", self.clinica_id)
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
        try:
            from config.database import get_connection

            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

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
        try:
            from config.database import get_connection

            if self.tipo_usuario not in ["gerenciamento", "dentista"]:
                return None

            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

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
        file_path = filedialog.askopenfilename(
            title="Selecionar logo da clínica",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.logo_upload_btn.configure(text="⏳ Carregando...", state="disabled")
            self.after(100, lambda: self._finish_load_clinic_logo(file_path))

    def _finish_load_clinic_logo(self, file_path):
        self.images["logo"] = file_path
        ImagePreview.create_circular_preview(self.logo_canvas, file_path, 140, "LOGO")

        self.logo_upload_btn.configure(
            text="✓ Logo carregada",
            fg_color=self.colors["success"],
            hover_color="#0f9c6d",
            state="normal"
        )

    def _setup_clinic_photos_ui(self):
        for widget in self.clinic_photos_container.winfo_children():
            widget.destroy()

        main_wrap = ctk.CTkFrame(self.clinic_photos_container, fg_color="transparent")
        main_wrap.pack(fill="both", expand=True, padx=18, pady=18)

        preview_frame = ctk.CTkFrame(
            main_wrap,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"]
        )
        preview_frame.pack(fill="both", expand=True, pady=(0, 14))

        self.clinic_photo_canvas = tk.Canvas(
            preview_frame,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        self.clinic_photo_canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.clinic_photo_canvas.bind("<Configure>", self._on_canvas_resize)

        footer = ctk.CTkFrame(main_wrap, fg_color="transparent")
        footer.pack(fill="x")

        nav_frame = ctk.CTkFrame(footer, fg_color="transparent")
        nav_frame.pack(side="left")

        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=42,
            height=42,
            font=font("subtitle", "bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            state="disabled",
            corner_radius=8,
            command=self._previous_clinic_photo
        )
        self.prev_btn.pack(side="left", padx=(0, 6))

        self.photo_counter_label = ctk.CTkLabel(
            nav_frame,
            text="0/0",
            font=font("text"),
            text_color=self.colors["text_secondary"]
        )
        self.photo_counter_label.pack(side="left", padx=10)

        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=42,
            height=42,
            font=font("subtitle", "bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            state="disabled",
            corner_radius=8,
            command=self._next_clinic_photo
        )
        self.next_btn.pack(side="left", padx=(6, 0))

        self.add_photo_btn = ctk.CTkButton(
            footer,
            text="+ Adicionar Foto",
            width=170,
            height=42,
            font=font("text"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            corner_radius=8,
            command=self._add_clinic_photo
        )
        self.add_photo_btn.pack(side="right")

        self._update_clinic_photos_display()

    def _update_clinic_photos_display(self, canvas_width=None, canvas_height=None):
        if canvas_width is None:
            canvas_width = 400
        if canvas_height is None:
            canvas_height = 240

        if not self.clinic_photos:
            ImagePreview.create_rectangular_preview(
                self.clinic_photo_canvas,
                None,
                canvas_width,
                canvas_height,
                "SEM FOTOS\nCLIQUE EM + PARA ADICIONAR"
            )
            self.photo_counter_label.configure(text="0/0")
            self.prev_btn.configure(state="disabled")
            self.next_btn.configure(state="disabled")
        else:
            current_photo = self.clinic_photos[self.current_photo_index]
            ImagePreview.create_rectangular_preview(
                self.clinic_photo_canvas,
                current_photo,
                canvas_width,
                canvas_height,
                "FOTO"
            )

            self.photo_counter_label.configure(
                text=f"{self.current_photo_index + 1}/{len(self.clinic_photos)}"
            )

            self.prev_btn.configure(
                state="normal" if self.current_photo_index > 0 else "disabled"
            )
            self.next_btn.configure(
                state="normal" if self.current_photo_index < len(self.clinic_photos) - 1 else "disabled"
            )

    def _next_clinic_photo(self):
        if self.current_photo_index < len(self.clinic_photos) - 1:
            self.current_photo_index += 1
            self._update_clinic_photos_display()

    def _previous_clinic_photo(self):
        if self.current_photo_index > 0:
            self.current_photo_index -= 1
            self._update_clinic_photos_display()

    def _add_clinic_photo(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar foto da clínica",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.clinic_photos.append(file_path)
            self.current_photo_index = len(self.clinic_photos) - 1
            self._update_clinic_photos_display()

    def _remove_current_clinic_photo(self):
        if self.clinic_photos and 0 <= self.current_photo_index < len(self.clinic_photos):
            result = messagebox.askyesno(
                "Confirmar Remoção",
                "Tem certeza que deseja remover esta foto?"
            )
            if result:
                del self.clinic_photos[self.current_photo_index]
                if self.current_photo_index >= len(self.clinic_photos):
                    self.current_photo_index = max(0, len(self.clinic_photos) - 1)
                self._update_clinic_photos_display()

    def _on_canvas_resize(self, event):
        self._update_clinic_photos_display(event.width, event.height)

    def _change_avatar(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar foto de perfil",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.images["avatar"] = file_path

            profile_data = self._load_user_profile_data()
            nome = profile_data.get("nome", "") if profile_data else ""
            placeholder_text = ImagePreview._get_initials(nome) if nome else "GG"
            ImagePreview.create_circular_preview(self.avatar_canvas, file_path, 140, placeholder_text)

            messagebox.showinfo("Sucesso", "Foto de perfil atualizada com sucesso!")

    def _cancel(self):
        result = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar? Todas as alterações não salvas serão perdidas."
        )
        if result:
            pass

    def _save(self):
        all_valid = True

        if self.current_tab == "Perfil":
            for _, input_widget in self.profile_entries.items():
                if not input_widget._validate():
                    all_valid = False

        if self.current_tab == "Minha Clínica" and self.tipo_usuario == "clinica":
            for _, input_widget in self.clinic_entries.items():
                if not input_widget._validate():
                    all_valid = False

        if all_valid:
            if self.tipo_usuario == "clinica" and self.clinica_id:
                self._save_clinic_data()
            else:
                messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

    def _save_clinic_data(self):
        """Salva dados da clínica e endereço no banco de dados"""
        try:
            from config.database import get_connection
            import shutil
            import json
            from datetime import datetime

            conn = None
            cursor = None

            try:
                conn = get_connection()
                cursor = conn.cursor()

                nome = self.clinic_entries["Nome da Clínica"].get().strip()
                cnpj = self.clinic_entries["CNPJ"].get().strip()
                email = self.clinic_entries["E-mail Clínica"].get().strip()
                telefone = self.clinic_entries["Telefone"].get().strip()

                cursor.execute("""
                    UPDATE odontoPro_clinica
                    SET nome = %s, cnpj = %s, email = %s, telefone = %s
                    WHERE id = %s
                """, (nome, cnpj, email, telefone, self.clinica_id))

                if "logo" in self.images:
                    logo_path = self.images["logo"]
                    upload_dir = os.path.join(os.path.dirname(__file__), "../assets/clinicas/logo")
                    os.makedirs(upload_dir, exist_ok=True)

                    extensao = os.path.splitext(logo_path)[1] or ".png"
                    filename = f"clinica_{self.clinica_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extensao}"
                    dest_path = os.path.join(upload_dir, filename)
                    shutil.copy(logo_path, dest_path)

                    cursor.execute("""
                        UPDATE odontoPro_clinica
                        SET logo = %s
                        WHERE id = %s
                    """, (dest_path, self.clinica_id))

                if hasattr(self, "clinic_photos"):
                    saved_photos = []
                    upload_dir = os.path.join(os.path.dirname(__file__), "../assets/clinicas/fotos")
                    os.makedirs(upload_dir, exist_ok=True)

                    for i, photo_path in enumerate(self.clinic_photos):
                        if os.path.exists(photo_path):
                            if not os.path.abspath(photo_path).startswith(os.path.abspath(upload_dir)):
                                extensao = os.path.splitext(photo_path)[1] or ".jpg"
                                filename = f"clinica_{self.clinica_id}_foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}{extensao}"
                                dest_path = os.path.join(upload_dir, filename)
                                shutil.copy(photo_path, dest_path)
                                saved_photos.append(dest_path)
                            else:
                                saved_photos.append(photo_path)

                    cursor.execute("""
                        UPDATE odontoPro_clinica
                        SET fotos = %s
                        WHERE id = %s
                    """, (json.dumps(saved_photos), self.clinica_id))

                # Salvar endereço
                if self.address_entries:
                    rua = self.address_entries["Rua"].get().strip()
                    numero = self.address_entries["Número"].get().strip()
                    bairro = self.address_entries["Bairro"].get().strip()
                    cidade = self.address_entries["Cidade"].get().strip()
                    estado = self.address_entries["Estado"].get().strip()
                    cep = self.address_entries["CEP"].get().strip()

                    cursor.execute("""
                        SELECT endereco_id
                        FROM odontoPro_clinica
                        WHERE id = %s
                    """, (self.clinica_id,))
                    result = cursor.fetchone()

                    endereco_id = result[0] if result and result[0] else None

                    if endereco_id:
                        cursor.execute("""
                            UPDATE odontoPro_endereco
                            SET rua = %s, numero = %s, bairro = %s, cidade = %s, estado = %s, cep = %s
                            WHERE id = %s
                        """, (rua, numero, bairro, cidade, estado, cep, endereco_id))
                    else:
                        cursor.execute("""
                            INSERT INTO odontoPro_endereco (rua, numero, bairro, cidade, estado, cep)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (rua, numero, bairro, cidade, estado, cep))

                        novo_endereco_id = cursor.lastrowid

                        cursor.execute("""
                            UPDATE odontoPro_clinica
                            SET endereco_id = %s
                            WHERE id = %s
                        """, (novo_endereco_id, self.clinica_id))

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
