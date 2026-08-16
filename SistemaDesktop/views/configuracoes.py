import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from .base import BaseScreen, ActionButtons
from .theme import font, ICON_SIZE, COLORS, toggle_dark_mode, get_dark_mode, INNER_CARD_BORDER, INNER_CARD_RADIUS
from services.endereco_service import EnderecoService
from services.cloudinary_service import upload_image_to_cloudinary
import os
import time
import requests
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw
import re


class ImagePreview:
    """Classe utilitária para gerenciar previews de imagens"""

    @staticmethod
    def _load_image(image_path):
        if not image_path:
            return None

        try:
            if isinstance(image_path, str) and image_path.lower().startswith(("http://", "https://")):
                response = requests.get(image_path, timeout=15)
                response.raise_for_status()
                return Image.open(BytesIO(response.content))

            if os.path.exists(image_path):
                return Image.open(image_path)

        except Exception as e:
            print(f"Erro ao carregar imagem '{image_path}': {e}")

        return None

    @staticmethod
    def create_circular_preview(canvas, image_path, size=140, placeholder_text="IMG"):
        """Cria preview circular de imagem em um canvas"""
        canvas.delete("all")

        img = ImagePreview._load_image(image_path)
        if img:
            try:
                img = img.convert("RGBA")
                img = img.resize((size - 10, size - 10), Image.Resampling.LANCZOS)

                mask = Image.new("L", (size - 10, size - 10), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size - 10, size - 10), fill=255)

                img.putalpha(mask)
                photo = ImageTk.PhotoImage(img)

                canvas.create_image(size // 2, size // 2, image=photo)
                canvas.image = photo
                canvas.create_oval(5, 5, size - 5, size - 5, outline=COLORS["primary"], width=2)
                return
            except Exception as e:
                print(f"Erro ao processar preview de imagem: {e}")

        ImagePreview._draw_placeholder_circle(canvas, size, placeholder_text)

    @staticmethod
    def create_rectangular_preview(canvas, image_path, width=300, height=150, placeholder_text="IMG"):
        """Cria preview retangular de imagem em um canvas"""
        canvas.delete("all")

        img = ImagePreview._load_image(image_path)
        if img:
            try:
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
                return
            except Exception as e:
                print(f"Erro ao processar preview de imagem: {e}")

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
    """Componente de input padronizado com label em cima e validação"""
    def __init__(self, parent, label="", placeholder="", icon=None, required=False, read_only=False, mask=None, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.required = required
        self.read_only = read_only
        self.mask = mask
        self.applying_mask = False  # Flag para evitar loops de aplicação de máscara

        # Label (em cima)
        label_frame = ctk.CTkFrame(self, fg_color="transparent")
        label_frame.pack(fill="x", pady=(0, 2))
        
        # Se há ícone, adicionar padding esquerdo ao label para alinhamento com o entry
        label_padx = (35, 0) if icon else (0, 0)
        lbl = ctk.CTkLabel(label_frame, text=label, font=font("text"), text_color=COLORS["text_secondary"])
        lbl.pack(side="left", padx=label_padx)
        
        if required:
            required_lbl = ctk.CTkLabel(label_frame, text="*", font=font("text", "bold"), text_color=COLORS["danger"])
            required_lbl.pack(side="left", padx=(2, 0))

        # Container do input
        input_container = ctk.CTkFrame(self, fg_color="transparent")
        input_container.pack(fill="x", pady=(2, 0))
        if icon:
            icon_lbl = ctk.CTkLabel(input_container, text=icon, font=font("text"), width=30)
            icon_lbl.pack(side="left", padx=(0, 5))

        self.entry = ctk.CTkEntry(
            input_container,
            placeholder_text=placeholder,
            height=44,
            corner_radius=8,
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

        # Se tem máscara, configurar
        if self.mask:
            self._setup_mask()

        # Se é read-only, bloquear modificações
        if self.read_only:
            self._setup_read_only()

    def _setup_mask(self):
        """Configura a máscara para o campo"""
        # Bloquear caracteres especiais (só números e caracteres da máscara)
        self.entry.bind("<KeyRelease>", self._on_mask_key_release)
        self.entry.bind("<Control-v>", self._on_paste)
        self.entry.bind("<Control-V>", self._on_paste)

    def _on_mask_key_release(self, event):
        """Aplica a máscara após cada digitação"""
        if self.applying_mask:
            return

        self.applying_mask = True
        current_text = self.entry.get()
        current_pos = self.entry.index(tk.INSERT)
        digits_only = ''.join(c for c in current_text if c.isdigit())
        digits_before_cursor = ''.join(c for c in current_text[:current_pos] if c.isdigit())

        if self.mask == "cpf":
            formatted = self._format_cpf(digits_only)
        elif self.mask == "telefone":
            formatted = self._format_telefone(digits_only)
        elif self.mask == "cnpj":
            formatted = self._format_cnpj(digits_only)
        elif self.mask == "data":
            formatted = self._format_data(digits_only)
        elif self.mask == "cep":
            formatted, _ = EnderecoService.formatar_cep(current_text)
        elif self.mask == "uf":
            formatted, _ = EnderecoService.formatar_uf(current_text)
        elif self.mask == "cidade":
            formatted, _ = EnderecoService.formatar_cidade(current_text)
        else:
            formatted = current_text

        cursor_pos = self._calculate_cursor_position(current_pos, formatted, len(digits_before_cursor))
        self.entry.delete(0, "end")
        self.entry.insert(0, formatted)
        self.entry.icursor(min(cursor_pos, len(formatted)))

        self.applying_mask = False

    def _on_paste(self, event):
        """Trata cola (Ctrl+V) com máscara"""
        try:
            pasted_text = self.entry.clipboard_get()

            if self.mask == "cpf":
                formatted = self._format_cpf(''.join(c for c in pasted_text if c.isdigit()))
            elif self.mask == "telefone":
                formatted = self._format_telefone(''.join(c for c in pasted_text if c.isdigit()))
            elif self.mask == "cnpj":
                formatted = self._format_cnpj(''.join(c for c in pasted_text if c.isdigit()))
            elif self.mask == "data":
                formatted = self._format_data(''.join(c for c in pasted_text if c.isdigit()))
            elif self.mask == "cep":
                formatted, _ = EnderecoService.formatar_cep(pasted_text)
            elif self.mask == "uf":
                formatted, _ = EnderecoService.formatar_uf(pasted_text)
            elif self.mask == "cidade":
                formatted, _ = EnderecoService.formatar_cidade(pasted_text)
            else:
                formatted = pasted_text

            try:
                sel_start = self.entry.index("sel.first")
                sel_end = self.entry.index("sel.last")
                self.entry.delete(sel_start, sel_end)
                self.entry.insert(sel_start, formatted)
            except tk.TclError:
                insert_pos = self.entry.index(tk.INSERT)
                self.entry.insert(insert_pos, formatted)

            return "break"
        except Exception:
            pass

    def _format_cpf(self, numbers):
        """Formata números como CPF: 000.000.000-00"""
        # Limitar a 11 dígitos
        numbers = numbers[:11]
        if len(numbers) <= 3:
            return numbers
        elif len(numbers) <= 6:
            return f"{numbers[:3]}.{numbers[3:]}"
        elif len(numbers) <= 9:
            return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:]}"
        else:
            return f"{numbers[:3]}.{numbers[3:6]}.{numbers[6:9]}-{numbers[9:]}"

    def _format_cnpj(self, numbers):
        """Formata números como CNPJ: 00.000.000/0000-00"""
        # Limitar a 14 dígitos
        numbers = numbers[:14]
        if len(numbers) <= 2:
            return numbers
        elif len(numbers) <= 5:
            return f"{numbers[:2]}.{numbers[2:]}"
        elif len(numbers) <= 8:
            return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:]}"
        elif len(numbers) <= 12:
            return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:]}"
        else:
            return f"{numbers[:2]}.{numbers[2:5]}.{numbers[5:8]}/{numbers[8:12]}-{numbers[12:]}"

    def _format_telefone(self, numbers):
        """Formata números como Telefone: (00) 00000-0000"""
        # Limitar a 11 dígitos
        numbers = numbers[:11]
        if len(numbers) == 0:
            return ""
        elif len(numbers) <= 2:
            return f"({numbers}"
        elif len(numbers) <= 7:
            return f"({numbers[:2]}) {numbers[2:]}"
        else:
            return f"({numbers[:2]}) {numbers[2:7]}-{numbers[7:]}"

    def _format_data(self, numbers):
        """Formata números como Data: 00/00/0000"""
        # Limitar a 8 dígitos
        numbers = numbers[:8]
        if len(numbers) <= 2:
            return numbers
        elif len(numbers) <= 4:
            return f"{numbers[:2]}/{numbers[2:]}"
        else:
            return f"{numbers[:2]}/{numbers[2:4]}/{numbers[4:]}"

    def _calculate_cursor_position(self, old_pos, formatted, numbers_only):
        """Calcula a posição do cursor após aplicar máscara"""
        if numbers_only <= 0:
            return min(old_pos, len(formatted))

        cursor = 0
        digits_seen = 0
        while cursor < len(formatted) and digits_seen < numbers_only:
            if formatted[cursor].isdigit():
                digits_seen += 1
            cursor += 1

        return cursor

    def _setup_read_only(self):
        """Configura o entry como read-only bloqueando todas as modificações"""
        # Bloquear foco (não permitir que o cursor pisque)
        self.entry.bind("<FocusIn>", self._block_focus)
        # Bloquear cliques do mouse
        self.entry.bind("<Button-1>", lambda e: "break")
        # Bloquear inserção de texto via teclado
        self.entry.bind("<KeyPress>", self._block_key_input)
        # Bloquear cola (Ctrl+V)
        self.entry.bind("<Control-v>", lambda e: "break")
        self.entry.bind("<Control-V>", lambda e: "break")
        # Bloquear corte (Ctrl+X)
        self.entry.bind("<Control-x>", lambda e: "break")
        self.entry.bind("<Control-X>", lambda e: "break")
        # Bloquear backspace e delete
        self.entry.bind("<BackSpace>", lambda e: "break")
        self.entry.bind("<Delete>", lambda e: "break")

    def _block_focus(self, event):
        """Impede que o entry receba foco, redirecionando para o parent"""
        # Redirecionar foco para o parent frame
        self.focus()
        return "break"

    def _block_key_input(self, event):
        """Bloqueia entrada de teclado, permitindo apenas navegação e seleção"""
        # Permitir teclas de navegação e seleção (sem modificação)
        allowed_keys = ["Left", "Right", "Home", "End", "Control_L", "Control_R"]
        modifiers = ["Shift", "Control"]
        
        # Se é uma tecla de navegação, modificador ou Ctrl+A (select all), permitir
        if event.keysym in allowed_keys or event.keysym in modifiers:
            return None
        
        # Permitir Ctrl+A (selecionar tudo) e Ctrl+C (copiar)
        if event.state & 0x4 and event.keysym.lower() in ["a", "c"]:
            return None
        
        # Bloquear qualquer outra entrada
        return "break"

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
        if self.mask == "cpf":
            formatted = self._format_cpf(''.join(c for c in str(value) if c.isdigit()))
        elif self.mask == "telefone":
            formatted = self._format_telefone(''.join(c for c in str(value) if c.isdigit()))
        elif self.mask == "cnpj":
            formatted = self._format_cnpj(''.join(c for c in str(value) if c.isdigit()))
        elif self.mask == "data":
            formatted = self._format_data(''.join(c for c in str(value) if c.isdigit()))
        elif self.mask == "cep":
            formatted, _ = EnderecoService.formatar_cep(str(value))
        elif self.mask == "uf":
            formatted, _ = EnderecoService.formatar_uf(str(value))
        elif self.mask == "cidade":
            formatted, _ = EnderecoService.formatar_cidade(str(value))
        else:
            formatted = str(value)
        self.entry.insert(0, formatted)


class Configuracoes(BaseScreen):
    def __init__(self, parent, tipo_usuario="clinica", clinica_id=None, usuario_id=None, app=None):
        super().__init__(parent, "Configurações")

        self.tipo_usuario = tipo_usuario
        self.clinica_id = clinica_id
        self.usuario_id = usuario_id
        self.app = app  # Referência à aplicação principal para alternar tema globalmente
        self.initialization_error = None

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

        self.tab_buttons = {}
        self.images = {}
        self.loading_states = {}
        self.clinic_entries = {}
        self.profile_entries = {}
        self.address_entries = {}
        
        # Determinar aba inicial baseada no tipo de usuário
        if self.tipo_usuario == "clinica":
            self.current_tab = "Minha Clínica"
        else:
            self.current_tab = "Perfil"

        self.setup_ui()

    def setup_ui(self):
        # Header com tabs e botão de tema
        header_container = ctk.CTkFrame(self.content_card, fg_color="transparent", height=44)
        header_container.pack(fill="x", padx=20, pady=(9, 0))
        header_container.pack_propagate(False)

        # Tabs à esquerda
        self.tab_bar = ctk.CTkFrame(header_container, fg_color="transparent")
        self.tab_bar.pack(side="left", fill="x", expand=True)

        # Botão de tema à direita
        theme_btn = ctk.CTkButton(
            header_container,
            text="Modo Escuro" if not get_dark_mode() else "Modo Claro",
            width=120,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            corner_radius=8,
            command=self._toggle_theme_global
        )
        theme_btn.pack(side="right", padx=(10, 0))
        self.theme_btn = theme_btn

        self._build_tabs()

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.content_card,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.container_conteudo = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.container_conteudo.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_footer(self.content_card)
        self.switch_tab(self.current_tab)

    def _build_tabs(self):
        todas_abas = [
            {"name": "Perfil", "text": "👤   Perfil", "tipo_acesso": ["gerenciamento", "dentista"]},
            {"name": "Segurança", "text": "🔒   Segurança", "tipo_acesso": ["clinica", "gerenciamento", "dentista"]},
            {"name": "Minha Clínica", "text": "🏥   Minha Clínica", "tipo_acesso": ["clinica", "gerenciamento"]}
        ]

        tabs_disponiveis = [tab for tab in todas_abas if self.tipo_usuario in tab["tipo_acesso"]]

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

    def _toggle_theme_global(self):
        """Alterna tema globalmente através da aplicação principal"""
        if self.app and hasattr(self.app, 'toggle_theme'):
            # Chamar o método da app que recria todos os frames
            self.app.toggle_theme()
        else:
            # Fallback: atualizar apenas localmente
            toggle_dark_mode()
            self._refresh_colors_after_theme_change()

    def _refresh_colors_after_theme_change(self):
        """Atualiza as cores após alternar tema"""
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
        self.theme_btn.configure(
            text="Modo Escuro" if not get_dark_mode() else "Modo Claro",
            fg_color=self.colors["accent"],
            hover_color=COLORS["primary_dark"]
        )
        # Recarregar aba atual para aplicar novas cores
        if hasattr(self, 'current_tab'):
            self.switch_tab(self.current_tab)

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

        for widget in self.container_conteudo.winfo_children():
            widget.destroy()

        render_methods = {
            "Perfil": self._render_profile,
            "Segurança": self._render_security,
            "Minha Clínica": self._render_preferences
        }

        if tab_name in render_methods:
            render_methods[tab_name](self.container_conteudo)

    def _titulo(self, parent, texto, padx=15):
        ctk.CTkLabel(
            parent,
            text=texto,
            font=font("title", "bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w", padx=padx, pady=(24, 17))

    def _secao_titulo(self, parent, texto, padx=15):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=padx, pady=(16, 8))

        ctk.CTkLabel(
            container,
            text=texto,
            font=font("subtitle", "bold"),
            text_color=self.colors["text_primary"]
        ).pack(anchor="w")

        linha = ctk.CTkFrame(container, height=2, width=52, fg_color=self.colors["accent"], corner_radius=1)
        linha.pack(anchor="w", pady=(4, 0))

    def _create_card_section(self, parent, title, subtitle=None):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['card'],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=self.colors["border"]
        )
        card.pack(fill="x", padx=0, pady=(0, 20), anchor="w")

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

        scroll = parent

        _, form_body = self._create_card_section(
            scroll,
            "Alterar Senha",
            "Mantenha sua conta segura com uma senha forte"
        )

        form_body.grid_columnconfigure((0, 1), weight=1)

        # Inputs de segurança
        current_pwd = ModernInput(
            form_body, label="Senha Atual", placeholder="Digite sua senha atual",
            icon="🔑", required=True
        )
        current_pwd.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=8)
        current_pwd.entry.configure(show="•")

        new_pwd = ModernInput(
            form_body, label="Nova Senha", placeholder="Digite a nova senha",
            icon="🔒", required=True
        )
        new_pwd.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=8)
        new_pwd.entry.configure(show="•")

        confirm_pwd = ModernInput(
            form_body, label="Confirmar Nova Senha", placeholder="Digite novamente a nova senha",
            icon="✓", required=True
        )
        confirm_pwd.grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)
        confirm_pwd.entry.configure(show="•")

        # Frame da força da senha
        strength_frame = ctk.CTkFrame(form_body, fg_color="transparent")
        strength_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        ctk.CTkLabel(
            strength_frame, text="Força da senha:", font=font("small"),
            text_color=self.colors["text_secondary"]
        ).pack(side="left", padx=(0, 10))

        self.strength_bar = ctk.CTkProgressBar(
            strength_frame, width=200, height=6, corner_radius=4,
            progress_color=self.colors["accent"]
        )
        self.strength_bar.pack(side="left")
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
        sub_tabs = ["Geral", "Serviços", "Descrição"]
        self.sub_tab_buttons = {}

        tab_frame = ctk.CTkFrame(parent, fg_color="transparent")
        tab_frame.pack(fill="x", padx=0, pady=(17, 10), anchor="w")

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
        divider.pack(fill="x", padx=0, pady=(0, 15))

        self.sub_tab_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.sub_tab_content.pack(fill="both", expand=True)

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
        scroll = parent

        clinica_data = None
        endereco_data = None

        if self.tipo_usuario == "clinica" and self.clinica_id:
            clinica_data = self._load_clinic_data()
            endereco_data = self._load_endereco_data()

        # CARD IDENTIDADE
        if self.tipo_usuario == "clinica" or self.tipo_usuario == "gerenciamento":
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
                bg=self.colors["bg_card"],
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
                {"label": "CNPJ", "placeholder": "00.000.000/0000-00", "row": 0, "col": 1, "required": True, "mask": "cnpj"},
                {"label": "E-mail Clínica", "placeholder": "email@clinica.com", "row": 1, "col": 0, "required": True},
                {"label": "Telefone", "placeholder": "(00) 00000-0000", "row": 1, "col": 1, "required": True, "mask": "telefone"},
            ]

            for field in fields:
                padx_val = (0, 8) if field["col"] == 0 else (8, 0)

                input_widget = ModernInput(
                    info_col,
                    label=field["label"],
                    placeholder=field["placeholder"],
                    required=field.get("required", False),
                    mask=field.get("mask")
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
            "Gerencie o banner principal e as fotos exibidas no site"
        )

        self.clinic_photos_container = ctk.CTkFrame(
            fotos_body,
            fg_color=COLORS["input_bg"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=self.colors["border"]
        )
        self.clinic_photos_container.pack(fill="both", expand=True, pady=(4, 0))

        # Novo layout: Banner + Galeria (3 fotos)
        self.clinic_banner = None  # Banner principal
        self.clinic_photos = []     # Galeria: máximo 3 fotos
        self.current_photo_index = 0  # Para compatibilidade
        self.photo_cards = []       # Lista de cards da galeria
        self.photo_canvases = []    # Lista de canvases dos cards

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
            {"label": "CEP", "placeholder": "00000-000", "row": 0, "col": 0, "mask": "cep"},
            {"label": "Estado", "placeholder": "UF", "row": 0, "col": 1, "mask": "uf"},
            {"label": "Cidade", "placeholder": "Nome da cidade", "row": 0, "col": 2, "mask": "cidade"},
            {"label": "Rua", "placeholder": "Nome da rua", "row": 1, "col": 0},
            {"label": "Número", "placeholder": "123", "row": 1, "col": 1},
            {"label": "Bairro", "placeholder": "Nome do bairro", "row": 1, "col": 2},
        ]

        for field in fields:
            input_widget = ModernInput(
                endereco_body,
                label=field["label"],
                placeholder=field["placeholder"],
                mask=field.get("mask")
            )
            input_widget.grid(
                row=field["row"],
                column=field["col"],
                sticky="ew",
                padx=8,
                pady=8
            )
            self.address_entries[field["label"]] = input_widget

        self._bind_address_fields()

        if endereco_data:
            self.address_entries["Rua"].set(endereco_data.get("rua", ""))
            self.address_entries["Número"].set(endereco_data.get("numero", ""))
            self.address_entries["Bairro"].set(endereco_data.get("bairro", ""))
            self.address_entries["Cidade"].set(endereco_data.get("cidade", ""))
            self.address_entries["Estado"].set(endereco_data.get("estado", ""))
            self.address_entries["CEP"].set(endereco_data.get("cep", ""))

    def _bind_address_fields(self):
        if not self.address_entries:
            return

        cep_entry = self.address_entries.get("CEP")
        if cep_entry:
            cep_entry.entry.bind("<KeyRelease>", self._on_cep_field_change, add="+")

        if self.address_entries.get("CEP") and self.address_entries.get("CEP").get().strip():
            self.after(200, lambda: self._on_cep_field_change(None))

    def _on_cep_field_change(self, event=None):
        if not self.address_entries or "CEP" not in self.address_entries:
            return

        cep_value = self.address_entries["CEP"].get().strip()
        cep_numero = EnderecoService.extrair_cep_numeros(cep_value)

        if len(cep_numero) != 8:
            return

        self.after(100, lambda: self._buscar_cep_automatico(cep_numero))

    def _buscar_cep_automatico(self, cep_numero):
        if not self.address_entries:
            return

        cep_entry = self.address_entries.get("CEP")
        if not cep_entry:
            return

        cep_texto = cep_entry.get().strip()
        if EnderecoService.extrair_cep_numeros(cep_texto) != cep_numero:
            return

        EnderecoService.buscar_cep_async(
            cep_numero,
            callback=self._preencher_endereco_por_cep,
            erro_callback=self._tratar_erro_busca_cep
        )

    def _preencher_endereco_por_cep(self, endereco):
        if not endereco:
            self.after(0, self._limpar_endereco_automatico)
            return

        self.after(0, lambda: self._aplicar_endereco_preenchido(endereco))

    def _aplicar_endereco_preenchido(self, endereco):
        if "Rua" in self.address_entries:
            self.address_entries["Rua"].set(endereco.get("rua", ""))
        if "Bairro" in self.address_entries:
            self.address_entries["Bairro"].set(endereco.get("bairro", ""))
        if "Cidade" in self.address_entries:
            self.address_entries["Cidade"].set(endereco.get("cidade", ""))
        if "Estado" in self.address_entries:
            self.address_entries["Estado"].set(endereco.get("estado", ""))

    def _tratar_erro_busca_cep(self, mensagem):
        self.after(0, lambda: self._mostrar_erro_cep(mensagem))

    def _mostrar_erro_cep(self, mensagem):
        self._limpar_endereco_automatico()
        messagebox.showwarning("CEP não encontrado", f"{mensagem}.\n\nOs campos de endereço preenchidos automaticamente foram limpos.")

    def _limpar_endereco_automatico(self):
        for campo in ["Rua", "Bairro", "Cidade", "Estado"]:
            if campo in self.address_entries:
                self.address_entries[campo].set("")

    def _render_preferences_services(self, parent):
        scroll = parent
        # Cabeçalho da seção (mantido conforme solicitado)
        self._secao_titulo(scroll, "Serviços Oferecidos", padx=0)

        # Botão de adicionar serviço
        add_btn = ctk.CTkButton(
            scroll,
            text='+ Adicionar Serviço e Valor',
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("accent_hover", self.colors.get("primary_soft")),
            font=font("text", "bold"),
            text_color="white",
            corner_radius=8,
            height=36,
            command=self._abrir_modal_adicionar_servico
        )
        add_btn.pack(anchor="w", pady=(8, 12))

        # Frame rolável que conterá a lista de serviços
        self.services_list_frame = ctk.CTkScrollableFrame(
            scroll,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            corner_radius=8,
            height=220
        )
        self.services_list_frame.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        # Cabeçalho da lista (3 colunas)
        header = ctk.CTkFrame(self.services_list_frame, fg_color="transparent")
        # Garantir largura mínima da coluna de nome para alinhar a coluna de valores
        header.grid_columnconfigure(0, weight=3, minsize=420)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)
        header.pack(fill="x", padx=8, pady=(6, 6))

        ctk.CTkLabel(header, text="Serviço", font=font("text", "bold"), text_color=self.colors["text_primary"]).grid(row=0, column=0, sticky="w")
        # Ajuste mínimo: deslocar levemente o título "Valor" para centralizar sobre a coluna
        ctk.CTkLabel(header, text="Valor", font=font("text", "bold"), text_color=self.colors["text_secondary"]).grid(row=0, column=1, sticky="w", padx=(0, 40))
        ctk.CTkLabel(header, text="", font=font("text", "bold"), text_color=self.colors["text_secondary"]).grid(row=0, column=2, sticky="e")

        # Corpo da lista será preenchido por _carregar_servicos
        self._carregar_servicos()

    def _render_preferences_description(self, parent):
        scroll = parent

        self._secao_titulo(scroll, "Sobre a Clínica", padx=0)

        self.description_text = ctk.CTkTextbox(
            scroll,
            height=280,
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=COLORS["input_bg"],
            font=font("text"),
            text_color=self.colors["text_primary"]
        )
        self.description_text.pack(fill="both", expand=True, anchor="w", padx=0, pady=(10, 0))
        self.description_text.insert("1.0", "Bem-vindo à nossa clínica! Somos uma equipe dedicada a proporcionar o melhor cuidado para seu sorriso...")

    # ==================== SERVIÇOS (Banco) ====================
    def _carregar_servicos(self):
        """Carrega e renderiza a lista de serviços da clínica atual."""
        # Limpa linhas anteriores (mantém apenas o cabeçalho)
        for w in list(self.services_list_frame.winfo_children()):
            # keep header label frames (we treat first child as header)
            # header was packed first, so remove all except the first header frame
            pass

        # Remove all except first (header)
        children = self.services_list_frame.winfo_children()
        if len(children) > 1:
            for ch in children[1:]:
                ch.destroy()

        # Buscar serviços no banco
        servicos = self._buscar_servicos_no_banco()

        if not servicos:
            empty = ctk.CTkLabel(self.services_list_frame, text="Nenhum serviço cadastrado ainda.", text_color=self.colors["text_secondary"], font=font("text"))
            empty.pack(padx=8, pady=12)
            return

        # Para cada serviço, criar uma linha com 3 colunas
        for idx, s in enumerate(servicos):
            row = ctk.CTkFrame(self.services_list_frame, fg_color="transparent")
            # Manter mesma largura mínima que o cabeçalho para alinhar valores
            row.grid_columnconfigure(0, weight=3, minsize=420)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=0)
            row.pack(fill="x", padx=8, pady=6)

            nome = s.get("nome") if isinstance(s, dict) else s[1]
            valor = s.get("preco") if isinstance(s, dict) else s[2]
            serv_id = s.get("id") if isinstance(s, dict) else s[0]

            # Formatar valor para padrão BR (milhares com . e decimais com ,)
            try:
                from decimal import Decimal
                v = Decimal(valor)
                v_str = f"{v:,.2f}"
                # trocar 1,234.56 -> 1.234,56
                v_str = v_str.replace(',', 'X').replace('.', ',').replace('X', '.')
                valor_text = f"R$ {v_str}"
            except Exception:
                valor_text = f"R$ {valor}"

            ctk.CTkLabel(row, text=nome, text_color=self.colors["text_primary"], font=font("text")).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(row, text=valor_text, text_color=self.colors["text_secondary"], font=font("text")).grid(row=0, column=1, sticky="w")

            del_btn = ctk.CTkButton(row, text="🗑", width=36, height=28, fg_color="transparent", hover_color=self.colors.get("row_hover", COLORS.get("hover")), text_color=COLORS.get("danger"), command=lambda sid=serv_id: self._excluir_servico(sid))
            del_btn.grid(row=0, column=2, sticky="e")

    def _buscar_servicos_no_banco(self):
        try:
            from config.database import get_connection
            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id, nome, preco
                    FROM odontoPro_especialidade
                    WHERE clinica_id = %s
                    ORDER BY nome ASC
                """, (self.clinica_id,))
                rows = cursor.fetchall() or []
                return rows
            except Exception as e:
                print(f"Erro ao buscar serviços: {e}")
                return []
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Erro ao buscar serviços (import/conn): {e}")
            return []

    def _abrir_modal_adicionar_servico(self):
        top = ctk.CTkToplevel(self)
        top.title("Adicionar Serviço e Valor")
        top.transient(self)
        top.grab_set()

        # Tamanho inicial confortável para exibir todos os campos sem cortar
        modal_w, modal_h = 520, 300
        top.geometry(f"{modal_w}x{modal_h}")
        # Não permitir redimensionamento manual (manter comportamento modal)
        try:
            top.resizable(False, False)
        except Exception:
            pass

        # Garantir que dimensões e layout foram aplicados antes de calcular posição
        try:
            top.update_idletasks()
        except Exception:
            pass

        # Centralizar em relação à janela principal (toplevel pai)
        try:
            parent_win = self.winfo_toplevel()
            parent_win.update_idletasks()
            px = parent_win.winfo_rootx()
            py = parent_win.winfo_rooty()
            pw = parent_win.winfo_width()
            ph = parent_win.winfo_height()

            x = px + (pw - modal_w) // 2
            y = py + (ph - modal_h) // 2

            # Garantir que o modal fique dentro dos limites da tela
            screen_w = top.winfo_screenwidth()
            screen_h = top.winfo_screenheight()
            x = max(0, min(x, screen_w - modal_w))
            y = max(0, min(y, screen_h - modal_h))

            top.geometry(f"{modal_w}x{modal_h}+{x}+{y}")
        except Exception as e:
            print(f"[AVISO] Não foi possível centralizar modal: {e}")

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)

        ctk.CTkLabel(body, text="Serviço", font=font("text", "bold"), text_color=self.colors["text_primary"]).pack(anchor="w")
        nome_entry = ctk.CTkEntry(body, placeholder_text="Ex: Limpeza profissional", width=440, fg_color=COLORS.get("input_bg"))
        nome_entry.pack(fill="x", pady=(6, 12))

        ctk.CTkLabel(body, text="Valor (R$)", font=font("text", "bold"), text_color=self.colors["text_primary"]).pack(anchor="w")
        valor_entry = ctk.CTkEntry(body, placeholder_text="Ex: 150.00", width=200, fg_color=COLORS.get("input_bg"))
        valor_entry.pack(fill="x", pady=(6, 12))

        error_label = ctk.CTkLabel(body, text="", text_color=COLORS.get("danger"), font=font("text"))
        error_label.pack(anchor="w", pady=(0, 8))

        def on_save():
            nome = nome_entry.get().strip()
            # normalizar espaços internos
            nome = " ".join(nome.split())
            raw_val = valor_entry.get().strip()
            raw_val = raw_val.replace(',', '.')
            if not nome:
                error_label.configure(text="Nome do serviço não pode ficar vazio.")
                return
            try:
                from decimal import Decimal, InvalidOperation
                val = Decimal(raw_val)
                if val < 0:
                    error_label.configure(text="Valor não pode ser negativo.")
                    return
            except Exception:
                error_label.configure(text="Valor inválido. Use 150.00 ou 150,00")
                return

            saved = self._salvar_servico_no_banco(nome, val)
            if saved:
                top.destroy()
                self._carregar_servicos()
            else:
                error_label.configure(text="Erro ao salvar serviço. Veja o console.")

        save_btn = ctk.CTkButton(body, text="Salvar", fg_color=COLORS.get("primary"), hover_color=COLORS.get("accent_hover", self.colors.get("primary_soft")), command=on_save, font=font("text", "bold"))
        save_btn.pack(anchor="e", pady=(6, 0))

    def _salvar_servico_no_banco(self, nome, valor):
        try:
            from config.database import get_connection
            import traceback
            conn = None
            cursor = None
            try:
                # Debug: mostrar valores sendo salvos
                print(f"[DEBUG] clinica_id: {self.clinica_id} (tipo: {type(self.clinica_id)})")
                print(f"[DEBUG] nome: {nome} (tipo: {type(nome)})")
                print(f"[DEBUG] valor: {valor} (tipo: {type(valor)})")
                
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO odontoPro_especialidade (nome, preco, clinica_id)
                    VALUES (%s, %s, %s)
                """, (nome, str(valor), self.clinica_id))
                conn.commit()
                return True
            except Exception as e:
                print(f"[ERRO] Falha ao salvar serviço: {e}")
                traceback.print_exc()
                return False
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        except Exception as e:
            print(f"[ERRO] Falha ao salvar serviço (import/conn): {e}")
            import traceback
            traceback.print_exc()
            return False

    def _excluir_servico(self, servico_id):
        try:
            result = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir este serviço?")
            if not result:
                return

            from config.database import get_connection
            import mysql.connector
            
            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM odontoPro_especialidade WHERE id = %s", (servico_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    self._carregar_servicos()
                    messagebox.showinfo("Sucesso", "Serviço excluído com sucesso.")
                else:
                    messagebox.showwarning("Aviso", f"Serviço não encontrado.")
                    
            except mysql.connector.errors.IntegrityError as e:
                # Erro de chave estrangeira (Foreign Key Constraint)
                if "1451" in str(e):
                    messagebox.showerror("Não é possível excluir", 
                        "Este serviço está vinculado a consultas agendadas.\n\n"
                        "Para excluir este serviço, primeiro cancele ou delete as consultas relacionadas.")
                else:
                    messagebox.showerror("Erro", f"Falha ao excluir serviço: {e}")
                    
            except Exception as e:
                print(f"[ERRO] Falha ao excluir serviço: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erro", "Falha ao excluir serviço. Veja o console.")
                
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"[ERRO] Erro no fluxo de exclusão: {e}")
            import traceback
            traceback.print_exc()


    # ==================== PERFIL ====================
    def _render_profile(self, parent):
        self._titulo(parent, "Meu Perfil")

        scroll = parent

        _, form_body = self._create_card_section(
            scroll,
            "Informações Pessoais",
            "Gerencie seus dados pessoais"
        )

        form_body.grid_columnconfigure((0, 1), weight=1)

        fields = [
            {"label": "Nome Completo", "placeholder": "Gabriel Gomes", "row": 0, "col": 0, "icon": "👤", "required": True},
            {"label": "CPF", "placeholder": "000.000.000-00", "row": 0, "col": 1, "icon": "📄", "required": True, "mask": "cpf"},
            {"label": "E-mail", "placeholder": "gabriel@email.com", "row": 1, "col": 0, "icon": "✉️", "required": True},
            {"label": "Telefone", "placeholder": "(00) 00000-0000", "row": 1, "col": 1, "icon": "📞", "required": True, "mask": "telefone"},
            {"label": "Data de Nascimento", "placeholder": "24/05/2002", "row": 2, "col": 0, "icon": "🎂", "required": False, "mask": "data"},
            {"label": "Profissão", "placeholder": "Dentista", "row": 2, "col": 1, "icon": "💼", "required": False, "read_only": True}
        ]

        self.profile_entries = {}
        for field in fields:
            input_widget = ModernInput(
                form_body, label=field["label"], placeholder=field["placeholder"],
                icon=field["icon"], required=field.get("required", False),
                read_only=field.get("read_only", False), mask=field.get("mask", None)
            )
            padx_val = (0, 8) if field["col"] == 0 else (8, 0)

            input_widget.grid(
                row=field["row"], column=field["col"], sticky="ew",
                padx=padx_val, pady=8
            )
            self.profile_entries[field["label"]] = input_widget

        profile_data = self._load_user_profile_data()
        if profile_data:
            self.profile_entries["Nome Completo"].set(profile_data.get("nome", ""))
            self.profile_entries["E-mail"].set(profile_data.get("email", ""))

    def _render_profile_form(self, parent):
        pass

    # ==================== FOOTER ====================
    def _build_footer(self, parent):
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=20, pady=(0, 20))

        ActionButtons(
            footer,
            primary_text="SALVAR ALTERAÇÕES",
            secondary_text="CANCELAR",
            on_primary=self._save,
            on_secondary=self._cancel
        ).pack(anchor="w")

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
                    SELECT nome, cnpj, email, telefone, logo
                    FROM odontoPro_clinica
                    WHERE id = %s
                """, (self.clinica_id,))

                result = cursor.fetchone()
                if result:
                    # photos/fotos column is not available in the current schema.
                    # Keep UI compatibility by returning an empty list for photos.
                    data = {
                        "nome": result[0] or "",
                        "cnpj": result[1] or "",
                        "email": result[2] or "",
                        "telefone": result[3] or "",
                        "logo": result[4] or "",
                        "photos": []
                    }
                    print(f"[DEBUG] Dados carregados: {data}")
                    return data

                print("[DEBUG] Nenhum resultado encontrado para clinica_id:", self.clinica_id)
                return None

            except Exception as e:
                erro_texto = str(e).lower()
                if "unknown column" in erro_texto and "fotos" in erro_texto:
                    print(f"[AVISO] Dados de fotos indisponíveis; Configurações continuará carregando: {e}")
                else:
                    self.initialization_error = e
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
                    WHERE id = %s AND clinica_id = %s
                """, (self.usuario_id, self.clinica_id))

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
            hover_color=self.colors["success"],
            state="normal"
        )

    def _setup_clinic_photos_ui(self):
        """Reorganiza a UI de fotos em duas seções: Banner Principal e Galeria"""
        for widget in self.clinic_photos_container.winfo_children():
            widget.destroy()

        # Frame principal que ocupa todo o container
        main_wrap = ctk.CTkFrame(self.clinic_photos_container, fg_color="transparent")
        main_wrap.pack(fill="both", expand=True, padx=16, pady=16)
        main_wrap.grid_columnconfigure(0, weight=1)

        # ==================== BANNER PRINCIPAL ====================
        # Título da seção Banner
        banner_title = ctk.CTkLabel(
            main_wrap,
            text="Banner Principal",
            font=font("text", "bold"),
            text_color=self.colors["text_primary"]
        )
        banner_title.pack(anchor="w", pady=(0, 4))

        # Subtítulo do Banner
        banner_subtitle = ctk.CTkLabel(
            main_wrap,
            text="Imagem exibida em destaque no perfil da clínica",
            font=font("text", "normal"),
            text_color=self.colors["text_secondary"]
        )
        banner_subtitle.pack(anchor="w", pady=(0, 12))

        # Frame do preview do banner (16:9)
        banner_preview_frame = ctk.CTkFrame(
            main_wrap,
            fg_color=COLORS['card'],
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            height=180
        )
        banner_preview_frame.pack(fill="x", pady=(0, 12))
        banner_preview_frame.pack_propagate(False)

        # Canvas do banner (proporção 16:9)
        self.banner_canvas = tk.Canvas(
            banner_preview_frame,
            bg=self.colors["bg_card"],
            highlightthickness=0,
            bd=0
        )
        self.banner_canvas.pack(fill="both", expand=True, padx=12, pady=12)
        self.banner_canvas.bind("<Configure>", self._on_banner_canvas_resize)

        # Botão do banner
        select_banner_btn = ctk.CTkButton(
            main_wrap,
            text="+ Selecionar Banner",
            height=40,
            font=("Arial", 11, "bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            corner_radius=6,
            command=self._add_clinic_banner
        )
        select_banner_btn.pack(anchor="e", pady=(0, 24))

        # ==================== GALERIA DA CLÍNICA ====================
        # Título da galeria
        gallery_title = ctk.CTkLabel(
            main_wrap,
            text="Galeria da Clínica",
            font=font("text", "bold"),
            text_color=self.colors["text_primary"]
        )
        gallery_title.pack(anchor="w", pady=(0, 4))

        # Subtítulo da galeria
        gallery_subtitle = ctk.CTkLabel(
            main_wrap,
            text="Adicione até 3 fotos dos ambientes da clínica",
            font=font("text", "normal"),
            text_color=self.colors["text_secondary"]
        )
        gallery_subtitle.pack(anchor="w", pady=(0, 12))

        # Frame da galeria (grid 3 colunas)
        gallery_frame = ctk.CTkFrame(main_wrap, fg_color="transparent")
        gallery_frame.pack(fill="x", expand=True, pady=(0, 12))
        gallery_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="gallery")

        # Criar 3 cards de foto
        self.photo_cards = []
        self.photo_canvases = []

        for idx in range(3):
            # Card da foto
            card_frame = ctk.CTkFrame(
                gallery_frame,
                fg_color=COLORS['card'],
                corner_radius=8,
                border_width=1,
                border_color=self.colors["border"]
            )
            card_frame.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 8, 0))
            card_frame.grid_rowconfigure(0, weight=0)
            card_frame.grid_rowconfigure(1, weight=0)
            card_frame.grid_rowconfigure(2, weight=0)
            card_frame.grid_columnconfigure(0, weight=1)

            # Número da foto
            photo_num_label = ctk.CTkLabel(
                card_frame,
                text=f"Foto {idx + 1}",
                font=font("text", "bold"),
                text_color=self.colors["text_primary"]
            )
            photo_num_label.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 6))

            # Canvas de preview
            photo_canvas = tk.Canvas(
                card_frame,
                bg=self.colors["bg_card"],
                highlightthickness=0,
                bd=0,
                height=92
            )
            photo_canvas.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
            photo_canvas.grid_propagate(False)
            
            # Armazenar reference para atualizar depois
            self.photo_canvases.append(photo_canvas)

            # Frame para botão
            btn_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            btn_frame.grid(row=2, column=0, sticky="n", padx=12, pady=(0, 10))
            btn_frame.grid_columnconfigure(0, weight=1)

            # Botão de adicionar foto
            add_btn = ctk.CTkButton(
                btn_frame,
                text="+ Adicionar foto",
                width=150,
                height=30,
                font=("Arial", 10, "bold"),
                fg_color=self.colors["accent"],
                hover_color=self.colors["accent_hover"],
                corner_radius=6,
                command=lambda index=idx: self._add_gallery_photo(index)
            )
            add_btn.grid(row=0, column=0, sticky="n")

            self.photo_cards.append({
                "frame": card_frame,
                "canvas": photo_canvas,
                "btn": add_btn
            })

        # Inicializar displays
        self._update_banner_display()
        self._update_gallery_display()

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

    # ==================== NOVO LAYOUT: BANNER PRINCIPAL ====================
    def _update_banner_display(self, canvas_width=None, canvas_height=None):
        """Atualiza o preview do banner com proporção 16:9"""
        if canvas_width is None:
            # Assumir width do container aproximadamente
            canvas_width = 400
        if canvas_height is None:
            # Proporção 16:9
            canvas_height = int(canvas_width * 9 / 16)

        if not self.clinic_banner:
            # Estado vazio
            ImagePreview.create_rectangular_preview(
                self.banner_canvas,
                None,
                canvas_width,
                canvas_height,
                "Nenhum banner selecionado\nClique para adicionar"
            )
        else:
            # Mostrar banner
            ImagePreview.create_rectangular_preview(
                self.banner_canvas,
                self.clinic_banner,
                canvas_width,
                canvas_height,
                "BANNER"
            )

    def _on_banner_canvas_resize(self, event):
        """Callback quando o banner redimensiona"""
        # Manter proporção 16:9
        canvas_height = int(event.width * 9 / 16)
        self._update_banner_display(event.width, canvas_height)

    def _add_clinic_banner(self):
        """Selecionar imagem para o banner"""
        file_path = filedialog.askopenfilename(
            title="Selecionar imagem do banner",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.clinic_banner = file_path
            self._update_banner_display()

    # ==================== NOVO LAYOUT: GALERIA DA CLÍNICA ====================
    def _update_gallery_display(self):
        """Atualiza os previews dos 3 cards da galeria"""
        if not hasattr(self, 'photo_canvases') or not self.photo_canvases:
            return

        for idx, canvas in enumerate(self.photo_canvases):
            if idx < len(self.clinic_photos) and self.clinic_photos[idx]:
                # Mostrar foto
                ImagePreview.create_rectangular_preview(
                    canvas,
                    self.clinic_photos[idx],
                    260,
                    92,
                    "FOTO"
                )
            else:
                # Espaço vazio
                ImagePreview.create_rectangular_preview(
                    canvas,
                    None,
                    260,
                    92,
                    "Sem imagem"
                )

    def _add_gallery_photo(self, index):
        """Adicionar foto a um card específico da galeria"""
        if index < 0 or index >= 3:
            return

        file_path = filedialog.askopenfilename(
            title=f"Selecionar foto {index + 1} da clínica",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            # Garantir que a lista tem 3 posições
            while len(self.clinic_photos) <= index:
                self.clinic_photos.append(None)
            
            self.clinic_photos[index] = file_path
            self._update_gallery_display()

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
        """Salva apenas os dados da aba ativa"""
        if self.current_tab == "Perfil":
            self._save_profile()
        elif self.current_tab == "Segurança":
            self._save_security()
        elif self.current_tab == "Minha Clínica":
            self._save_clinic()

    def _save_profile(self):
        """Valida e salva dados do perfil do usuário no banco de dados"""
        all_valid = True
        
        for _, input_widget in self.profile_entries.items():
            if not input_widget._validate():
                all_valid = False

        if all_valid:
            try:
                from config.database import get_connection
                
                conn = None
                cursor = None
                
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    nome = self.profile_entries["Nome Completo"].get().strip()
                    email = self.profile_entries["E-mail"].get().strip()
                    cpf = self.profile_entries["CPF"].get().strip()
                    telefone = self.profile_entries["Telefone"].get().strip()
                    data_nascimento = self.profile_entries["Data de Nascimento"].get().strip()
                    
                    # Convertendo data de DD/MM/YYYY para YYYY-MM-DD
                    if data_nascimento and len(data_nascimento) == 10:
                        try:
                            dia, mes, ano = data_nascimento.split("/")
                            data_nascimento = f"{ano}-{mes}-{dia}"
                        except:
                            data_nascimento = None
                    else:
                        data_nascimento = None
                    
                    cursor.execute("""
                        UPDATE odontoPro_gerenciamento
                        SET nome = %s, email = %s
                        WHERE id = %s AND clinica_id = %s
                    """, (nome, email, self.usuario_id, self.clinica_id))
                    
                    conn.commit()
                    messagebox.showinfo("Sucesso", "✓ Dados do perfil salvos com sucesso!\n\nNota: CPF, Telefone e Data de Nascimento podem estar em outra tabela ou serão implementados em breve.")
                    
                except Exception as e:
                    if conn:
                        conn.rollback()
                    messagebox.showerror("Erro", f"Erro ao salvar perfil: {str(e)}")
                    print(f"[ERRO] {str(e)}")
                    
                finally:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()
                        
            except ImportError as e:
                messagebox.showerror("Erro", f"Erro ao importar módulos: {str(e)}")
        else:
            messagebox.showerror("Erro", "Por favor, preencha todos os campos obrigatórios.")

    def _save_security(self):
        """Valida e salva dados de segurança (senha)"""
        # TODO: Implementar salvamento de senha com validação de senha atual
        messagebox.showinfo("Sucesso", "✓ Segurança atualizada com sucesso!")
        print("[INFO] Funcionalidade de segurança será implementada com validação de senha.")
        return

    def _save_clinic(self):
        """Valida e salva dados da clínica"""
        all_valid = True
        
        if self.clinic_entries:
            for _, input_widget in self.clinic_entries.items():
                if not input_widget._validate():
                    all_valid = False

        if all_valid:
            if (self.tipo_usuario == "clinica" or self.tipo_usuario == "gerenciamento") and self.clinica_id:
                self._save_clinic_data()
            else:
                messagebox.showinfo("Sucesso", "✓ Configurações da clínica salvas com sucesso!")
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

                # Store only digits for CNPJ and Telefone in DB
                try:
                    cnpj_clean = re.sub(r"\D", "", cnpj)
                except Exception:
                    cnpj_clean = cnpj

                try:
                    telefone_clean = re.sub(r"\D", "", telefone)
                except Exception:
                    telefone_clean = telefone

                cursor.execute("""
                    UPDATE odontoPro_clinica
                    SET nome = %s, cnpj = %s, email = %s, telefone = %s
                    WHERE id = %s
                """, (nome, cnpj_clean, email, telefone_clean, self.clinica_id))

                if "logo" in self.images:
                    logo_path = self.images["logo"]
                    saved_logo = None

                    try:
                        # Case A: user selected a remote URL (already uploaded)
                        if isinstance(logo_path, str) and logo_path.lower().startswith(("http://", "https://")):
                            saved_logo = logo_path

                        # Case B: local file selected -> upload to Cloudinary
                        elif isinstance(logo_path, str) and os.path.exists(logo_path):
                            try:
                                public_id = f"clinica_{self.clinica_id}_{int(time.time())}"
                                folder = f"odontopro/clinicas/{self.clinica_id}"
                                print(f"[LOGO] Iniciando upload Cloudinary for clinica_id={self.clinica_id}")
                                saved_logo = upload_image_to_cloudinary(logo_path, public_id=public_id, folder=folder)
                                print(f"[LOGO] Upload concluído, URL recebida: {saved_logo}")
                            except Exception as e:
                                print(f"[AVISO] Falha ao enviar logo para Cloudinary: {e}")
                                messagebox.showerror("Erro", f"Falha ao enviar a logo para o Cloudinary: {str(e)}")
                                saved_logo = None

                        else:
                            # The value is neither an accessible local file nor an http url.
                            print(f"[AVISO] Valor inesperado para self.images['logo']: {logo_path}")
                            saved_logo = None

                    except Exception as e:
                        print(f"[ERRO] Erro ao processar imagem da logo: {e}")
                        saved_logo = None

                    # Only update DB when we have a valid HTTPS URL returned by Cloudinary or an existing remote URL
                    if saved_logo and isinstance(saved_logo, str) and saved_logo.lower().startswith("https://"):
                        cursor.execute("""
                            UPDATE odontoPro_clinica
                            SET logo = %s
                            WHERE id = %s
                        """, (saved_logo, self.clinica_id))
                        print(f"[LOGO] Atualizando clinica_id={self.clinica_id} com URL Cloudinary")
                    else:
                        # Do not overwrite existing logo in DB. Keep previous value.
                        print(f"[LOGO] Nenhuma URL válida para atualizar no banco; mantendo logo atual para clinica_id={self.clinica_id}")

                if hasattr(self, "clinic_photos"):
                    saved_photos = []
                    upload_dir = os.path.join(os.path.dirname(__file__), "../assets/clinicas/fotos")
                    os.makedirs(upload_dir, exist_ok=True)

                    for i, photo_path in enumerate(self.clinic_photos):
                        # Keep UI behavior (allow selecting photos locally) but do not persist
                        # them to the database yet since the `fotos` column does not exist.
                        try:
                            if os.path.exists(photo_path):
                                if not os.path.abspath(photo_path).startswith(os.path.abspath(upload_dir)):
                                    extensao = os.path.splitext(photo_path)[1] or ".jpg"
                                    filename = f"clinica_{self.clinica_id}_foto_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}{extensao}"
                                    dest_path = os.path.join(upload_dir, filename)
                                    shutil.copy(photo_path, dest_path)
                                    saved_photos.append(dest_path)
                                else:
                                    saved_photos.append(photo_path)
                        except Exception as _e:
                            # Ignore photo copy errors for now; do not block saving clinic data
                            print(f"[AVISO] Erro ao processar foto local: {_e}")

                # Salvar endereço
                if self.address_entries:
                    rua = self.address_entries["Rua"].get().strip()
                    numero = self.address_entries["Número"].get().strip()
                    bairro = self.address_entries["Bairro"].get().strip()
                    cidade = self.address_entries["Cidade"].get().strip()
                    estado = self.address_entries["Estado"].get().strip()
                    cep = self.address_entries["CEP"].get().strip()

                    # Save CEP to DB as digits only (e.g., 66017010) to avoid column length/format issues
                    try:
                        cep_clean = re.sub(r"\D", "", cep)
                    except Exception:
                        cep_clean = cep

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
                        """, (rua, numero, bairro, cidade, estado, cep_clean, endereco_id))
                    else:
                        cursor.execute("""
                            INSERT INTO odontoPro_endereco (rua, numero, bairro, cidade, estado, cep)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (rua, numero, bairro, cidade, estado, cep_clean))

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
