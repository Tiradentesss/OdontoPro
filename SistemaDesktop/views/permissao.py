import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from tkinter import messagebox, filedialog
from .base import BaseScreen
from .theme import COLORS, font, ICON_SIZE
from controllers.gerenciamento_controller import GerenciamentoController


class ImagePreview:
    """Classe utilitária para gerenciar previews de imagens"""

    @staticmethod
    def create_circular_preview(canvas, image_path, size=36, placeholder_text="A"):
        canvas.delete("all")
        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img = img.resize((size, size), Image.Resampling.LANCZOS)
                mask = Image.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                img.putalpha(mask)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                return ctk_img
            except Exception as e:
                print(f"Erro ao carregar imagem: {e}")
                return None
        return None


class ModernAvatar:
    """Classe utilitária para gerenciar avatares"""

    @staticmethod
    def create_rounded_image(img, size):
        img = img.convert("RGBA")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        scale = 4
        large_mask = Image.new('L', (size * scale, size * scale), 0)
        draw = ImageDraw.Draw(large_mask)
        draw.ellipse([0, 0, size * scale, size * scale], fill=255)
        mask = large_mask.resize((size, size), Image.Resampling.LANCZOS)
        img.putalpha(mask)
        return img

    @staticmethod
    def create_letter_avatar(letter, color, size):
        scale = 4
        big_size = size * scale
        if isinstance(color, str):
            h = color.lstrip('#')
            if len(h) == 3:
                h = ''.join(ch * 2 for ch in h)
            try:
                color_rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
            except Exception:
                color_rgb = (99, 102, 241)
        elif isinstance(color, (tuple, list)):
            color_rgb = tuple(int(c) for c in color[:3])
        else:
            color_rgb = (99, 102, 241)

        bg_color = (*color_rgb, 255)
        img = Image.new("RGBA", (big_size, big_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        inset = scale
        shadow_offset = scale
        bbox_main = [inset, inset, big_size - inset, big_size - inset]
        bbox_shadow = [inset + shadow_offset, inset + shadow_offset,
                       big_size - inset - shadow_offset, big_size - inset - shadow_offset]
        draw.ellipse(bbox_shadow, fill=(0, 0, 0, 90))
        draw.ellipse(bbox_main, fill=bg_color)
        try:
            font_img = ImageFont.truetype("arial.ttf", int(size * 0.6 * scale))
        except Exception:
            font_img = ImageFont.load_default()
        try:
            bbox = font_img.getbbox(letter)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except Exception:
            text_w, text_h = draw.textsize(letter, font=font_img)
        text_x = (big_size - text_w) / 2
        text_y = (big_size - text_h) / 2
        draw.text((text_x + scale // 2, text_y + scale // 2), letter, font=font_img, fill=(0, 0, 0, 140))
        draw.text((text_x, text_y), letter, font=font_img, fill=(255, 255, 255, 255))
        mask = Image.new("L", (big_size, big_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(bbox_main, fill=255)
        img.putalpha(mask)
        final = img.resize((size, size), Image.Resampling.LANCZOS)
        return final


class AdminListFrame(ctk.CTkFrame):
    """Lista de administradores com badges de status em formato de pílula"""

    # Configuração das colunas: pesos e tamanhos mínimos para espaçamento uniforme
    COL_CONFIG = {
        0: {"weight": 0, "minsize": 56},   # avatar - fixo
        1: {"weight": 0, "minsize": 130},  # Nome - sem expansão para evitar gaps desiguais
        2: {"weight": 1, "minsize": 130},  # Email - expande para usar espaço restante
        3: {"weight": 0, "minsize": 110},  # Status - fixo, menor para não comprimir Nome
    }

    def __init__(self, master, admins_data, on_click_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_click_callback = on_click_callback
        self.admins_data = admins_data
        self.admin_rows = []
        self.avatar_labels = {}
        self.current_page = 1
        self.items_per_page = 5
        self.selected_row_frame = None

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup_ui()
        self.populate_list()

    def _apply_col_config(self, widget):
        for col_idx, conf in self.COL_CONFIG.items():
            widget.grid_columnconfigure(col_idx, weight=conf["weight"], minsize=conf["minsize"])

    def setup_ui(self):
        header_content = ctk.CTkFrame(self, fg_color="transparent")
        header_content.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text="👥", font=font(ICON_SIZE)).pack(side="left", padx=(0, 10))
        self.lbl_title = ctk.CTkLabel(
            title_frame, text="Administradores",
            font=font("subtitle", "bold"), text_color=COLORS["text"]
        )
        self.lbl_title.pack(side="left")
        self.lbl_count = ctk.CTkLabel(
            header_content, text=f"{len(self.admins_data)} ativos",
            text_color=COLORS["muted"], font=font("small")
        )
        self.lbl_count.pack(side="left", padx=15)
        self.btn_refresh = ctk.CTkButton(
            header_content, text="↻", width=36, height=36, font=font("text"),
            fg_color="transparent", text_color=COLORS["muted"],
            hover_color=COLORS["hover"], corner_radius=8, command=self.refresh_list
        )
        self.btn_refresh.pack(side="right")

        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        self.header_bg = ctk.CTkFrame(
            table_container, fg_color=COLORS["content_bg"], height=44, corner_radius=10
        )
        self.header_bg.grid(row=0, column=0, sticky="ew", padx=12, pady=(0, 6))
        self.header_bg.grid_propagate(False)
        self._apply_col_config(self.header_bg)

        # Cabeçalhos com padding horizontal uniforme
        headers = ["", "Nome", "Email", "Status"]
        anchors = ["center", "w", "w", "center"]  # Email alinhado à esquerda para acompanhar os itens
        stickys = ["nsew", "w", "w", "w"]  # Avatar expande, Email e Status alinhados à esquerda
        padx_map = {
            0: (12, 8),   # avatar: espaço à esquerda
            1: (8, 8),    # Nome: espaço equilibrado
            2: (8, 8),    # Email: espaço equilibrado
            3: (20, 8),   # Status: deslocado mais para a direita para centralizar visualmente
        }
        for i, text in enumerate(headers):
            ctk.CTkLabel(
                self.header_bg, text=text,
                font=font("small", "bold"),
                text_color=COLORS["text_secondary"],
                anchor=anchors[i]
            ).grid(row=0, column=i, sticky=stickys[i], padx=padx_map[i], pady=10)

        self.scroll_list = ctk.CTkFrame(table_container, fg_color="transparent")
        self.scroll_list.grid(row=1, column=0, sticky="nsew", padx=12, pady=0)

        self.footer_frame = ctk.CTkFrame(
            self, fg_color=COLORS["content_bg"], corner_radius=15, height=70
        )
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.footer_frame.grid_propagate(False)
        footer_content = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=20)

        self.lbl_pagination = ctk.CTkLabel(
            footer_content, text="", font=font("small"), text_color=COLORS["text_secondary"]
        )
        self.lbl_pagination.pack(side="left", pady=17)

        buttons_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        buttons_frame.pack(side="right", pady=17)
        self.btn_anterior = ctk.CTkButton(
            buttons_frame, text="← Anterior", width=100, height=36, font=font("small"),
            fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"],
            text_color=COLORS["text"], hover_color=COLORS["hover"],
            corner_radius=8, command=self.previous_page
        )
        self.btn_anterior.pack(side="left", padx=5)
        self.btn_proximo = ctk.CTkButton(
            buttons_frame, text="Próximo →", width=100, height=36, font=font("small"),
            fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"],
            text_color=COLORS["text"], hover_color=COLORS["hover"],
            corner_radius=8, command=self.next_page
        )
        self.btn_proximo.pack(side="left", padx=5)

    def refresh_list(self):
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
        row_frame.pack(fill="x", pady=2)
        row_frame.pack_propagate(False)

        self._apply_col_config(row_frame)
        row_frame.grid_rowconfigure(0, weight=1)

        def on_row_click(event=None):
            self.highlight_row(row_frame)
            self.on_click_callback(None, nome)

        row_frame.bind("<Button-1>", on_row_click)
        row_frame.configure(cursor="hand2")
        self.admin_rows.append(row_frame)

        colors = [
            COLORS["danger"],
            COLORS["warning"],
            COLORS["warning"],
            COLORS["success"],
            COLORS["accent"],
            COLORS["secondary"],
            COLORS["accent"],
            COLORS["secondary"]
        ]

        color_hex = colors[hash(nome) % len(colors)]
        color_rgb = tuple(
            int(color_hex.lstrip('#')[i:i + 2], 16)
            for i in (0, 2, 4)
        )

        # =========================================================
        # AVATAR
        # =========================================================
        if "photo_path" in info and os.path.exists(info["photo_path"]):
            try:
                img = Image.open(info["photo_path"])

                img = ImageOps.fit(
                    img,
                    (36, 36),
                    Image.Resampling.LANCZOS,
                    centering=(0.5, 0.5)
                )

                img = ModernAvatar.create_rounded_image(img, 36)

                ctk_img = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(36, 36)
                )

            except Exception:
                letter_img = ModernAvatar.create_letter_avatar(
                    nome[0].upper(),
                    color_rgb,
                    36
                )

                ctk_img = ctk.CTkImage(
                    light_image=letter_img,
                    dark_image=letter_img,
                    size=(36, 36)
                )

        else:
            letter_img = ModernAvatar.create_letter_avatar(
                nome[0].upper(),
                color_rgb,
                36
            )

            ctk_img = ctk.CTkImage(
                light_image=letter_img,
                dark_image=letter_img,
                size=(36, 36)
            )

        avatar_label = ctk.CTkLabel(
            row_frame,
            image=ctk_img,
            text="",
            cursor="hand2"
        )

        avatar_label.grid(
            row=0,
            column=0,
            padx=(12, 8),
            pady=0,
            sticky="ns"
        )

        avatar_label.image = ctk_img
        avatar_label.bind("<Button-1>", lambda e: self.upload_photo(nome))
        self.avatar_labels[nome] = avatar_label

        # =========================================================
        # NOME
        # =========================================================
        nome_label = ctk.CTkLabel(
            row_frame,
            text=nome,
            font=font("text", "bold"),
            text_color=COLORS["text"],
            anchor="w"
        )

        nome_label.grid(
            row=0,
            column=1,
            sticky="w",  # Alinhado à esquerda (sem expansão vertical)
            padx=(8, 8),
            pady=0
        )

        nome_label.bind("<Button-1>", on_row_click)

        # =========================================================
        # EMAIL
        # =========================================================
        email = info.get("email", "sem@email.com")

        email_label = ctk.CTkLabel(
            row_frame,
            text=email,
            font=font("small"),
            text_color=COLORS["text_secondary"],
            anchor="center"
        )

        email_label.grid(
            row=0,
            column=2,
            sticky="w",  # Sem expansão, alinhado à esquerda
            padx=(8, 8),
            pady=0
        )

        email_label.bind("<Button-1>", on_row_click)

        # =========================================================
        # STATUS
        # =========================================================
        status = info.get("status", "Ativo")

        status_cfg_map = {
            "Ativo": {
                "color": COLORS["success"],
                "bg": COLORS["success_light"],
                "icon": "●"
            },

            "Pendente": {
                "color": COLORS["warning"],
                "bg": COLORS["warning_light"],
                "icon": "●"
            },

            "Inativo": {
                "color": COLORS["danger"],
                "bg": COLORS["danger_light"],
                "icon": "●"
            },
        }

        cfg = status_cfg_map.get(status, status_cfg_map["Ativo"])

        # Container centralizador para manter o badge pequeno e centralizado
        status_container = ctk.CTkFrame(
            row_frame,
            fg_color="transparent"
        )
        status_container.grid(
            row=0,
            column=3,
            sticky="w",  # Sem expansão, alinhado à esquerda
            padx=(8, 8),
            pady=0
        )

        status_badge = ctk.CTkLabel(
            status_container,
            text=f"{cfg['icon']} {status}",
            font=font("small", "bold"),
            text_color=cfg["color"],
            fg_color=cfg["bg"],
            corner_radius=20,
            anchor="center"
        )

        status_badge.grid(row=0, column=0)

        status_badge.bind("<Button-1>", on_row_click)

    def highlight_row(self, frame_to_select):
        if self.selected_row_frame is not None:
            try:
                self.selected_row_frame.configure(fg_color="transparent")
            except Exception:
                pass
        frame_to_select.configure(fg_color=COLORS["selected_row"])
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
        file_path = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            self.admins_data[admin_name]["photo_path"] = file_path
            try:
                img = Image.open(file_path)
                img = ImageOps.fit(img, (36, 36), Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                img = ModernAvatar.create_rounded_image(img, 36)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(36, 36))
                avatar_label = self.avatar_labels.get(admin_name)
                if avatar_label:
                    avatar_label.configure(image=ctk_img)
                    avatar_label.image = ctk_img
                messagebox.showinfo("Sucesso", f"Foto de {admin_name} atualizada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar imagem: {str(e)}")


class Permissoes(BaseScreen):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, "Permissões")
        self.clinica_id = clinica_id

        resultado_perms = GerenciamentoController.inicializar_permissoes_padrao()
        if not resultado_perms.get("sucesso"):
            print(f"[AVISO PERMISSÃO] Falha ao inicializar permissões: {resultado_perms.get('mensagem')}")

        self.content_card.grid_columnconfigure(0, weight=4)
        self.content_card.grid_columnconfigure(1, weight=5)
        self.content_card.grid_rowconfigure(0, weight=1)

        self.selected_admin_name = None
        self.selected_admin_id = None
        self.switch_widgets = {}
        self.permissions_list = [
            "Painel", "Agenda", "Financeiro", "Configurações",
            "Cadastro", "Gerenciamento", "Permissões"
        ]

        self.admins_data = self.load_gerentes_from_database()
        self.setup_ui()

    def load_gerentes_from_database(self):
        try:
            gerentes_bd = GerenciamentoController.listar_todos_gerentes_por_clinica(self.clinica_id)
            if not gerentes_bd:
                print("Nenhum gerente encontrado para esta clínica")
                return self.get_default_data()

            permissoes_bd = GerenciamentoController.listar_permissoes_disponiveis()
            permissao_map = {p['codigo']: p['id'] for p in permissoes_bd}

            admins = {}
            for gerente in gerentes_bd:
                gerente_id = gerente['id']
                gerentes_perms_bd = GerenciamentoController.obter_permissoes_gerente(gerente_id)
                perms_dict = {}
                for perm in self.permissions_list:
                    tem_permissao = any(p['codigo'] == perm for p in gerentes_perms_bd)
                    perms_dict[perm] = tem_permissao
                status = "Ativo" if gerente['ativo'] == 1 else "Inativo"
                admins[gerente['nome']] = {
                    "id": gerente_id,
                    "level": "Gerente",
                    "email": gerente['email'],
                    "status": status,
                    "perms": perms_dict
                }
            return admins if admins else self.get_default_data()
        except Exception as e:
            print(f"Erro ao carregar gerentes do BD: {e}")
            import traceback
            traceback.print_exc()
            return self.get_default_data()

    def get_default_data(self):
        return {
            "John Doe": {
                "id": 1, "level": "Admin", "email": "john.doe@email.com", "status": "Ativo",
                "perms": {p: True for p in self.permissions_list}
            },
            "Jane Smith": {
                "id": 2, "level": "Billing", "email": "jane.smith@email.com", "status": "Ativo",
                "perms": {p: True for p in self.permissions_list[:3]}
            },
            "Alice Brown": {
                "id": 3, "level": "Reporting", "email": "alice.b@email.com", "status": "Ativo",
                "perms": {p: False for p in self.permissions_list}
            },
            "Carlos Mendes": {
                "id": 4, "level": "Financeiro", "email": "carlos.mendes@email.com", "status": "Ativo",
                "perms": {
                    "Painel": True, "Agenda": False, "Financeiro": True,
                    "Configurações": False, "Cadastro": False,
                    "Gerenciamento": False, "Permissões": False
                }
            },
        }

    def setup_ui(self):
        self.admin_list_panel = AdminListFrame(
            self.content_card, admins_data=self.admins_data,
            on_click_callback=self.on_admin_click,
            fg_color=COLORS["card"], corner_radius=20
        )
        self.admin_list_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        self.right_card = ctk.CTkFrame(self.content_card, fg_color=COLORS["card"], corner_radius=20)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.right_card.grid_rowconfigure(1, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        header_bg = ctk.CTkFrame(self.right_card, fg_color="transparent")
        header_bg.grid(row=0, column=0, sticky="ew", pady=(30, 10), padx=25)
        header_content = ctk.CTkFrame(header_bg, fg_color="transparent")
        header_content.pack(fill="x")
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left")
        self.icon_label = ctk.CTkLabel(title_frame, text="🔐", font=font(ICON_SIZE))
        self.icon_label.pack(side="left", padx=(0, 12))
        self.title_label = ctk.CTkLabel(
            title_frame, text="Permissões",
            font=font("subtitle", "bold"), text_color=COLORS["text"]
        )
        self.title_label.pack(side="left")
        self.selected_admin_label = ctk.CTkLabel(
            title_frame, text="Nenhum administrador selecionado",
            font=font("small"), text_color=COLORS["muted"]
        )
        self.selected_admin_label.pack(side="left", padx=15)

        self.permissions_container = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.permissions_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=10)
        self.permissions_container.grid_columnconfigure(0, weight=1, minsize=210)
        self.permissions_container.grid_columnconfigure(1, weight=1, minsize=210)

        permissions_config = {
            "Painel":        {"icon": "📊", "desc": "Acesso ao dashboard",     "color": COLORS["accent"]},
            "Agenda":        {"icon": "📅", "desc": "Gerenciar eventos",        "color": COLORS["secondary"]},
            "Financeiro":    {"icon": "💰", "desc": "Transações e relatórios",  "color": COLORS["success"]},
            "Configurações": {"icon": "⚙️", "desc": "Configurações do sistema", "color": COLORS["warning"]},
            "Cadastro":      {"icon": "📝", "desc": "CRUD de usuários",         "color": COLORS["danger"]},
            "Gerenciamento": {"icon": "👔", "desc": "Controle administrativo",  "color": COLORS["secondary"]},
            "Permissões":    {"icon": "🔐", "desc": "Controle de acesso",       "color": COLORS["accent"]},
            "Status da Conta": {"icon": "👤", "desc": "Ativar ou desativar o acesso à conta", "color": COLORS["accent"]},
        }

        # Lista completa inclui Status da Conta
        all_items = self.permissions_list + ["Status da Conta"]
        
        for index, perm_name in enumerate(all_items):
            row, col = divmod(index, 2)
            config = permissions_config.get(perm_name, {"icon": "🛡️", "desc": "", "color": COLORS["muted"]})

            card = ctk.CTkFrame(
                self.permissions_container, fg_color=COLORS["content_bg"],
                corner_radius=16, border_width=1, border_color=COLORS["border"], height=85
            )
            card.grid(row=row, column=col, sticky="ew", padx=6, pady=8)
            card.grid_propagate(False)
            card.grid_columnconfigure(2, weight=1)

            icon_frame = ctk.CTkFrame(card, fg_color=COLORS["hover"], width=44, height=44, corner_radius=12)
            icon_frame.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)
            icon_frame.grid_propagate(False)
            ctk.CTkLabel(
                icon_frame, text=config["icon"],
                font=font(ICON_SIZE), text_color=config['color']
            ).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(
                card, text=perm_name,
                font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text"]
            ).grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(10, 0))

            ctk.CTkLabel(
                card, text=config["desc"],
                font=ctk.CTkFont(size=12), text_color=COLORS["muted"]
            ).grid(row=1, column=1, sticky="w", padx=(0, 5), pady=(0, 10))

            if perm_name == "Status da Conta":
                self.account_status_switch = ctk.CTkSwitch(
                    card, text="", width=40, height=22,
                    progress_color=config['color'],
                    button_color=COLORS["card"],
                    button_hover_color=COLORS["hover"],
                    command=self.sync_account_status
                )
                self.account_status_switch.grid(row=0, column=2, rowspan=2, padx=(5, 15), sticky="e")
            else:
                sw = ctk.CTkSwitch(
                    card, text="", width=40, height=22,
                    progress_color=config['color'],
                    button_color=COLORS["card"],
                    button_hover_color=COLORS["hover"],
                    command=lambda p=perm_name: self.sync_permission(p)
                )
                sw.grid(row=0, column=2, rowspan=2, padx=(5, 15), sticky="e")
                self.switch_widgets[perm_name] = sw

        button_frame = ctk.CTkFrame(self.right_card, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(0, 25), padx=20, sticky="e")
        self.save_btn = ctk.CTkButton(
            button_frame, text="💾 Salvar Alterações",
            font=font("button_large", "bold"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
            height=38, width=200, corner_radius=8,
            text_color="#FFFFFF", command=self.save_to_database
        )
        self.save_btn.pack(anchor="e")

        self.toggle_switches_state("disabled")

    def on_admin_click(self, frame, admin_name):
        self.selected_admin_name = admin_name
        self.selected_admin_id = self.admins_data[admin_name].get("id")
        self.selected_admin_label.configure(text=f"Configurando: {admin_name}")
        self.toggle_switches_state("normal")
        admin_perms = self.admins_data[admin_name].get("perms", {})
        for p_name in self.permissions_list:
            if admin_perms.get(p_name, False):
                self.switch_widgets[p_name].select()
            else:
                self.switch_widgets[p_name].deselect()
        admin_status = self.admins_data[admin_name].get("status", "Inativo")
        if admin_status == "Ativo":
            self.account_status_switch.select()
        else:
            self.account_status_switch.deselect()

    def sync_account_status(self):
        if self.selected_admin_name:
            is_active = bool(self.account_status_switch.get())
            self.admins_data[self.selected_admin_name]["status"] = "Ativo" if is_active else "Inativo"

    def sync_permission(self, perm_name):
        if self.selected_admin_name:
            new_state = self.switch_widgets[perm_name].get()
            self.admins_data[self.selected_admin_name]["perms"][perm_name] = new_state

    def toggle_switches_state(self, state):
        for sw in self.switch_widgets.values():
            sw.configure(state=state)
        self.account_status_switch.configure(state=state)

    def save_to_database(self):
        if not self.selected_admin_id:
            messagebox.showwarning("Aviso", "Selecione um administrador para salvar permissões")
            return
        try:
            gerente_id = self.selected_admin_id
            GerenciamentoController.remover_todas_permissoes_gerente(gerente_id)
            todas_permissoes = GerenciamentoController.listar_permissoes_disponiveis()
            permissao_map = {p['codigo']: p['id'] for p in todas_permissoes}
            for perm_nome in self.permissions_list:
                if self.switch_widgets[perm_nome].get():
                    permissao_id = permissao_map.get(perm_nome)
                    if permissao_id:
                        GerenciamentoController.adicionar_permissao_gerente(gerente_id, permissao_id)
            if self.account_status_switch.get():
                GerenciamentoController.ativar_gerente(gerente_id)
            else:
                GerenciamentoController.desativar_gerente(gerente_id)
            self.admins_data = self.load_gerentes_from_database()
            messagebox.showinfo("Sucesso", "✅ Permissões e status da conta salvos com sucesso!")
            self.admin_list_panel.admins_data = self.admins_data
            self.admin_list_panel.refresh_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar permissões: {str(e)}")
            import traceback
            traceback.print_exc()