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
        label_frame.pack(fill="x", pady=(0, 4))
        
        lbl = ctk.CTkLabel(
            label_frame,
            text=label,
            font=font("small", "bold"),
            text_color="#6B7280"
        )
        lbl.pack(side="left")
        
        if required:
            required_lbl = ctk.CTkLabel(
                label_frame,
                text="*",
                font=font("small", "bold"),
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
                font=font("text"),
                width=30
            )
            icon_lbl.pack(side="left", padx=(0, 5))
        
        self.entry = ctk.CTkEntry(
            input_container,
            placeholder_text=placeholder,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color="#E5E7EB",
            fg_color="#F9FAFB",
            text_color="#111827",
            placeholder_text_color="#9CA3AF",
            font=font("text"),
            **kwargs
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Bind para validação
        self.entry.bind("<FocusOut>", self._validate)
    
    def _validate(self, event=None):
        """Valida campo obrigatório"""
        if self.required and not self.entry.get().strip():
            self.entry.configure(border_color="#EF4444", border_width=2)
            return False
        else:
            self.entry.configure(border_color="#E5E7EB", border_width=1)
            return True
    
    def get(self):
        return self.entry.get()
    
    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

class ModernCard(ctk.CTkFrame):
    """Card com bordas arredondadas"""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB",
            **kwargs
        )

class Configuracoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Configurações")

        # Paleta de cores ajustada para o padrão do Painel
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
            "input_bg": "#F9FAFB"
        }

        self.current_tab = "Perfil"
        self.tab_buttons = {}
        self.images = {}
        self.loading_states = {}

        self.setup_ui()

    def setup_ui(self):
        """Configura a interface principal"""
        
        # Container externo igual ao do Cadastro (padx=120)
        self.container_outer = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent",
            corner_radius=20
        )
        self.container_outer.pack(fill="both", expand=True, padx=120, pady=(6, 8))

        # Container interno (fundo branco)
        self.container_conteudo = ctk.CTkFrame(
            self.container_outer,
            fg_color=self.colors["bg_card"],
            corner_radius=12
        )
        self.container_conteudo.pack(fill="both", expand=True, padx=2, pady=(5, 1))

        # Header com padding reduzido
        header_frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent", height=20)
        header_frame.pack(fill="x", padx=60, pady=(10, 0))

        # Tabs
        self._build_tabs(self.container_conteudo)

        # Área de conteúdo - TODOS OS ELEMENTOS AGORA COMEÇAM À ESQUERDA
        self.content_area = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=60, pady=(15, 10))
        
        # Força o alinhamento à esquerda para todos os conteúdos futuros
        self.content_area.pack_configure(anchor="w")

        # Footer
        self._build_footer(self.container_conteudo)

        # Render inicial
        self.switch_tab(self.current_tab)

    def _build_tabs(self, parent):
        """Tabs com design moderno"""
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        tab_frame.pack(fill="x", padx=60, pady=(0, 5), anchor="w")  # ✅ Alinhado à esquerda

        tabs = [
            {"name": "Perfil", "icon": "👤"},
            {"name": "Segurança", "icon": "🔒"},
            {"name": "Minha Clínica", "icon": "🏥"}
        ]
        
        # Container para os botões - alinhado à esquerda
        self.tab_container = ctk.CTkFrame(tab_frame, fg_color="transparent")
        self.tab_container.pack(side="left", anchor="w")

        for tab in tabs:
            tab_name = tab["name"]
            tab_icon = tab["icon"]
            
            btn_frame = ctk.CTkFrame(self.tab_container, fg_color="transparent")
            btn_frame.pack(side="left", padx=(0, 15))
            
            # Ícone
            icon_lbl = ctk.CTkLabel(
                btn_frame,
                text=tab_icon,
                font=font("subtitle"),
                text_color=self.colors["text_secondary"],
                anchor="w"  # ✅ Alinhado à esquerda
            )
            icon_lbl.pack(side="left", padx=(0, 8))
            
            # Botão
            btn = ctk.CTkButton(
                btn_frame,
                text=tab_name,
                fg_color="transparent",
                hover_color=self.colors["accent_light"],
                font=font(14, "bold"),
                text_color=self.colors["text_secondary"],
                anchor="w",  # ✅ Texto alinhado à esquerda
                command=lambda t=tab_name: self.switch_tab(t)
            )
            btn.pack(side="left")
            
            self.tab_buttons[tab_name] = {"btn": btn, "icon": icon_lbl}

        # Underline animado
        self.underline = ctk.CTkFrame(
            tab_frame,
            height=3,
            width=90,
            fg_color=self.colors["accent"],
            corner_radius=2
        )
        self.underline.place(x=60, y=32)

    def switch_tab(self, tab_name):
        """Muda a aba com animação"""
        self.current_tab = tab_name
        tab_order = ["Perfil", "Segurança", "Minha Clínica"]
        
        # Atualiza cores dos botões
        for name, components in self.tab_buttons.items():
            if name == tab_name:
                components["btn"].configure(text_color=self.colors["accent"])
                components["icon"].configure(text_color=self.colors["accent"])
                
                # Move underline
                idx = tab_order.index(name)
                x_pos = 60 + (idx * 115)
                self.underline.place(x=x_pos, y=32)
                self.underline.configure(width=90)
            else:
                components["btn"].configure(text_color=self.colors["text_secondary"])
                components["icon"].configure(text_color=self.colors["text_secondary"])

        # Limpa conteúdo
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Renderiza aba selecionada
        render_methods = {
            "Perfil": self._render_profile,
            "Segurança": self._render_security,
            "Minha Clínica": self._render_preferences
        }
        
        if tab_name in render_methods:
            render_methods[tab_name](self.content_area)

    # ==================== SEGURANÇA ====================
    def _render_security(self, parent):
        """Tela de segurança - TODOS OS ELEMENTOS ALINHADOS À ESQUERDA"""
        
        # Card de senha
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", pady=(20, 40), anchor="w")  # ✅ Alinhado à esquerda
        
        # Header
        header = ctk.CTkFrame(password_frame, fg_color="transparent")
        header.pack(anchor="w", pady=(0, 40))  # ✅ Já estava anchor="w"
        
        ctk.CTkLabel(
            header,
            text="🔐",
            font=font("title"),
            text_color=self.colors["accent"]
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header,
            text="Alterar Senha",
            font=font("subtitle", "bold"),
            text_color=self.colors["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            header,
            text="(mínimo 8 caracteres)",
            font=font("small"),
            text_color=self.colors["text_muted"]
        ).pack(side="left", padx=(10, 0))

        # Formulário
        form_frame = ctk.CTkFrame(password_frame, fg_color="transparent")
        form_frame.pack(fill="x", anchor="w")  # ✅ Alinhado à esquerda

        # Senha atual
        current_pwd = ModernInput(
            form_frame,
            label="Senha Atual",
            placeholder="Digite sua senha atual",
            icon="🔑",
            required=True
        )
        current_pwd.pack(fill="x", pady=(0, 40), anchor="w")  # ✅ Alinhado à esquerda
        current_pwd.entry.configure(show="•")

        # Nova senha
        new_pwd = ModernInput(
            form_frame,
            label="Nova Senha",
            placeholder="Digite a nova senha",
            icon="🔒",
            required=True
        )
        new_pwd.pack(fill="x", pady=(0, 40), anchor="w")  # ✅ Alinhado à esquerda
        new_pwd.entry.configure(show="•")

        # Confirmar senha
        confirm_pwd = ModernInput(
            form_frame,
            label="Confirmar Nova Senha",
            placeholder="Digite novamente a nova senha",
            icon="✓",
            required=True
        )
        confirm_pwd.pack(fill="x", pady=(0, 40), anchor="w")  # ✅ Alinhado à esquerda
        confirm_pwd.entry.configure(show="•")

        # Barra de força da senha
        strength_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        strength_frame.pack(fill="x", pady=(10, 0), anchor="w")  # ✅ Alinhado à esquerda
        
        ctk.CTkLabel(
            strength_frame,
            text="Força da senha:",
            font=font("small"),
            text_color=self.colors["text_secondary"]
        ).pack(side="left")
        
        self.strength_bar = ctk.CTkProgressBar(
            strength_frame,
            width=200,
            height=6,
            corner_radius=3,
            progress_color=self.colors["accent"]
        )
        self.strength_bar.pack(side="left", padx=(10, 0))
        self.strength_bar.set(0)
        
        # Bind para verificar força da senha
        new_pwd.entry.bind("<KeyRelease>", lambda e: self._check_password_strength(new_pwd.entry.get()))

    def _check_password_strength(self, password):
        """Verifica força da senha"""
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
            self.strength_bar.configure(progress_color="#EF4444")
        elif strength < 0.75:
            self.strength_bar.configure(progress_color="#F59E0B")
        else:
            self.strength_bar.configure(progress_color="#10B981")

    # ==================== PREFERÊNCIAS ====================
    def _render_preferences(self, parent):
        """Tela de preferências"""
        
        # Tabs de preferências
        sub_tabs = ["Geral", "Serviços", "Descrição"]
        self.sub_tab_buttons = {}
        
        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", pady=(0, 10), anchor="w")  # ✅ Alinhado à esquerda
        
        for tab in sub_tabs:
            btn = ctk.CTkButton(
                tab_frame,
                text=tab,
                fg_color="transparent",
                hover_color=self.colors["accent_light"],
                font=font("text"),
                text_color=self.colors["text_secondary"],
                anchor="w",  # ✅ Texto alinhado à esquerda
                command=lambda t=tab.lower(): self._switch_sub_tab(parent, t)
            )
            btn.pack(side="left", padx=(0, 25))
            self.sub_tab_buttons[tab.lower()] = btn
        
        # Linha divisória
        divider = ctk.CTkFrame(parent, height=1, fg_color=self.colors["border"])
        divider.pack(fill="x", pady=(0, 15))
        
        self.sub_tab_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.sub_tab_content.pack(fill="both", expand=True, anchor="w")  # ✅ Alinhado à esquerda
        
        # Inicia com a primeira aba
        self._switch_sub_tab(parent, "geral")

    def _switch_sub_tab(self, parent, tab_name):
        """Muda entre sub-abas"""
        # Atualiza cores dos botões
        for name, btn in self.sub_tab_buttons.items():
            if name == tab_name:
                btn.configure(text_color=self.colors["accent"])
            else:
                btn.configure(text_color=self.colors["text_secondary"])
        
        # Limpa conteúdo
        for widget in self.sub_tab_content.winfo_children():
            widget.destroy()
        
        # Renderiza tab selecionada
        if tab_name == "geral":
            self._render_preferences_geral(self.sub_tab_content)
        elif tab_name == "serviços":
            self._render_preferences_services(self.sub_tab_content)
        elif tab_name == "descrição":
            self._render_preferences_description(self.sub_tab_content)

    def _render_preferences_geral(self, parent):
        """Configurações gerais da clínica - BARRA DE ROLAGEM CINZA"""
        
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#D1D5DB",  # ✅ ALTERADO: cinza claro
            scrollbar_button_hover_color="#9CA3AF"  # ✅ ALTERADO: cinza médio para hover
        )
        scroll.pack(fill="both", expand=True, anchor="w")  # ✅ Alinhado à esquerda

        # Seção de fotos
        photos_section = ctk.CTkFrame(scroll, fg_color="transparent")
        photos_section.pack(fill="x", pady=(0, 25), anchor="w")  # ✅ Alinhado à esquerda

        ctk.CTkLabel(
            photos_section,
            text="📸 Fotos da Clínica",
            font=font("text", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"  # ✅ Texto alinhado à esquerda
        ).pack(anchor="w", pady=(0, 12))

        # Foto principal
        ctk.CTkLabel(
            photos_section,
            text="Foto Principal da Fachada",
            font=font("small"),
            text_color=self.colors["text_primary"],
            anchor="w"  # ✅ Texto alinhado à esquerda
        ).pack(anchor="w")

        self.main_photo_container = ctk.CTkFrame(
            photos_section,
            fg_color="#F9FAFB",
            corner_radius=10,
            height=150,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.main_photo_container.pack(fill="x", pady=(8, 20), anchor="w")  # ✅ Alinhado à esquerda
        self.main_photo_container.pack_propagate(False)

        self.main_photo_btn = ctk.CTkButton(
            self.main_photo_container,
            text="📷 Carregar Foto da Fachada",
            font=font("text"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            height=40,
            corner_radius=8,
            anchor="w",  # ✅ Texto alinhado à esquerda
            command=self._load_main_photo
        )
        self.main_photo_btn.pack(expand=True)

        # Fotos adicionais
        ctk.CTkLabel(
            photos_section,
            text="Fotos Internas (até 5)",
            font=font("small"),
            text_color=self.colors["text_primary"],
            anchor="w"  # ✅ Texto alinhado à esquerda
        ).pack(anchor="w")

        grid_frame = ctk.CTkFrame(photos_section, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(8, 20), anchor="w")  # ✅ Alinhado à esquerda

        self.photo_buttons = {}
        for i in range(5):
            btn = ctk.CTkButton(
                grid_frame,
                text=f"📷 Foto {i+1}",
                width=90,
                height=90,
                font=font("small"),
                fg_color="#F9FAFB",
                hover_color=self.colors["accent_light"],
                text_color=self.colors["text_secondary"],
                corner_radius=8,
                border_width=1,
                border_color=self.colors["border"],
                anchor="w",  # ✅ Texto alinhado à esquerda
                command=lambda idx=i: self._load_photo(idx)
            )
            btn.grid(row=0, column=i, padx=5)
            self.photo_buttons[i] = btn

        # Seção de endereço
        address_section = ctk.CTkFrame(scroll, fg_color="transparent")
        address_section.pack(fill="x", pady=(0, 10), anchor="w")  # ✅ Alinhado à esquerda

        ctk.CTkLabel(
            address_section,
            text="📍 Endereço da Clínica",
            font=font("text", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"  # ✅ Texto alinhado à esquerda
        ).pack(anchor="w", pady=(0, 12))

        # Campos de endereço em grid
        address_form = ctk.CTkFrame(address_section, fg_color="transparent")
        address_form.pack(fill="x", anchor="w")  # ✅ Alinhado à esquerda
        address_form.grid_columnconfigure((0, 1), weight=1)

        fields = [
            {"label": "Rua", "col": 0, "row": 0, "placeholder": "Nome da rua"},
            {"label": "Número", "col": 1, "row": 0, "placeholder": "123"},
            {"label": "Bairro", "col": 0, "row": 1, "placeholder": "Nome do bairro"},
            {"label": "Cidade", "col": 1, "row": 1, "placeholder": "Nome da cidade"},
            {"label": "Estado", "col": 0, "row": 2, "placeholder": "UF"},
            {"label": "CEP", "col": 1, "row": 2, "placeholder": "00000-000"}
        ]

        self.address_entries = {}
        for field in fields:
            lbl = ctk.CTkLabel(
                address_form,
                text=field["label"],
                font=font("small"),
                text_color=self.colors["text_secondary"],
                anchor="w"  # ✅ Texto alinhado à esquerda
            )
            lbl.grid(row=field["row"]*2, column=field["col"], sticky="w", pady=(8, 2))
            
            entry = ctk.CTkEntry(
                address_form,
                placeholder_text=field["placeholder"],
                height=40,
                corner_radius=8,
                border_width=1,
                border_color=self.colors["border"],
                fg_color="#F9FAFB",
                font=font("text")
            )
            entry.grid(row=field["row"]*2 + 1, column=field["col"], sticky="ew", padx=(0, 10))

    def _render_preferences_services(self, parent):
        """Serviços oferecidos"""
        
        # Se necessário adicionar scroll futuramente
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#D1D5DB",  # ✅ cinza claro
            scrollbar_button_hover_color="#9CA3AF"  # ✅ cinza médio
        )
        scroll.pack(fill="both", expand=True, anchor="w")
        
        ctk.CTkLabel(
            scroll,
            text="🩺 Serviços Oferecidos",
            font=font("subtitle", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 15))

        # Lista de serviços sugeridos
        suggestions_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        suggestions_frame.pack(fill="x", pady=(0, 15), anchor="w")

        ctk.CTkLabel(
            suggestions_frame,
            text="Sugestões de serviços:",
            font=font("small"),
            text_color=self.colors["text_secondary"],
            anchor="w"
        ).pack(anchor="w")

        chips_frame = ctk.CTkFrame(suggestions_frame, fg_color="transparent")
        chips_frame.pack(fill="x", pady=(8, 0), anchor="w")

        suggestions = ["Limpeza", "Clareamento", "Implantes", "Aparelhos", "Extração", "Canal"]
        for suggestion in suggestions:
            chip = ctk.CTkButton(
                chips_frame,
                text=suggestion,
                fg_color=self.colors["accent_light"],
                hover_color=self.colors["accent"],
                text_color=self.colors["accent_hover"],
                height=30,
                corner_radius=15,
                font=font("small"),
                border_width=0,
                anchor="w",
                command=lambda s=suggestion: self._add_service(s)
            )
            chip.pack(side="left", padx=(0, 8))

        # Área de texto
        self.services_text = ctk.CTkTextbox(
            scroll,
            height=180,
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            fg_color="#F9FAFB",
            font=font("text")
        )
        self.services_text.pack(fill="both", expand=True, anchor="w")
        self.services_text.insert("1.0", "• Limpeza profissional\n• Clareamento dental\n• Implantes\n• Aparelhos ortodônticos")

    def _render_preferences_description(self, parent):
        """Descrição da clínica"""
        
        # Se necessário adicionar scroll futuramente
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#D1D5DB",  # ✅ cinza claro
            scrollbar_button_hover_color="#9CA3AF"  # ✅ cinza médio
        )
        scroll.pack(fill="both", expand=True, anchor="w")
        
        ctk.CTkLabel(
            scroll,
            text="📝 Sobre a Clínica",
            font=font("subtitle", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 15))

        # Dicas
        tips_frame = ctk.CTkFrame(
            scroll,
            fg_color=self.colors["accent_light"],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"]
        )
        tips_frame.pack(fill="x", pady=(0, 15), anchor="w")

        ctk.CTkLabel(
            tips_frame,
            text="💡 Dicas para uma boa descrição:",
            font=font("small", "bold"),
            text_color=self.colors["accent_hover"],
            anchor="w"
        ).pack(anchor="w", padx=10, pady=(8, 5))

        tips = [
            "• Fale sobre sua missão e valores",
            "• Destaque seus diferenciais",
            "• Mencione a equipe e estrutura",
            "• Inclua seu horário de funcionamento"
        ]

        for tip in tips:
            ctk.CTkLabel(
                tips_frame,
                text=tip,
                font=font("small"),
                text_color=self.colors["text_secondary"],
                anchor="w"
            ).pack(anchor="w", padx=10, pady=2)

        # Área de texto
        self.description_text = ctk.CTkTextbox(
            scroll,
            height=280,
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            fg_color="#F9FAFB",
            font=font("text")
        )
        self.description_text.pack(fill="both", expand=True, anchor="w")
        self.description_text.insert("1.0", "Bem-vindo à nossa clínica! Somos uma equipe dedicada a proporcionar o melhor cuidado para seu sorriso...")

    # ==================== PERFIL (ALTERADO - ESPAÇAMENTOS AUMENTADOS) ====================
    def _render_profile(self, parent):
        """Tela de perfil do usuário"""
        
        # Layout em duas colunas
        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)

        # Avatar
        self._render_avatar(parent)

        # Formulário
        self._render_profile_form(parent)

    def _render_avatar(self, parent):
        """Seção de avatar - ESPAÇAMENTOS AUMENTADOS"""
        avatar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        avatar_frame.grid(row=0, column=0, sticky="nw", padx=(0, 25))

        ctk.CTkLabel(
            avatar_frame,
            text="Foto de Perfil",
            font=font("text", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 20))  # ⬆️ AUMENTADO de 12 para 20

        # Container do avatar
        avatar_container = ctk.CTkFrame(
            avatar_frame,
            fg_color="transparent",
            width=140,
            height=140
        )
        avatar_container.pack(anchor="w", pady=(0, 25))  # ➕ ADICIONADO pady inferior de 25
        avatar_container.pack_propagate(False)

        # Canvas para avatar
        self.avatar_canvas = tk.Canvas(
            avatar_container,
            width=140,
            height=140,
            bg="white",
            highlightthickness=0,
            bd=0
        )
        self.avatar_canvas.pack()

        # Desenha círculo
        self.avatar_canvas.create_oval(
            5, 5, 135, 135,
            fill=self.colors["accent_light"],
            outline=self.colors["accent"],
            width=2
        )

        # Iniciais
        self.avatar_canvas.create_text(
            70, 70,
            text="GG",
            font=("Arial", 36, "bold"),
            fill=self.colors["accent"]
        )

        # Botão de upload
        upload_btn = ctk.CTkButton(
            avatar_frame,
            text="Alterar foto",
            fg_color="transparent",
            hover_color=self.colors["accent_light"],
            text_color=self.colors["accent"],
            border_width=1,
            border_color=self.colors["accent"],
            height=35,
            corner_radius=8,
            font=font("text"),
            anchor="w",
            command=self._change_avatar
        )
        upload_btn.pack(anchor="w")  # ✅ REMOVIDO pady=12 para não criar espaço extra

    def _render_profile_form(self, parent):
        """Formulário de perfil - ESPAÇAMENTOS AUMENTADOS"""
        form_frame = ctk.CTkFrame(parent, fg_color="transparent")
        form_frame.grid(row=0, column=1, sticky="nsew")
        form_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            form_frame,
            text="Informações Pessoais",
            font=font("text", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 25))  # ⬆️ AUMENTADO de 12 para 25

        # Campos do formulário
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
                form_frame,
                label=field["label"],
                placeholder=field["placeholder"],
                icon=field["icon"],
                required=field.get("required", False)
            )
            input_widget.grid(
                row=field["row"]*2,
                column=field["col"],
                sticky="ew",
                padx=(0 if field["col"] == 0 else 10, 10 if field["col"] == 0 else 0),
                pady=(0, 25)  # ⬆️ AUMENTADO de 8 para 25
            )
            self.profile_entries[field["label"]] = input_widget

    # ==================== FOOTER ====================
    def _build_footer(self, parent):
        """Rodapé com botões de ação"""
        footer = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        footer.pack(fill="x", side="bottom", padx=60, pady=(10, 15))

        # Botões - alinhados à direita (mantido)
        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right")

        # Botão cancelar
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color=self.colors["text_secondary"],
            border_width=1,
            border_color=self.colors["border"],
            height=38,
            width=95,
            corner_radius=8,
            font=font("text"),
            anchor="center",  # ✅ Centralizado (padrão para botões)
            command=self._cancel
        )
        cancel_btn.pack(side="left", padx=(0, 8))

        # Botão salvar
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Salvar alterações",
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="white",
            height=38,
            width=135,
            corner_radius=8,
            font=font("text", "bold"),
            anchor="center",  # ✅ Centralizado (padrão para botões)
            command=self._save
        )
        save_btn.pack(side="left")

    # ==================== HELPERS ====================
    def _load_main_photo(self):
        """Carrega foto principal"""
        file_path = filedialog.askopenfilename(
            title="Selecionar foto da fachada",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.main_photo_btn.configure(text="⏳ Carregando...", state="disabled")
            self.after(100, lambda: self._finish_load_main_photo(file_path))

    def _finish_load_main_photo(self, file_path):
        """Finaliza carregamento da foto"""
        self.images['main'] = file_path
        self.main_photo_btn.configure(
            text="✓ Foto carregada",
            fg_color=self.colors["success"],
            state="normal"
        )

    def _load_photo(self, index):
        """Carrega foto interna"""
        file_path = filedialog.askopenfilename(
            title=f"Selecionar foto {index + 1}",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.images[f'photo_{index}'] = file_path
            self.photo_buttons[index].configure(
                text="✓ Carregada",
                fg_color=self.colors["success"],
                text_color="white"
            )

    def _add_service(self, service):
        """Adiciona serviço à lista"""
        current_text = self.services_text.get("1.0", "end-1c")
        if service not in current_text:
            if current_text.strip():
                self.services_text.insert("end", f"\n• {service}")
            else:
                self.services_text.insert("1.0", f"• {service}")

    def _change_avatar(self):
        """Altera foto do avatar"""
        file_path = filedialog.askopenfilename(
            title="Selecionar foto de perfil",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            messagebox.showinfo("Sucesso", "Foto de perfil atualizada com sucesso!")

    def _cancel(self):
        """Cancela as alterações"""
        result = messagebox.askyesno(
            "Cancelar",
            "Tem certeza que deseja cancelar? Todas as alterações não salvas serão perdidas."
        )
        if result:
            # Recarrega os dados originais
            pass

    def _save(self):
        """Salva todas as alterações"""
        all_valid = True
        
        if self.current_tab == "Perfil":
            for field_name, input_widget in self.profile_entries.items():
                if not input_widget._validate():
                    all_valid = False
        
        if all_valid:
            messagebox.showinfo(
                "Sucesso",
                "Configurações salvas com sucesso!"
            )
        else:
            messagebox.showerror(
                "Erro",
                "Por favor, preencha todos os campos obrigatórios."
            )