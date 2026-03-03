import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from tkinter import messagebox, filedialog
from .theme import font, ICON_SIZE

# Certifique-se que este import existe no seu projeto, senão comente as linhas de salvar/carregar
try:
    from services.permissoes_service import carregar_permissoes, salvar_permissoes
except ImportError:
    # Mock para caso o arquivo não exista durante o teste
    def carregar_permissoes(): return {}
    def salvar_permissoes(data): pass

# Configuração de aparência global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class ModernAvatar:
    """Classe utilitária para gerenciar avatares"""
    
    @staticmethod
    def create_rounded_image(img, size):
        img = img.convert("RGBA")

        # Redimensiona a imagem para o tamanho alvo com alta qualidade
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Cria uma máscara em resolução mais alta e reduz para produzir anti-aliasing suave
        scale = 4
        large_mask = Image.new('L', (size * scale, size * scale), 0)
        draw = ImageDraw.Draw(large_mask)
        draw.ellipse([0, 0, size * scale, size * scale], fill=255)
        mask = large_mask.resize((size, size), Image.Resampling.LANCZOS)

        img.putalpha(mask)
        return img
    
    @staticmethod
    def create_letter_avatar(letter, color, size):
        # Render at higher resolution and downsample for smooth anti-aliased edges
        scale = 4
        big_size = size * scale

        # Normalize color: accept "#RRGGBB" or (r,g,b) tuples
        if isinstance(color, str):
            h = color.lstrip('#')
            if len(h) == 3:
                h = ''.join(ch*2 for ch in h)
            try:
                color_rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            except Exception:
                color_rgb = (99, 102, 241)
        elif isinstance(color, (tuple, list)):
            color_rgb = tuple(int(c) for c in color[:3])
        else:
            color_rgb = (99, 102, 241)

        bg_color = (*color_rgb, 255)

        # Big canvas for drawing
        img = Image.new("RGBA", (big_size, big_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # BBoxes: inset a bit so downsampling keeps smooth edges
        inset = scale
        shadow_offset = scale  # shadow offset in big canvas
        bbox_main = [inset, inset, big_size - inset, big_size - inset]
        bbox_shadow = [inset + shadow_offset, inset + shadow_offset, big_size - inset - shadow_offset, big_size - inset - shadow_offset]

        # Draw subtle shadow and colored circle
        draw.ellipse(bbox_shadow, fill=(0, 0, 0, 90))
        draw.ellipse(bbox_main, fill=bg_color)

        # Draw centered letter with shadow
        try:
            font = ImageFont.truetype("arial.ttf", int(size * 0.6 * scale))
        except Exception:
            font = ImageFont.load_default()

        # Measure text precisely when possible
        try:
            bbox = font.getbbox(letter)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except Exception:
            text_w, text_h = draw.textsize(letter, font=font)

        text_x = (big_size - text_w) / 2
        text_y = (big_size - text_h) / 2

        # Letter shadow
        draw.text((text_x + scale // 2, text_y + scale // 2), letter, font=font, fill=(0, 0, 0, 140))
        # Letter foreground (white)
        draw.text((text_x, text_y), letter, font=font, fill=(255, 255, 255, 255))

        # Circular mask (drawn at big resolution for anti-aliasing) and apply as alpha
        mask = Image.new("L", (big_size, big_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(bbox_main, fill=255)
        img.putalpha(mask)

        # Downsample to target size with high-quality resampling
        final = img.resize((size, size), Image.Resampling.LANCZOS)
        return final


class AdminListFrame(ctk.CTkFrame):
    def __init__(self, master, admins_data, on_click_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_click_callback = on_click_callback
        self.admins_data = admins_data
        self.admin_rows = [] 
        self.avatar_labels = {} 
        self.current_page = 1
        self.items_per_page = 5
        self.selected_row_frame = None 

        # Configuração do Grid Principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- CONFIGURAÇÃO DAS COLUNAS ---
        self.col_config = {
            0: {"weight": 0, "minsize": 80},   # Avatar
            1: {"weight": 2, "minsize": 150},  # Nome
            2: {"weight": 3, "minsize": 180},  # Email
            3: {"weight": 1, "minsize": 120},  # Nível
            4: {"weight": 0, "minsize": 100},  # Status
        }

        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        # --- Cabeçalho com gradiente ---
        header_content = ctk.CTkFrame(self, fg_color="transparent")
        header_content.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="ew")
        
        # Título com ícone
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(title_frame, text="👥", font=font(ICON_SIZE)).pack(side="left", padx=(0, 10))
        self.lbl_title = ctk.CTkLabel(
            title_frame, 
            text="Administradores", 
            font=font("subtitle", "bold"), 
            text_color="#1E293B"
        )
        self.lbl_title.pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            header_content, 
            text=f"{len(self.admins_data)} ativos", 
            text_color="#64748B", 
            font=font("small")
        )
        self.lbl_count.pack(side="left", padx=15)

        # Botão de refresh (opcional)
        self.btn_refresh = ctk.CTkButton(
            header_content,
            text="↻",
            width=36,
            height=36,
            font=font("text"),
            fg_color="transparent",
            text_color="#64748B",
            hover_color="#F1F5F9",
            corner_radius=8,
            command=self.refresh_list
        )
        self.btn_refresh.pack(side="right")

        # --- Frame da Tabela ---
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # --- Cabeçalho da Tabela ---
        header_bg = ctk.CTkFrame(
            table_container, 
            fg_color="#F8FAFC", 
            height=48, 
            corner_radius=10
        )
        header_bg.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 8))
        header_bg.grid_propagate(False) 
        
        # Aplica configuração no Header
        for col_idx, conf in self.col_config.items():
            header_bg.grid_columnconfigure(col_idx, weight=conf["weight"], minsize=conf["minsize"])

        headers = ["", "Nome", "Email", "Nível", "Status"]
        anchors = ["center", "w", "w", "w", "center"]

        for i, text in enumerate(headers):
            ctk.CTkLabel(
                header_bg, 
                text=text, 
                font=font("small", "bold"), 
                text_color="#475569",
                anchor=anchors[i]
            ).grid(row=0, column=i, sticky="ew", padx=(15 if i == 0 else 10, 10), pady=12)

        # --- Lista rolável ---
        self.scroll_list = ctk.CTkFrame(table_container, fg_color="transparent")
        self.scroll_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        self.scroll_list.grid_columnconfigure(0, weight=1) 

        # --- Rodapé com Paginação ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=15, height=70)
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.footer_frame.grid_propagate(False)

        footer_content = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=20)

        self.lbl_pagination = ctk.CTkLabel(
            footer_content, 
            text="", 
            font=font("small"), 
            text_color="#475569"
        )
        self.lbl_pagination.pack(side="left")

        buttons_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        buttons_frame.pack(side="right")

        # Botões de paginação estilizados
        self.btn_anterior = ctk.CTkButton(
            buttons_frame, 
            text="← Anterior", 
            width=100, 
            height=36, 
            font=font("small"), 
            fg_color="white", 
            border_width=1, 
            border_color="#E2E8F0", 
            text_color="#334155", 
            hover_color="#F1F5F9",
            corner_radius=8,
            command=self.previous_page
        )
        self.btn_anterior.pack(side="left", padx=5)

        self.btn_proximo = ctk.CTkButton(
            buttons_frame, 
            text="Próximo →", 
            width=100, 
            height=36, 
            font=font("small"), 
            fg_color="white", 
            border_width=1, 
            border_color="#E2E8F0", 
            text_color="#334155", 
            hover_color="#F1F5F9",
            corner_radius=8,
            command=self.next_page
        )
        self.btn_proximo.pack(side="left", padx=5)

    def refresh_list(self):
        """Atualiza a lista de administradores"""
        self.lbl_count.configure(text=f"{len(self.admins_data)} ativos")
        self.populate_list()

    def populate_list(self):
        for widget in self.scroll_list.winfo_children():
            widget.destroy()
        
        self.admin_rows = []
        self.selected_row_frame = None 

        admin_list = list(self.admins_data.items())
        total_pages = max(1, (len(admin_list) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = admin_list[start_idx:end_idx]

        self.lbl_pagination.configure(text=f"Página {self.current_page} de {total_pages}")
        self.btn_anterior.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_proximo.configure(state="normal" if self.current_page < total_pages else "disabled")

        for index, (nome, info) in enumerate(page_data):
            self.create_admin_row(nome, info, index)

    def create_admin_row(self, nome, info, index):
        row_frame = ctk.CTkFrame(
            self.scroll_list, 
            fg_color="transparent", 
            corner_radius=8, 
            height=60
        )
        row_frame.pack(fill="x", pady=2, padx=0)
        row_frame.pack_propagate(False)
        
        for col_idx, conf in self.col_config.items():
            row_frame.grid_columnconfigure(col_idx, weight=conf["weight"], minsize=conf["minsize"])

        def on_row_click(event=None):
            self.highlight_row(row_frame)
            self.on_click_callback(None, nome)

        row_frame.bind("<Button-1>", on_row_click)
        row_frame.configure(cursor="hand2")
        self.admin_rows.append(row_frame)

        # --- Avatar (Coluna 0) ---
        colors = [
            "#EF4444", "#F97316", "#EAB308", "#22C55E", 
            "#3B82F6", "#8B5CF6", "#EC4899", "#6366F1"
        ]
        color_hex = colors[hash(nome) % len(colors)]
        color_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        if "photo_path" in info and os.path.exists(info["photo_path"]):
            try:
                img = Image.open(info["photo_path"])
                # Use ImageOps.fit para crop+resize com boa qualidade e centralização
                img = ImageOps.fit(img, (36, 36), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                img = ModernAvatar.create_rounded_image(img, 36)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 36))
            except:
                letter_img = ModernAvatar.create_letter_avatar(nome[0].upper(), color_rgb, 36)
                ctk_img = ctk.CTkImage(light_image=letter_img, dark_image=letter_img, size=(36, 36))
        else:
            letter_img = ModernAvatar.create_letter_avatar(nome[0].upper(), color_rgb, 36)
            ctk_img = ctk.CTkImage(light_image=letter_img, dark_image=letter_img, size=(36, 36))

        avatar_label = ctk.CTkLabel(
            row_frame, 
            image=ctk_img, 
            text="",
            cursor="hand2"
        )
        avatar_label.grid(row=0, column=0, padx=15, pady=10)
        # Keep a reference to the CTkImage to prevent GC from removing it
        avatar_label.image = ctk_img
        avatar_label.bind("<Button-1>", lambda e: self.upload_photo(nome)) 
        self.avatar_labels[nome] = avatar_label

        # --- Labels de Texto ---
        nome_label = ctk.CTkLabel(
            row_frame, 
            text=nome, 
            font=font("text", "bold"), 
            text_color="#0F172A", 
            anchor="w"
        )
        nome_label.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        nome_label.bind("<Button-1>", on_row_click)

        email = info.get("email", "sem@email.com")
        email_label = ctk.CTkLabel(
            row_frame, 
            text=email, 
            font=font("small"), 
            text_color="#475569", 
            anchor="w"
        )
        email_label.grid(row=0, column=2, sticky="w", padx=10, pady=10)
        email_label.bind("<Button-1>", on_row_click)

        level = info.get("level", "Nível não definido")
        nivel_label = ctk.CTkLabel(
            row_frame, 
            text=level, 
            font=font("small"), 
            text_color="#475569", 
            anchor="w"
        )
        nivel_label.grid(row=0, column=3, sticky="w", padx=10, pady=10)
        nivel_label.bind("<Button-1>", on_row_click)

        # --- Status (Coluna 4) ---
        status = info.get("status", "Ativo")
        status_config = {
            "Ativo": {"color": "#22C55E", "bg": "#F0FDF4", "icon": "●"},
            "Pendente": {"color": "#F59E0B", "bg": "#FFFBEB", "icon": "●"},
            "Inativo": {"color": "#EF4444", "bg": "#FEF2F2", "icon": "●"}
        }
        config = status_config.get(status, status_config["Ativo"])
        
        status_frame = ctk.CTkFrame(
            row_frame, 
            fg_color=config["bg"], 
            corner_radius=20,
            height=28
        )
        status_frame.grid(row=0, column=4, padx=10, pady=10)
        status_frame.bind("<Button-1>", on_row_click)
        
        status_label = ctk.CTkLabel(
            status_frame, 
            text=f"{config['icon']} {status}", 
            font=font("small", "bold"), 
            text_color=config["color"],
            padx=10
        )
        status_label.pack(pady=4)
        status_label.bind("<Button-1>", on_row_click)

    def highlight_row(self, frame_to_select):
        if self.selected_row_frame is not None:
            try:
                self.selected_row_frame.configure(fg_color="transparent")
            except:
                pass 
        frame_to_select.configure(fg_color="#EFF6FF") 
        self.selected_row_frame = frame_to_select

    def next_page(self):
        admin_list = list(self.admins_data.items())
        total_pages = max(1, (len(admin_list) + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.populate_list()

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.populate_list()

    def upload_photo(self, admin_name, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.admins_data[admin_name]["photo_path"] = file_path
            try:
                img = Image.open(file_path)
                # Use ImageOps.fit para crop+resize com boa qualidade e centralização
                img = ImageOps.fit(img, (36, 36), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                img = ModernAvatar.create_rounded_image(img, 36)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 36))

                avatar_label = self.avatar_labels.get(admin_name)
                if avatar_label:
                    avatar_label.configure(image=ctk_img)
                    # Keep a reference to the CTkImage to prevent GC
                    avatar_label.image = ctk_img

                messagebox.showinfo("Sucesso", f"Foto de {admin_name} atualizada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar imagem: {str(e)}")


class Permissoes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#F1F5F9")

        self.grid_columnconfigure(0, weight=4)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        self.selected_admin_name = None
        self.switch_widgets = {}
        self.permissions_list = ["Painel", "Agenda", "Financeiro", "Configurações", "Cadastro", "Permissões"]

        try:
            dados = carregar_permissoes()
            self.admins_data = dados if dados and isinstance(dados, dict) else self.get_default_data()
        except Exception:
            self.admins_data = self.get_default_data()

        self.setup_ui()

    def get_default_data(self):
        return {
            "John Doe": {
                "level": "Admin", 
                "email": "john.doe@email.com", 
                "status": "Ativo", 
                "perms": {p: True for p in self.permissions_list}
            },
            "Jane Smith": {
                "level": "Billing", 
                "email": "jane.smith@email.com", 
                "status": "Ativo", 
                "perms": {p: True for p in self.permissions_list[:3]}
            },
            "Alice Brown": {
                "level": "Reporting", 
                "email": "alice.b@email.com", 
                "status": "Ativo", 
                "perms": {p: False for p in self.permissions_list}
            },
            "Locaritn Ltrntan": {
                "level": "Somente Leitura", 
                "email": "loc@email.com", 
                "status": "Pendente", 
                "perms": {p: False for p in self.permissions_list}
            },
        }

    def setup_ui(self):
        # COLUNA ESQUERDA
        self.admin_list_panel = AdminListFrame(
            self, 
            admins_data=self.admins_data, 
            on_click_callback=self.on_admin_click, 
            fg_color="white", 
            corner_radius=20
        )
        self.admin_list_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # COLUNA DIREITA
        self.right_card = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_card.grid_rowconfigure(2, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        # Cabeçalho do card direito
        header_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10), padx=25)
        
        ctk.CTkLabel(
            header_frame, 
            text="🔐", 
            font=font(28)
        ).pack(side="left", padx=(0, 15))
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(
            title_frame, 
            text="Permissões", 
            font=font("subtitle", "bold"), 
            text_color="#0F172A",
            anchor="w"
        ).pack(anchor="w")
        
        self.selected_admin_label = ctk.CTkLabel(
            title_frame, 
            text="Nenhum administrador selecionado", 
            font=font("small"), 
            text_color="#64748B",
            anchor="w"
        )
        self.selected_admin_label.pack(anchor="w")

        # Área de permissões - AGORA SEM SCROLLBAR
        self.permissions_container = ctk.CTkFrame(
            self.right_card, 
            fg_color="transparent"
        )
        self.permissions_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # Configurar 2 colunas para os cards
        self.permissions_container.grid_columnconfigure(0, weight=1)
        self.permissions_container.grid_columnconfigure(1, weight=1)
        
        # Mapeamento de ícones e descrições
        permissions_config = {
            "Painel": {"icon": "📊", "desc": "Acesso ao dashboard", "color": "#3B82F6"},
            "Agenda": {"icon": "📅", "desc": "Gerenciar eventos", "color": "#8B5CF6"},
            "Financeiro": {"icon": "💰", "desc": "Transações e relatórios", "color": "#10B981"},
            "Configurações": {"icon": "⚙️", "desc": "Configurações do sistema", "color": "#F59E0B"},
            "Cadastro": {"icon": "📝", "desc": "CRUD de usuários", "color": "#EF4444"},
            "Permissões": {"icon": "🔐", "desc": "Controle de acesso", "color": "#EC4899"}
        }

        for index, perm_name in enumerate(self.permissions_list):
            row, col = divmod(index, 2)
            config = permissions_config.get(perm_name, {"icon": "🛡️", "desc": "", "color": "#64748B"})
            
            # Card de permissão - COM ALTURA REDUZIDA PARA CABER NA TELA
            card = ctk.CTkFrame(
                self.permissions_container, 
                fg_color="#F8FAFC", 
                corner_radius=16,
                border_width=1,
                border_color="#E2E8F0",
                height=85
            )
            card.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            card.grid_propagate(False)
            card.grid_columnconfigure(2, weight=1)

            # Ícone colorido
            icon_frame = ctk.CTkFrame(
                card, 
                fg_color="#F1F5F9",
                width=44, 
                height=44,
                corner_radius=12
            )
            icon_frame.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)
            icon_frame.grid_propagate(False)
            
            ctk.CTkLabel(
                icon_frame, 
                text=config["icon"], 
                font=font(ICON_SIZE),
                text_color=config['color']
            ).place(relx=0.5, rely=0.5, anchor="center")

            # Nome da permissão
            ctk.CTkLabel(
                card, 
                text=perm_name, 
                font=font("text", "bold"), 
                text_color="#0F172A"
            ).grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(10, 0))

            # Descrição
            ctk.CTkLabel(
                card, 
                text=config["desc"], 
                font=font("small"), 
                text_color="#64748B"
            ).grid(row=1, column=1, sticky="w", padx=(0, 5), pady=(0, 10))

            # Switch
            sw = ctk.CTkSwitch(
                card, 
                text="", 
                width=40, 
                height=22, 
                progress_color=config['color'],
                button_color="white",
                button_hover_color="#F1F5F9",
                command=lambda p=perm_name: self.sync_permission(p)
            )
            sw.grid(row=0, column=2, rowspan=2, padx=(5, 15), sticky="e")
            self.switch_widgets[perm_name] = sw

        # Botão Salvar
        button_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(0, 25))
        
        self.save_btn = ctk.CTkButton(
            button_frame, 
            text="💾 Salvar Alterações", 
            font=font("text", "bold"), 
            fg_color="#2563EB", 
            height=48, 
            width=260, 
            corner_radius=12,
            hover_color="#0EA5E9",
            command=self.save_to_database
        )
        self.save_btn.pack()

        self.toggle_switches_state("disabled")

    def on_admin_click(self, frame, admin_name):
        self.selected_admin_name = admin_name
        self.selected_admin_label.configure(text=f"Configurando: {admin_name}")
        self.toggle_switches_state("normal")

        admin_perms = self.admins_data[admin_name].get("perms", {})
        for p_name in self.permissions_list:
            if admin_perms.get(p_name, False): 
                self.switch_widgets[p_name].select()
            else: 
                self.switch_widgets[p_name].deselect()

    def sync_permission(self, perm_name):
        if self.selected_admin_name:
            if "perms" not in self.admins_data[self.selected_admin_name]:
                self.admins_data[self.selected_admin_name]["perms"] = {}
            self.admins_data[self.selected_admin_name]["perms"][perm_name] = bool(self.switch_widgets[perm_name].get())

    def toggle_switches_state(self, state):
        for sw in self.switch_widgets.values(): 
            sw.configure(state=state)

    def save_to_database(self):
        salvar_permissoes(self.admins_data)
        messagebox.showinfo("Sucesso", "✅ Permissões salvas com sucesso!")
        self.admin_list_panel.refresh_list()