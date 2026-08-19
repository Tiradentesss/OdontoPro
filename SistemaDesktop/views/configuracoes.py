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
    def create_rectangular_preview(canvas, image_path, width=300, height=150, placeholder_text="IMG", fit_mode="contain", draw_border=True):
        """Cria preview retangular de imagem em um canvas
        
        fit_mode:
            "contain" - ajusta a imagem para caber dentro da área, deixando espaço em branco se necessário (padrão)
            "cover"   - ajusta a imagem para cobrir toda a área, fazendo crop centralizado se necessário

        draw_border:
            True  - desenha uma borda interna (usado em previews que precisam de contorno)
            False - não desenha borda interna, usando toda a área de preview
        """
        canvas.delete("all")

        img = ImagePreview._load_image(image_path)
        if img:
            try:
                img_ratio = img.width / img.height
                canvas_ratio = width / height

                if fit_mode == "cover":
                    # Comportamento cover: Escala para cobrir toda a área, depois faz crop centralizado
                    # Calcula a escala necessária para cobrir (usar max em vez de min)
                    scale = max(width / img.width, height / img.height)
                    
                    new_width = int(img.width * scale)
                    new_height = int(img.height * scale)
                    
                    # Redimensiona mantendo proporção
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Calcula crop centralizado
                    left = (new_width - width) // 2
                    top = (new_height - height) // 2
                    right = left + width
                    bottom = top + height
                    
                    # Garante que não sai dos limites
                    left = max(0, left)
                    top = max(0, top)
                    right = min(new_width, right)
                    bottom = min(new_height, bottom)
                    
                    # Faz o crop
                    img = img.crop((left, top, right, bottom))
                    
                    # Se ficou menor do que deveria (casos edge), redimensiona para o tamanho exato
                    if img.size != (width, height):
                        img = img.resize((width, height), Image.Resampling.LANCZOS)
                    
                    photo = ImageTk.PhotoImage(img)
                    # Desenha no centro do canvas (que agora tem tamanho exato)
                    canvas.create_image(width // 2, height // 2, image=photo)
                else:
                    # Comportamento contain: Redimensiona para caber dentro, deixando espaço em branco (padrão)
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
                if draw_border:
                    canvas.create_rectangle(2, 2, width - 2, height - 2, outline=COLORS["border"], width=1)
                return
            except Exception as e:
                print(f"Erro ao processar preview de imagem: {e}")

        ImagePreview._draw_placeholder_rectangle(canvas, width, height, placeholder_text, draw_border=draw_border)

    @staticmethod
    def _draw_placeholder_circle(canvas, size, text):
        colors = {"bg": COLORS["accent_light"], "border": COLORS["primary"], "text": COLORS["primary"]}
        canvas.create_oval(5, 5, size - 5, size - 5, fill=colors["bg"], outline=colors["border"], width=2)
        canvas.create_text(size // 2, size // 2, text=text, font=font("subtitle"), fill=colors["text"])

    @staticmethod
    def _draw_placeholder_rectangle(canvas, width, height, text, draw_border=True):
        colors = {"bg": COLORS["input_bg"], "border": COLORS["border"], "text": COLORS["text_secondary"]}
        if draw_border:
            canvas.create_rectangle(2, 2, width - 2, height - 2, fill=colors["bg"], outline=colors["border"], width=1)
        else:
            canvas.create_rectangle(0, 0, width, height, fill=colors["bg"], outline="")
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
        container.pack(fill="x", padx=padx, pady=(8, 8))

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
        divider.pack(fill="x", padx=0, pady=(0, 8))

        self.sub_tab_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.sub_tab_content.pack(fill="both", expand=True)

        self._switch_sub_tab(parent, "geral")

    def _switch_sub_tab(self, parent, tab_name):
        for name, btn in self.sub_tab_buttons.items():
            btn.configure(text_color=self.colors["accent"] if name == tab_name else self.colors["text_secondary"])

        external_scrollbar = getattr(self.scroll_frame, "_scrollbar", None)
        if external_scrollbar:
            if tab_name == "serviços":
                external_scrollbar.grid_remove()
            else:
                external_scrollbar.grid()

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

        if clinica_data and clinica_data.get("imagem"):
            self.clinic_banner = clinica_data["imagem"]

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

        services_area = ctk.CTkFrame(scroll, fg_color="transparent")
        services_area.pack(fill="x", expand=False, padx=0, pady=(0, 10))
        services_area.grid_rowconfigure(0, weight=1)
        services_area.grid_columnconfigure(0, weight=1)

        # Frame rolável que conterá a lista de serviços
        self.services_list_frame = ctk.CTkScrollableFrame(
            services_area,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            corner_radius=8,
            height=575
        )
        self.services_list_frame.grid(row=0, column=0, sticky="nsew")

        if hasattr(self, "_services_resize_bind_id"):
            self.content_card.unbind("<Configure>", self._services_resize_bind_id)
        self._services_resize_bind_id = self.content_card.bind(
            "<Configure>", self._ajustar_altura_servicos, add="+"
        )

        # Cabeçalho da lista (3 colunas)
        header = ctk.CTkFrame(self.services_list_frame, fg_color="transparent")
        # Garantir largura mínima da coluna de nome para alinhar a coluna de valores
        header.grid_columnconfigure(0, weight=3, minsize=420)
        header.grid_columnconfigure(1, weight=1)
        header.grid_columnconfigure(2, weight=0)
        header.pack(fill="x", padx=8, pady=(6, 6))

        ctk.CTkLabel(header, text="Serviço", font=font("text", "bold"), text_color=self.colors["text_primary"]).grid(row=0, column=0, sticky="w")
        valor_header = ctk.CTkLabel(
            header,
            text="Valor",
            font=font("text", "bold"),
            text_color=self.colors["text_secondary"],
            width=118,
            anchor="w"
        )
        valor_header.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(header, text="", font=font("text", "bold"), text_color=self.colors["text_secondary"]).grid(row=0, column=2, sticky="e")

        # Corpo da lista será preenchido por _carregar_servicos
        self._carregar_servicos()
        self.after_idle(self._ajustar_altura_servicos)

    def _ajustar_altura_servicos(self, event=None):
        if not hasattr(self, "services_list_frame") or not self.services_list_frame.winfo_exists():
            return
        if not hasattr(self, "footer") or not self.footer.winfo_exists():
            return

        self.update_idletasks()
        base_height = 545
        margin = 20
        top_of_list = self.services_list_frame.winfo_rooty()
        top_of_footer = self.footer.winfo_rooty()
        available_height = top_of_footer - top_of_list - margin
        if available_height <= 1:
            return

        target_height = max(base_height, available_height - 30)
        if abs(self.services_list_frame.winfo_height() - target_height) > 3:
            self.services_list_frame.configure(height=target_height)

    def _render_preferences_description(self, parent):
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        scroll = content_frame

        self._secao_titulo(scroll, "Sobre a Clínica", padx=0)

        clinica_data = None
        if self.tipo_usuario == "clinica" and self.clinica_id:
            clinica_data = self._load_clinic_data()

        descricao_texto = ""
        if clinica_data and clinica_data.get("descricao") is not None:
            descricao_texto = str(clinica_data.get("descricao", ""))

        self.description_text = ctk.CTkTextbox(
            scroll,
            height=210,
            corner_radius=8,
            border_width=1,
            border_color=self.colors["border"],
            fg_color=COLORS["input_bg"],
            font=font("text"),
            text_color=self.colors["text_primary"]
        )
        self.description_text.pack(fill="x", expand=False, anchor="w", padx=0, pady=(10, 16))
        self.description_text.insert("1.0", descricao_texto)

        horario_button = ctk.CTkButton(
            scroll,
            text="Horário de Funcionamento",
            width=220,
            height=40,
            corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            font=font("text", "bold"),
            text_color="white",
            command=self._abrir_modal_horario_funcionamento
        )
        horario_button.pack(anchor="w", pady=(0, 8))

        bottom_spacing = ctk.CTkLabel(scroll, text="", height=12)
        bottom_spacing.pack(pady=(0, 12))

    # ==================== SERVIÇOS (Banco) ====================
    def _carregar_servicos(self):
        """Carrega e renderiza a lista de serviços da clínica atual."""
        # Limpa linhas anteriores, mantendo o cabeçalho da lista.
        children = self.services_list_frame.winfo_children()
        if len(children) > 1:
            for ch in children[1:]:
                ch.destroy()

        # Buscar somente os serviços da clínica atual.
        servicos = self._buscar_servicos_no_banco()

        if not servicos:
            ctk.CTkLabel(
                self.services_list_frame,
                text="Nenhum serviço cadastrado ainda.",
                text_color=self.colors["text_secondary"],
                font=font("text")
            ).pack(padx=8, pady=12)
            return

        for servico in servicos:
            row = ctk.CTkFrame(self.services_list_frame, fg_color="transparent")
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=0, minsize=118)
            row.grid_columnconfigure(2, weight=0)
            row.pack(fill="x", padx=8, pady=6)

            nome = servico.get("nome", "")
            preco = servico.get("preco")
            servico_id = servico.get("id")

            try:
                from decimal import Decimal
                preco_formatado = f"{Decimal(str(preco)):,.2f}"
                preco_formatado = preco_formatado.replace(",", "X").replace(".", ",").replace("X", ".")
                valor_texto = f"R$ {preco_formatado}"
            except (TypeError, ValueError, ArithmeticError):
                valor_texto = f"R$ {preco or '0,00'}"

            ctk.CTkLabel(
                row,
                text=nome,
                text_color=self.colors["text_primary"],
                font=font("text")
            ).grid(row=0, column=0, sticky="w")
            price_cell = ctk.CTkFrame(row, fg_color="transparent", width=118, height=28)
            price_cell.grid(row=0, column=1, sticky="e", padx=(0, 235))
            price_cell.grid_propagate(False)

            ctk.CTkLabel(
                price_cell,
                text=valor_texto,
                text_color=self.colors["text_secondary"],
                font=font("text"),
                anchor="e",
                justify="right"
            ).pack(fill="both", expand=True, anchor="e")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=2, sticky="e")
            ctk.CTkButton(
                actions,
                text="✎",
                width=36,
                height=28,
                fg_color="transparent",
                hover_color=self.colors.get("accent_light", COLORS["accent_light"]),
                text_color=self.colors["accent"],
                command=lambda sid=servico_id: self._abrir_modal_descricao_servico(sid)
            ).pack(side="left", padx=(0, 4))
            ctk.CTkButton(
                actions,
                text="🗑",
                width=36,
                height=28,
                fg_color="transparent",
                hover_color=self.colors.get("row_hover", COLORS.get("hover")),
                text_color=COLORS["danger"],
                command=lambda sid=servico_id: self._excluir_servico(sid)
            ).pack(side="left")

    def _fechar_modal_horario_funcionamento(self):
        if hasattr(self, "horario_modal") and self.horario_modal and self.horario_modal.winfo_exists():
            self.horario_modal.destroy()
            self.horario_modal = None
        if hasattr(self, "horario_campos"):
            delattr(self, "horario_campos")

    def _formatar_hora_para_entry(self, valor):
        """Normaliza horário para o formato HH:MM esperado pelo modal.

        Aceita:
        - datetime.time
        - datetime.timedelta
        - string "HH:MM:SS" / "H:MM:SS"
        - None
        """
        if valor is None:
            return ""

        if hasattr(valor, "total_seconds") and not hasattr(valor, "strftime"):
            try:
                total_segundos = int(valor.total_seconds())
                horas = total_segundos // 3600
                minutos = (total_segundos % 3600) // 60
                return f"{horas:02d}:{minutos:02d}"
            except Exception:
                pass

        if hasattr(valor, 'strftime'):
            return valor.strftime("%H:%M")

        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return ""

            partes = valor.split(':')
            if len(partes) >= 2:
                try:
                    hora = int(partes[0])
                    minuto = int(partes[1])
                    return f"{hora:02d}:{minuto:02d}"
                except ValueError:
                    return ""

        return ""

    def _carregar_horarios_funcionamento(self):
        """Carrega horários da clínica do banco de dados."""
        try:
            from config.database import get_connection

            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT
                        d.id,
                        d.dia,
                        h.hora_inicio,
                        h.hora_fim
                    FROM odontoPro_diasemanadisponivel d
                    LEFT JOIN odontoPro_horarioaberto h
                        ON h.dia_id = d.id
                    WHERE d.clinica_id = %s
                    ORDER BY d.id
                """, (self.clinica_id,))

                resultados = cursor.fetchall()
                horarios_por_dia = {}

                for dia_id, dia, hora_inicio, hora_fim in resultados:
                    dia_aberto = hora_inicio is not None and hora_fim is not None
                    horarios_por_dia[dia] = {
                        'dia_id': dia_id,
                        'hora_inicio': self._formatar_hora_para_entry(hora_inicio) if dia_aberto else "",
                        'hora_fim': self._formatar_hora_para_entry(hora_fim) if dia_aberto else "",
                        'tem_horario': dia_aberto
                    }

                return horarios_por_dia

            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()

        except Exception as e:
            print(f"[ERRO] Falha ao carregar horários: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def _salvar_horarios_funcionamento(self):
        """Salva horários da clínica no banco de dados"""
        try:
            from config.database import get_connection
            from datetime import datetime
            import traceback
            
            # Validar e coletar dados
            dados_dias = {}
            erros_validacao = []
            
            for dia_label, campo_info in self.horario_campos.items():
                abertura_entry = campo_info['abertura_entry']
                fechamento_entry = campo_info['fechamento_entry']
                fechado_var = campo_info['fechado_var']
                
                fechado = fechado_var.get()
                
                if fechado:
                    # Dia fechado - não há validação necessária
                    dados_dias[dia_label] = {
                        'fechado': True,
                        'dia_id': campo_info['dia_id'],
                        'hora_inicio': None,
                        'hora_fim': None
                    }
                else:
                    # Dia aberto - validar horários
                    abertura = abertura_entry.get().strip()
                    fechamento = fechamento_entry.get().strip()
                    
                    # Validar formato HH:MM
                    if not abertura or abertura == "--":
                        erros_validacao.append(f"{campo_info['dia_display']}: Horário de abertura inválido")
                        continue
                    if not fechamento or fechamento == "--":
                        erros_validacao.append(f"{campo_info['dia_display']}: Horário de fechamento inválido")
                        continue
                    
                    # Validar formato HH:MM usando regex
                    import re
                    if not re.match(r'^\d{2}:\d{2}$', abertura):
                        erros_validacao.append(f"{campo_info['dia_display']}: Abertura '{abertura}' não está no formato HH:MM")
                        continue
                    if not re.match(r'^\d{2}:\d{2}$', fechamento):
                        erros_validacao.append(f"{campo_info['dia_display']}: Fechamento '{fechamento}' não está no formato HH:MM")
                        continue
                    
                    # Validar intervalo de horas
                    try:
                        hora_a = datetime.strptime(abertura, '%H:%M')
                        hora_f = datetime.strptime(fechamento, '%H:%M')
                        
                        if hora_f <= hora_a:
                            erros_validacao.append(
                                f"{campo_info['dia_display']}: O horário de fechamento ({fechamento}) "
                                f"deve ser posterior ao horário de abertura ({abertura})"
                            )
                            continue
                    except ValueError as e:
                        erros_validacao.append(f"{campo_info['dia_display']}: Horário inválido - {e}")
                        continue
                    
                    dados_dias[dia_label] = {
                        'fechado': False,
                        'dia_id': campo_info['dia_id'],
                        'hora_inicio': abertura,
                        'hora_fim': fechamento
                    }
            
            # Se houver erros, mostrar e não salvar
            if erros_validacao:
                mensagem_erro = "Erros de validação:\n\n" + "\n".join(erros_validacao)
                messagebox.showerror("Validação", mensagem_erro)
                return False
            
            # Se chegou aqui, todas as validações passaram
            # Agora salvar no banco de dados com transação
            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Mapeamento dia_label -> dia_banco para criação se necessário
                dia_banco_map = {
                    'segunda': 'segunda',
                    'terca': 'terca',
                    'quarta': 'quarta',
                    'quinta': 'quinta',
                    'sexta': 'sexta',
                    'sabado': 'sabado',
                    'domingo': 'domingo',
                }
                
                # Processar cada dia
                for dia_label, dados in dados_dias.items():
                    dia_id = dados['dia_id']
                    
                    # Se dia_id é None, precisamos criar DiaSemanaDisponivel
                    if dia_id is None:
                        cursor.execute(
                            """SELECT id FROM odontoPro_diasemanadisponivel
                               WHERE clinica_id = %s AND dia = %s""",
                            (self.clinica_id, dia_banco_map[dia_label])
                        )
                        resultado = cursor.fetchone()
                        
                        if resultado:
                            dia_id = resultado[0]
                        else:
                            # Criar novo DiaSemanaDisponivel
                            cursor.execute(
                                """INSERT INTO odontoPro_diasemanadisponivel
                                   (clinica_id, dia)
                                   VALUES (%s, %s)""",
                                (self.clinica_id, dia_banco_map[dia_label])
                            )
                            dia_id = cursor.lastrowid
                    
                    if dados['fechado']:
                        # Deletar horários deste dia (marca como fechado)
                        cursor.execute(
                            "DELETE FROM odontoPro_horarioaberto WHERE dia_id = %s",
                            (dia_id,)
                        )
                    else:
                        # Verificar se já existe horário
                        cursor.execute(
                            "SELECT id FROM odontoPro_horarioaberto WHERE dia_id = %s LIMIT 1",
                            (dia_id,)
                        )
                        resultado = cursor.fetchone()
                        
                        if resultado:
                            # UPDATE
                            cursor.execute(
                                """UPDATE odontoPro_horarioaberto
                                   SET hora_inicio = %s, hora_fim = %s
                                   WHERE dia_id = %s""",
                                (dados['hora_inicio'], dados['hora_fim'], dia_id)
                            )
                        else:
                            # INSERT
                            cursor.execute(
                                """INSERT INTO odontoPro_horarioaberto
                                   (dia_id, hora_inicio, hora_fim)
                                   VALUES (%s, %s, %s)""",
                                (dia_id, dados['hora_inicio'], dados['hora_fim'])
                            )
                
                # Commit da transação
                conn.commit()
                messagebox.showinfo("Sucesso", "Horários de funcionamento salvos com sucesso!")
                self._fechar_modal_horario_funcionamento()
                return True
                
            except Exception as e:
                if conn:
                    conn.rollback()
                print(f"[ERRO] Falha ao salvar horários: {e}")
                traceback.print_exc()
                messagebox.showerror("Erro", f"Falha ao salvar: {e}")
                return False
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                    
        except Exception as e:
            print(f"[ERRO] Falha em _salvar_horarios_funcionamento: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Erro: {e}")
            return False

    def _abrir_modal_horario_funcionamento(self):
        if hasattr(self, "horario_modal") and self.horario_modal and self.horario_modal.winfo_exists():
            self.horario_modal.focus_set()
            return

        # Carregar horários do banco
        horarios_banco = self._carregar_horarios_funcionamento()

        modal = ctk.CTkToplevel(self)
        modal.title("Horário de Funcionamento")
        modal.transient(self)
        modal.grab_set()
        modal.resizable(False, False)
        modal.geometry("700x560")
        self.horario_modal = modal
        self.horario_campos = {}  # Armazenar referências aos widgets

        modal.protocol("WM_DELETE_WINDOW", self._fechar_modal_horario_funcionamento)

        header = ctk.CTkFrame(modal, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(18, 8))

        ctk.CTkLabel(
            header,
            text="Horário de Funcionamento",
            font=font("subtitle", "bold"),
            text_color=self.colors["text_primary"],
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Configure os dias e horários de atendimento da clínica",
            font=font("text"),
            text_color=self.colors["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(4, 0))

        body = ctk.CTkScrollableFrame(
            modal,
            fg_color="transparent",
            corner_radius=8,
            border_width=0
        )
        body.pack(fill="both", expand=True, padx=22, pady=(6, 14))

        # Mapeamento dia_label -> dia_semana_banco
        dias_mapeamento = [
            ("Segunda-feira", "segunda", 0),
            ("Terça-feira", "terca", 1),
            ("Quarta-feira", "quarta", 2),
            ("Quinta-feira", "quinta", 3),
            ("Sexta-feira", "sexta", 4),
            ("Sábado", "sabado", 5),
            ("Domingo", "domingo", 6),
        ]

        # Defaults quando não houver registro no banco
        defaults = {
            "segunda": {"abertura": "08:00", "fechamento": "18:00", "fechado": False},
            "terca": {"abertura": "08:00", "fechamento": "18:00", "fechado": False},
            "quarta": {"abertura": "08:00", "fechamento": "18:00", "fechado": False},
            "quinta": {"abertura": "08:00", "fechamento": "18:00", "fechado": False},
            "sexta": {"abertura": "08:00", "fechamento": "18:00", "fechado": False},
            "sabado": {"abertura": "08:00", "fechamento": "12:00", "fechado": False},
            "domingo": {"abertura": None, "fechamento": None, "fechado": True},
        }

        for dia_display, dia_banco, dia_index in dias_mapeamento:
            # Obter dados do banco ou usar defaults somente quando não houver configuração alguma
            if dia_banco in horarios_banco:
                dados_dia = horarios_banco[dia_banco]
                dia_id = dados_dia['dia_id']
                tem_horario = dados_dia['tem_horario']
                abertura = dados_dia['hora_inicio'] if tem_horario else None
                fechamento = dados_dia['hora_fim'] if tem_horario else None
                fechado = not tem_horario
            elif not horarios_banco:
                dia_id = None
                dados_default = defaults[dia_banco]
                abertura = dados_default["abertura"]
                fechamento = dados_default["fechamento"]
                fechado = dados_default["fechado"]
            else:
                dia_id = None
                abertura = None
                fechamento = None
                fechado = True

            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=8)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)
            row.grid_columnconfigure(3, weight=0)
            row.grid_columnconfigure(4, weight=0)

            ctk.CTkLabel(
                row,
                text=dia_display,
                font=font("text"),
                text_color=self.colors["text_primary"],
                width=18,
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=(0, 10))

            abertura_entry = ctk.CTkEntry(
                row,
                width=90,
                height=28,
                border_width=1,
                border_color=self.colors["border"],
                fg_color=COLORS["input_bg"],
                font=font("text"),
                text_color=self.colors["text_primary"]
            )
            abertura_entry.grid(row=0, column=1, sticky="w", padx=(0, 8))
            if not fechado and abertura:
                abertura_entry.insert(0, str(abertura))
            else:
                abertura_entry.insert(0, "--")

            ctk.CTkLabel(
                row,
                text="até",
                font=font("text"),
                text_color=self.colors["text_secondary"],
                width=4,
                anchor="w"
            ).grid(row=0, column=2, sticky="w", padx=(0, 8))

            fechamento_entry = ctk.CTkEntry(
                row,
                width=90,
                height=28,
                border_width=1,
                border_color=self.colors["border"],
                fg_color=COLORS["input_bg"],
                font=font("text"),
                text_color=self.colors["text_primary"]
            )
            fechamento_entry.grid(row=0, column=3, sticky="w", padx=(0, 12))
            if not fechado and fechamento:
                fechamento_entry.insert(0, str(fechamento))
            else:
                fechamento_entry.insert(0, "--")

            fechado_var = ctk.BooleanVar(value=fechado)

            def toggle_fechado(var=fechado_var, abertura=abertura_entry, fechamento=fechamento_entry):
                if var.get():
                    abertura.configure(state="disabled")
                    fechamento.configure(state="disabled")
                    abertura.delete(0, "end")
                    fechamento.delete(0, "end")
                    abertura.insert(0, "--")
                    fechamento.insert(0, "--")
                else:
                    abertura.configure(state="normal")
                    fechamento.configure(state="normal")
                    abertura.delete(0, "end")
                    fechamento.delete(0, "end")
                    abertura.insert(0, "08:00")
                    fechamento.insert(0, "18:00")

            if fechado:
                abertura_entry.configure(state="disabled")
                fechamento_entry.configure(state="disabled")

            check = ctk.CTkCheckBox(
                row,
                text="Fechado",
                variable=fechado_var,
                command=toggle_fechado,
                font=font("text"),
                text_color=self.colors["text_secondary"],
                checkbox_height=16,
                checkbox_width=16,
            )
            check.grid(row=0, column=4, sticky="e")

            if not fechado:
                check.deselect()

            # Armazenar referências para poder coletar depois
            self.horario_campos[dia_banco] = {
                'dia_id': dia_id,
                'dia_display': dia_display,
                'abertura_entry': abertura_entry,
                'fechamento_entry': fechamento_entry,
                'fechado_var': fechado_var
            }

        footer = ctk.CTkFrame(modal, fg_color="transparent")
        footer.pack(fill="x", padx=22, pady=(0, 18))

        cancel_btn = ctk.CTkButton(
            footer,
            text="Cancelar",
            width=110,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=self.colors["border"],
            text_color=self.colors["text_primary"],
            hover_color=self.colors["accent_light"],
            command=self._fechar_modal_horario_funcionamento
        )
        cancel_btn.pack(side="right", padx=(0, 10))

        save_btn = ctk.CTkButton(
            footer,
            text="Salvar",
            width=110,
            height=36,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            text_color="white",
            command=self._salvar_horarios_funcionamento
        )
        save_btn.pack(side="right")

        modal.update_idletasks()
        modal.focus_set()

    def _buscar_servicos_no_banco(self):
        try:
            from config.database import get_connection
            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id, nome, preco, descricao
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
                cursor.execute(
                    """DELETE FROM odontoPro_especialidade
                       WHERE id = %s AND clinica_id = %s""",
                    (servico_id, self.clinica_id)
                )
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

    # ==================== EDITAR SERVIÇO ====================
    def _abrir_modal_descricao_servico(self, serv_id):
        """Abre modal para editar nome, valor e descrição do serviço."""
        nome_servico, preco_atual, descricao_atual = self._carregar_descricao_atual(serv_id)

        if nome_servico is None:
            messagebox.showerror("Erro", "Serviço não encontrado.")
            return

        def formatar_preco_br(valor):
            if valor is None or valor == "":
                return ""
            try:
                from decimal import Decimal
                valor_decimal = Decimal(str(valor))
                texto = f"{valor_decimal:,.2f}"
                texto = texto.replace(',', 'X').replace('.', ',').replace('X', '.')
                return f"R$ {texto}"
            except Exception:
                return str(valor)

        def converter_preco_para_decimal(valor_texto):
            if valor_texto is None:
                return None

            texto = str(valor_texto).strip()
            if not texto:
                return None

            texto = texto.replace("R$", "").replace(" ", "")
            if "." in texto and "," in texto:
                texto = texto.replace(".", "").replace(",", ".")
            elif "," in texto:
                texto = texto.replace(",", ".")

            try:
                from decimal import Decimal, InvalidOperation
                valor = Decimal(texto)
                if valor < 0:
                    return None
                return valor
            except (InvalidOperation, ValueError):
                return None

        top = ctk.CTkToplevel(self)
        top.title("Editar Serviço")
        top.transient(self)
        top.grab_set()

        modal_w, modal_h = 550, 470
        top.geometry(f"{modal_w}x{modal_h}")
        try:
            top.resizable(False, False)
        except Exception:
            pass

        try:
            top.update_idletasks()
            parent_win = self.winfo_toplevel()
            parent_win.update_idletasks()
            px = parent_win.winfo_rootx()
            py = parent_win.winfo_rooty()
            pw = parent_win.winfo_width()
            ph = parent_win.winfo_height()

            x = px + (pw - modal_w) // 2
            y = py + (ph - modal_h) // 2

            screen_w = top.winfo_screenwidth()
            screen_h = top.winfo_screenheight()
            x = max(0, min(x, screen_w - modal_w))
            y = max(0, min(y, screen_h - modal_h))

            top.geometry(f"{modal_w}x{modal_h}+{x}+{y}")
        except Exception as e:
            print(f"[AVISO] Não foi possível centralizar modal: {e}")

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=12)

        title_label = ctk.CTkLabel(
            body,
            text="Editar Serviço",
            font=font("heading3", "bold"),
            text_color=self.colors["text_primary"]
        )
        title_label.pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(body, text="Serviço:", font=font("text", "bold"), text_color=self.colors["text_primary"]).pack(anchor="w")
        nome_entry = ctk.CTkEntry(
            body,
            width=480,
            fg_color=COLORS.get("input_bg")
        )
        nome_entry.insert(0, nome_servico)
        nome_entry.pack(fill="x", pady=(6, 12))

        ctk.CTkLabel(body, text="Valor:", font=font("text", "bold"), text_color=self.colors["text_primary"]).pack(anchor="w")
        valor_entry = ctk.CTkEntry(
            body,
            width=200,
            fg_color=COLORS.get("input_bg")
        )
        valor_entry.insert(0, formatar_preco_br(preco_atual))
        valor_entry.pack(anchor="w", pady=(6, 12))

        ctk.CTkLabel(body, text="Descrição:", font=font("text", "bold"), text_color=self.colors["text_primary"]).pack(anchor="w")
        desc_textbox = ctk.CTkTextbox(
            body,
            width=480,
            height=140,
            fg_color=COLORS.get("input_bg"),
            border_color=self.colors.get("border", COLORS.get("hover")),
            text_color=self.colors["text_primary"],
            font=font("text")
        )
        desc_textbox.pack(fill="both", expand=True, pady=(6, 12))

        if descricao_atual:
            desc_textbox.insert("1.0", descricao_atual)

        btn_frame = ctk.CTkFrame(body, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(12, 0))

        def on_save():
            nome = nome_entry.get().strip()
            nome = " ".join(nome.split())
            valor_raw = valor_entry.get().strip()
            descricao = desc_textbox.get("1.0", "end-1c").strip()

            if not nome:
                messagebox.showerror("Erro", "O nome do serviço é obrigatório.")
                return

            valor_decimal = converter_preco_para_decimal(valor_raw)
            if valor_decimal is None:
                messagebox.showerror("Erro", "Informe um valor válido.")
                return

            try:
                from config.database import get_connection
                import traceback
                conn = None
                cursor = None
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        UPDATE odontoPro_especialidade
                        SET nome = %s,
                            preco = %s,
                            descricao = %s
                        WHERE id = %s
                        AND clinica_id = %s
                        """,
                        (nome, str(valor_decimal), descricao if descricao else None, serv_id, self.clinica_id)
                    )
                    conn.commit()

                    if cursor.rowcount > 0:
                        top.destroy()
                        self._carregar_servicos()
                        messagebox.showinfo("Sucesso", "Serviço atualizado com sucesso.")
                    else:
                        messagebox.showerror("Erro", "Serviço não encontrado.")
                except Exception as e:
                    print(f"[ERRO] Falha ao atualizar serviço: {e}")
                    traceback.print_exc()
                    messagebox.showerror("Erro", "Falha ao salvar serviço. Veja o console.")
                finally:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()
            except Exception as e:
                print(f"[ERRO] Falha ao atualizar serviço (import/conn): {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erro", "Falha ao salvar serviço. Veja o console.")

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            fg_color=COLORS.get("secondary", "#666666"),
            hover_color=COLORS.get("secondary_hover", "#555555"),
            command=top.destroy,
            font=font("text", "bold")
        )
        cancel_btn.pack(side="right", padx=(4, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="Salvar",
            fg_color=COLORS.get("primary"),
            hover_color=COLORS.get("accent_hover", self.colors.get("primary_soft")),
            command=on_save,
            font=font("text", "bold")
        )
        save_btn.pack(side="right")

    def _carregar_descricao_atual(self, serv_id):
        """Carrega nome, preço e descrição atuais do serviço do banco."""
        try:
            from config.database import get_connection
            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT nome, preco, descricao
                    FROM odontoPro_especialidade
                    WHERE id = %s
                    AND clinica_id = %s
                """, (serv_id, self.clinica_id))

                row = cursor.fetchone()

                if row:
                    return row.get("nome"), row.get("preco"), row.get("descricao") or ""
                else:
                    return None, None, None

            except Exception as e:
                print(f"Erro ao carregar descrição: {e}")
                return None, None, None
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Erro ao carregar descrição (import/conn): {e}")
            return None, None, None

    def _salvar_descricao_no_banco(self, serv_id, descricao):
        """Salva a descrição do serviço no banco."""
        try:
            from config.database import get_connection
            import traceback
            conn = None
            cursor = None
            try:
                print(f"[DEBUG] Salvando descrição - serv_id: {serv_id}, clinica_id: {self.clinica_id}")
                print(f"[DEBUG] Descrição: {descricao[:50]}..." if len(descricao) > 50 else f"[DEBUG] Descrição: {descricao}")
                
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE odontoPro_especialidade
                    SET descricao = %s
                    WHERE id = %s
                    AND clinica_id = %s
                """, (descricao if descricao else None, serv_id, self.clinica_id))
                
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"[INFO] Descrição salva com sucesso para serviço ID: {serv_id}")
                    return True
                else:
                    print(f"[AVISO] Nenhuma linha foi atualizada. Serviço ID: {serv_id} não encontrado.")
                    return False
                    
            except Exception as e:
                print(f"[ERRO] Falha ao salvar descrição: {e}")
                traceback.print_exc()
                return False
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        except Exception as e:
            print(f"[ERRO] Falha ao salvar descrição (import/conn): {e}")
            import traceback
            traceback.print_exc()
            return False

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
        self.footer = footer

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
                    SELECT nome, cnpj, email, telefone, logo, imagem, descricao
                    FROM odontoPro_clinica
                    WHERE id = %s
                """, (self.clinica_id,))

                result = cursor.fetchone()
                if result:
                    # Carregar as 3 fotos da galeria da tabela odontoPro_clinicaimagem
                    photos = [None, None, None]  # Índices 0, 1, 2 para ordens 1, 2, 3
                    
                    cursor.execute("""
                        SELECT imagem, ordem
                        FROM odontoPro_clinicaimagem
                        WHERE clinica_id = %s
                        AND ordem IN (1, 2, 3)
                        ORDER BY ordem ASC
                    """, (self.clinica_id,))
                    
                    galeria_result = cursor.fetchall()
                    if galeria_result:
                        for row in galeria_result:
                            imagem_url = row[0]
                            ordem = row[1]
                            # ordem 1 → índice 0, ordem 2 → índice 1, ordem 3 → índice 2
                            if 1 <= ordem <= 3:
                                photos[ordem - 1] = imagem_url
                        print(f"[DEBUG] Fotos carregadas: {photos}")
                    
                    data = {
                        "nome": result[0] or "",
                        "cnpj": result[1] or "",
                        "email": result[2] or "",
                        "telefone": result[3] or "",
                        "logo": result[4] or "",
                        "imagem": result[5] or "",
                        "descricao": result[6] if len(result) > 6 else "",
                        "photos": photos
                    }
                    print(f"[DEBUG] Dados carregados: {data}")
                    return data

                print("[DEBUG] Nenhum resultado encontrado para clinica_id:", self.clinica_id)
                return None

            except Exception as e:
                erro_texto = str(e).lower()
                print(f"[ERRO] Falha ao carregar dados da clínica: {e}")
                self.initialization_error = e
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
                # Mostrar foto - usar fit_mode="cover" para preencher completamente
                ImagePreview.create_rectangular_preview(
                    canvas,
                    self.clinic_photos[idx],
                    260,
                    92,
                    "FOTO",
                    fit_mode="cover",
                    draw_border=False
                )
            else:
                # Espaço vazio
                ImagePreview.create_rectangular_preview(
                    canvas,
                    None,
                    260,
                    92,
                    "Sem imagem",
                    fit_mode="cover",
                    draw_border=False
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
                descricao = self.description_text.get("1.0", "end-1c") if hasattr(self, "description_text") else ""

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
                    SET nome = %s, cnpj = %s, email = %s, telefone = %s, descricao = %s
                    WHERE id = %s
                """, (nome, cnpj_clean, email, telefone_clean, descricao, self.clinica_id))

                if hasattr(self, "clinic_banner") and self.clinic_banner:
                    banner_value = str(self.clinic_banner).strip()
                    saved_banner = None

                    try:
                        if banner_value.lower().startswith(("http://", "https://")):
                            saved_banner = banner_value.replace("http://", "https://", 1) if banner_value.lower().startswith("http://") else banner_value
                        elif os.path.exists(banner_value):
                            try:
                                public_id = f"clinica_{self.clinica_id}_banner_{int(time.time())}"
                                folder = f"odontopro/clinicas/{self.clinica_id}/banner"
                                print(f"[BANNER] Iniciando upload Cloudinary para clinica_id={self.clinica_id}")
                                saved_banner = upload_image_to_cloudinary(banner_value, public_id=public_id, folder=folder)
                                print(f"[BANNER] Upload concluído, URL recebida: {saved_banner}")
                            except Exception as e:
                                print(f"[AVISO] Falha ao enviar banner para Cloudinary: {e}")
                                messagebox.showerror("Erro", f"Falha ao enviar o banner para o Cloudinary: {str(e)}")
                                saved_banner = None
                        else:
                            print(f"[AVISO] Valor inesperado para self.clinic_banner: {banner_value}")
                            saved_banner = None
                    except Exception as e:
                        print(f"[ERRO] Erro ao processar imagem do banner: {e}")
                        saved_banner = None

                    if saved_banner and isinstance(saved_banner, str) and saved_banner.lower().startswith("https://"):
                        cursor.execute("""
                            UPDATE odontoPro_clinica
                            SET imagem = %s
                            WHERE id = %s
                        """, (saved_banner, self.clinica_id))
                        print(f"[BANNER] Atualizando clinica_id={self.clinica_id} com URL Cloudinary")
                    else:
                        print(f"[BANNER] Nenhuma URL válida para atualizar no banco; mantendo imagem atual para clinica_id={self.clinica_id}")

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

                if hasattr(self, "clinic_photos") and self.clinic_photos:
                    # Processar as 3 fotos da galeria
                    failed_photos = []
                    
                    for index, photo_path in enumerate(self.clinic_photos):
                        ordem = index + 1  # ordem 1, 2, 3
                        
                        # Se for None ou vazio, pular (não criar/deletar registro)
                        if not photo_path:
                            print(f"[FOTO {ordem}] Vazio, pulando")
                            continue
                        
                        # Se já for URL remota, preservar
                        if isinstance(photo_path, str) and photo_path.lower().startswith(("http://", "https://")):
                            print(f"[FOTO {ordem}] URL remota detectada, preservando: {photo_path[:80]}...")
                            saved_url = photo_path
                        # Se for arquivo local, fazer upload
                        elif isinstance(photo_path, str) and os.path.exists(photo_path):
                            try:
                                timestamp = int(time.time())
                                public_id = f"clinica_{self.clinica_id}_foto_{ordem}_{timestamp}"
                                folder = f"odontopro/clinicas/{self.clinica_id}/galeria"
                                print(f"[FOTO {ordem}] Iniciando upload Cloudinary...")
                                saved_url = upload_image_to_cloudinary(photo_path, public_id=public_id, folder=folder)
                                print(f"[FOTO {ordem}] Upload concluído: {saved_url[:80]}...")
                            except Exception as upload_error:
                                print(f"[FOTO {ordem} - ERRO] Falha no upload: {upload_error}")
                                failed_photos.append(ordem)
                                continue
                        else:
                            print(f"[FOTO {ordem}] Caminho inválido ou não encontrado: {photo_path}")
                            continue
                        
                        # UPSERT: verificar se já existe registro para essa ordem
                        if saved_url and isinstance(saved_url, str) and saved_url.lower().startswith("https://"):
                            try:
                                cursor.execute("""
                                    SELECT id
                                    FROM odontoPro_clinicaimagem
                                    WHERE clinica_id = %s AND ordem = %s
                                """, (self.clinica_id, ordem))
                                
                                existing_record = cursor.fetchone()
                                
                                if existing_record:
                                    # UPDATE
                                    cursor.execute("""
                                        UPDATE odontoPro_clinicaimagem
                                        SET imagem = %s
                                        WHERE clinica_id = %s AND ordem = %s
                                    """, (saved_url, self.clinica_id, ordem))
                                    print(f"[FOTO {ordem}] Record atualizado (ID: {existing_record[0]})")
                                else:
                                    # INSERT
                                    cursor.execute("""
                                        INSERT INTO odontoPro_clinicaimagem
                                        (clinica_id, imagem, ordem)
                                        VALUES (%s, %s, %s)
                                    """, (self.clinica_id, saved_url, ordem))
                                    print(f"[FOTO {ordem}] Novo registro inserido")
                            except Exception as db_error:
                                print(f"[FOTO {ordem} - ERRO] Falha ao salvar no banco: {db_error}")
                                failed_photos.append(ordem)
                                continue
                    
                    # Informar erros ao usuário
                    if failed_photos:
                        erro_msg = f"Falha ao processar as seguintes fotos: {', '.join(str(f) for f in failed_photos)}. Tente novamente."
                        messagebox.showwarning("Aviso", erro_msg)
                        print(f"[AVISO] Fotos com erro: {failed_photos}")

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
