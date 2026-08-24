import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from functools import partial
from tkinter import messagebox, filedialog
from .base import BaseScreen
from .theme import COLORS, font, ICON_SIZE, INNER_CARD_BORDER, INNER_CARD_RADIUS
from config.database import get_connection
from controllers.gerenciamento_controller import GerenciamentoController
from models.auth import verificar_senha


MAPA_PERMISSOES = {
    "Painel": "dashboard",
    "Agenda": "consultas",
    "Financeiro": "financeiro",
    "Cadastro": "pacientes",
    "Gerenciamento": "medicos",
    "Configurações": "configuracoes",
}


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

    def __init__(self, master, admins_data, on_click_callback, on_delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.on_click_callback = on_click_callback
        self.on_delete_callback = on_delete_callback
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
        self.header_bg = ctk.CTkFrame(self, fg_color="transparent")
        self.header_bg.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.header_content = ctk.CTkFrame(self.header_bg, fg_color="transparent")
        self.header_content.pack(fill="x")

        title_frame = ctk.CTkFrame(self.header_content, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text="👥", font=font(ICON_SIZE)).pack(side="left", padx=(0, 10))
        self.lbl_title = ctk.CTkLabel(
            title_frame, text="Funcionários",
            font=font("subtitle", "bold"), text_color=COLORS["text"]
        )
        self.lbl_title.pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            self.header_content, text=f"{len(self.admins_data)} ativos",
            text_color=COLORS["muted"], font=font("small")
        )
        self.lbl_count.pack(side="left", padx=15)

        self.btn_refresh = ctk.CTkButton(
            self.header_content, text="↻", width=36, height=36, font=font("text"),
            fg_color="transparent", text_color=COLORS["muted"],
            hover_color=COLORS["hover"], corner_radius=8, command=self.refresh_list
        )
        self.btn_refresh.pack(side="right")

        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_container.grid_rowconfigure(1, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.table_header = ctk.CTkFrame(
            self.content_container, fg_color=COLORS["content_bg"], height=44, corner_radius=10
        )
        self.table_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(0, 6))
        self.table_header.grid_propagate(False)
        self._apply_col_config(self.table_header)

        headers = ["", "Nome", "Email", "Status"]
        anchors = ["center", "w", "w", "center"]
        stickys = ["nsew", "w", "w", "w"]
        padx_map = {
            0: (12, 8),
            1: (8, 8),
            2: (8, 8),
            3: (20, 8),
        }
        for i, text in enumerate(headers):
            ctk.CTkLabel(
                self.table_header, text=text,
                font=font("small", "bold"),
                text_color=COLORS["text_secondary"],
                anchor=anchors[i]
            ).grid(row=0, column=i, sticky=stickys[i], padx=padx_map[i], pady=10)

        self.scroll_list = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.scroll_list.grid(row=1, column=0, sticky="nsew", padx=12, pady=0)

        self.footer_container = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_container.grid(row=2, column=0, pady=(0, 25), padx=20, sticky="e")

        self.lbl_pagination = ctk.CTkLabel(
            self.footer_container, text="", font=font("small"), text_color=COLORS["text_secondary"]
        )
        self.lbl_pagination.pack(side="left", pady=17)

        self.buttons_frame = ctk.CTkFrame(self.footer_container, fg_color="transparent")
        self.buttons_frame.pack(side="right", pady=17)
        self.btn_anterior = ctk.CTkButton(
            self.buttons_frame, text="← Anterior", width=100, height=36, font=font("small"),
            fg_color=COLORS["card"], border_width=1, border_color=COLORS["border"],
            text_color=COLORS["text"], hover_color=COLORS["hover"],
            corner_radius=8, command=self.previous_page
        )
        self.btn_anterior.pack(side="left", padx=5)
        self.btn_proximo = ctk.CTkButton(
            self.buttons_frame, text="Próximo →", width=100, height=36, font=font("small"),
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

        if not admin_list:
            self.no_results_label = ctk.CTkLabel(
                self.scroll_list,
                text="Nenhum gestor cadastrado.",
                font=font("text", "bold"),
                text_color=COLORS["muted"]
            )
            self.no_results_label.pack(expand=True, pady=30)
            return

        for index, (nome, info) in enumerate(page_data):
            self.create_admin_row(nome, info, index)

    def create_admin_row(self, nome, info, index):
        row_frame = ctk.CTkFrame(
            self.scroll_list,
            fg_color="transparent",
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
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
            padx=(16, 12),
            pady=11,
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
            padx=(12, 12),
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
            padx=(12, 12),
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
            padx=(12, 12),
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

        if self.on_delete_callback is not None:
            gerente_para_excluir = {**info, "nome": nome}
            excluir = ctk.CTkButton(
                row_frame,
                text="X",
                width=24,
                height=24,
                fg_color="transparent",
                bg_color="transparent",
                hover_color=COLORS["primary_soft"],
                text_color=COLORS["primary"],
                corner_radius=12,
                border_width=0,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=partial(self._handle_delete_click, gerente_para_excluir)
            )
            excluir.place(relx=1.0, rely=0.0, anchor="ne", x=2, y=-5)

    def _handle_delete_click(self, gerente):
        self.on_delete_callback(gerente)

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
    def __init__(self, parent, clinica_id=None, usuario_id=None, tipo_usuario=None):
        super().__init__(parent, "Permissões")
        self.clinica_id = clinica_id
        self.usuario_logado_id = usuario_id
        self.tipo_usuario = tipo_usuario
        self.usuario_e_master = self.tipo_usuario == "clinica"

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
            "Cadastro", "Gerenciamento", "Permissões", "Minha Clínica"
        ]

        self.admins_data = self.load_gerentes_from_database()
        self.setup_ui()

    def load_gerentes_from_database(self):
        try:
            gerentes_bd = GerenciamentoController.listar_todos_gerentes_por_clinica(self.clinica_id)
            if not gerentes_bd:
                print("Nenhum gerente encontrado para esta clínica")
                return {}

            permissoes_bd = GerenciamentoController.listar_permissoes_disponiveis()
            codigos_permissoes = {p['codigo'] for p in permissoes_bd}

            admins = {}
            for gerente in gerentes_bd:
                gerente_id = gerente['id']
                gerentes_perms_bd = GerenciamentoController.obter_permissoes_gerente(gerente_id)
                perms_dict = {}
                for perm in self.permissions_list:
                    codigo = MAPA_PERMISSOES.get(perm)
                    tem_permissao = codigo in codigos_permissoes and any(
                        p['codigo'] == codigo for p in gerentes_perms_bd
                    )
                    perms_dict[perm] = tem_permissao
                status = "Ativo" if gerente['ativo'] == 1 else "Inativo"
                admins[gerente['nome']] = {
                    "id": gerente_id,
                    "level": "Gestor",
                    "email": gerente['email'],
                    "status": status,
                    "perms": perms_dict
                }
            return admins
        except Exception as e:
            print(f"Erro ao carregar gerentes do BD: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def refresh(self):
        self.admins_data = self.load_gerentes_from_database()
        if hasattr(self, "admin_list_panel"):
            self.admin_list_panel.admins_data = self.admins_data
            self.admin_list_panel.refresh_list()

    def setup_ui(self):
        self.admin_list_panel = AdminListFrame(
            self.content_card, admins_data=self.admins_data,
            on_click_callback=self.on_admin_click,
            on_delete_callback=self._confirmar_exclusao_gerente if self.usuario_e_master else None,
            fg_color=COLORS["card"], corner_radius=INNER_CARD_RADIUS, border_width=1, border_color=INNER_CARD_BORDER
        )
        self.admin_list_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)

        self.right_card = ctk.CTkFrame(self.content_card, fg_color=COLORS["card"], corner_radius=INNER_CARD_RADIUS, border_width=1, border_color=INNER_CARD_BORDER)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.right_card.grid_rowconfigure(1, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        header_bg = ctk.CTkFrame(self.right_card, fg_color="transparent")
        header_bg.grid(row=0, column=0, sticky="ew", pady=(30, 10), padx=20)
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

        self.permissions_container = ctk.CTkScrollableFrame(
            self.right_card,
            fg_color="transparent",
            corner_radius=0,
            border_width=0
        )
        self.permissions_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.permissions_container.grid_columnconfigure(0, weight=1)
        self.permissions_container.grid_columnconfigure(1, weight=1)

        permissions_config = {
            "Painel":        {"icon": "📊", "desc": "Acesso ao dashboard",     "color": COLORS["accent"]},
            "Agenda":        {"icon": "📅", "desc": "Gerenciar eventos",        "color": COLORS["secondary"]},
            "Financeiro":    {"icon": "�", "desc": "Transações e relatórios",  "color": COLORS["success"]},
            "Configurações": {"icon": "⚙️", "desc": "Configurações do sistema", "color": COLORS["warning"]},
            "Cadastro":      {"icon": "📝", "desc": "CRUD de usuários",         "color": COLORS["danger"]},
            "Gerenciamento": {"icon": "👔", "desc": "Controle administrativo",  "color": COLORS["secondary"]},
            "Permissões":    {"icon": "🔐", "desc": "Controle de acesso",       "color": COLORS["accent"]},
            "Minha Clínica":  {"icon": "🏥", "desc": "Acessar configurações da clínica", "color": COLORS["success"]},
            "Status da Conta": {"icon": "👤", "desc": "Ativar ou desativar o acesso à conta", "color": COLORS["accent"]},
        }

        # Lista completa inclui Status da Conta
        all_items = self.permissions_list + ["Status da Conta"]
        
        for index, perm_name in enumerate(all_items):
            row, col = divmod(index, 2)
            config = permissions_config.get(perm_name, {"icon": "🛡️", "desc": "", "color": COLORS["muted"]})
            display_name = "Relatórios" if perm_name == "Financeiro" else perm_name

            card = ctk.CTkFrame(
                self.permissions_container, fg_color=COLORS["content_bg"],
                corner_radius=INNER_CARD_RADIUS, border_width=1, border_color=INNER_CARD_BORDER, height=85
            )
            card.grid(row=row, column=col, sticky="ew", padx=6, pady=8)
            card.grid_propagate(False)
            card.grid_columnconfigure(2, weight=1)

            icon_frame = ctk.CTkFrame(card, fg_color=COLORS["hover"], width=44, height=44, corner_radius=12)
            icon_frame.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)
            icon_frame.grid_propagate(False)

            icon_image = None
            icon_text = config["icon"]
            if perm_name == "Financeiro":
                app = self.winfo_toplevel()
                if hasattr(app, "_get_menu_icon"):
                    icon_image = app._get_menu_icon("relatorios", config["color"])
                    icon_text = ""

            ctk.CTkLabel(
                icon_frame, text=icon_text, image=icon_image,
                font=font(ICON_SIZE), text_color=config['color']
            ).place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(
                card, text=display_name,
                font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["text"]
            ).grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(10, 0))

            ctk.CTkLabel(
                card, text=config["desc"],
                font=ctk.CTkFont(size=12), text_color=COLORS["muted"]
            ).grid(row=1, column=1, sticky="w", padx=(0, 5), pady=(0, 10))

            if perm_name == "Status da Conta":
                self.account_status_switch = ctk.CTkSwitch(
                    card, text="", width=40, height=22,
                    progress_color=COLORS["primary"],
                    button_color="#F1F5F9",
                    command=self.sync_account_status
                )
                self.account_status_switch.grid(row=0, column=2, rowspan=2, padx=(5, 15), sticky="e")
            else:
                sw = ctk.CTkSwitch(
                    card, text="", width=40, height=22,
                    progress_color=COLORS["primary"],
                    button_color="#F1F5F9",
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

    # initialize removed to restore original architecture

    def _is_self_account_selected(self):
        return bool(self.selected_admin_id is not None and self.selected_admin_id == self.usuario_logado_id)

    def on_admin_click(self, frame, admin_name):
        self.selected_admin_name = admin_name
        self.selected_admin_id = self.admins_data[admin_name].get("id")
        self.selected_admin_label.configure(text=f"Configurando: {admin_name}")
        self.toggle_switches_state("normal" if self.usuario_e_master else "disabled")
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

        if self._is_self_account_selected():
            self.account_status_switch.configure(state="disabled")

    def _confirmar_exclusao_gerente(self, gerente):
        if not self.usuario_e_master:
            messagebox.showerror("Acesso negado", "Somente a conta principal da clínica pode excluir gestores.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar exclusão")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f'Deseja excluir o gestor "{gerente["nome"]}"?',
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text"],
            justify="center"
        ).pack(padx=28, pady=(24, 18))

        botoes = ctk.CTkFrame(dialog, fg_color="transparent")
        botoes.pack(pady=(0, 20))

        ctk.CTkButton(
            botoes,
            text="Excluir",
            width=80,
            height=32,
            command=lambda: self._abrir_modal_senha_exclusao(gerente, dialog)
        ).pack(side="left", padx=6)
        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=80,
            height=32,
            fg_color=COLORS["card_soft"],
            text_color=COLORS["text"],
            hover_color=COLORS["hover"],
            command=dialog.destroy
        ).pack(side="left", padx=6)

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.update_idletasks()
        janela_principal = self.winfo_toplevel()
        pos_x = janela_principal.winfo_rootx() + (janela_principal.winfo_width() - dialog.winfo_width()) // 2
        pos_y = janela_principal.winfo_rooty() + (janela_principal.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{pos_x}+{pos_y}")

    def _abrir_modal_senha_exclusao(self, gerente, confirm_dialog):
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
            text_color=COLORS["text"]
        ).pack(padx=40, pady=(32, 12))

        senha_entry = ctk.CTkEntry(dialog, width=260, show="*")
        senha_entry.pack(padx=40, pady=(0, 14))

        erro_label = ctk.CTkLabel(dialog, text="", text_color=COLORS["danger"])
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
            self._excluir_gerente_confirmado(gerente, dialog)

        ctk.CTkButton(botoes, text="Confirmar", width=90, height=32, command=confirmar).pack(side="left", padx=6)
        ctk.CTkButton(
            botoes,
            text="Cancelar",
            width=90,
            height=32,
            fg_color=COLORS["card_soft"],
            text_color=COLORS["text"],
            hover_color=COLORS["hover"],
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

    def _excluir_gerente_confirmado(self, gerente, dialog):
        if not self.usuario_e_master:
            dialog.destroy()
            messagebox.showerror("Acesso negado", "Somente a conta principal da clínica pode excluir gestores.")
            return

        resultado = GerenciamentoController.excluir_gerente(
            gerente["id"],
            current_user_id=self.usuario_logado_id,
            clinica_id=self.clinica_id,
            current_user_type=self.tipo_usuario
        )
        dialog.destroy()

        if not resultado.get("sucesso"):
            mensagem = resultado.get("mensagem", "Não foi possível excluir o gestor.")
            mensagem = (str(mensagem)
                        .replace("GERENTE", "GESTOR")
                        .replace("Gerente", "Gestor")
                        .replace("gerente", "gestor"))
            messagebox.showerror("Erro", mensagem)
            return

        if self.selected_admin_id == gerente["id"]:
            self.selected_admin_name = None
            self.selected_admin_id = None
            self.selected_admin_label.configure(text="Nenhum administrador selecionado")
            self.toggle_switches_state("disabled")

        self.admins_data = self.load_gerentes_from_database()
        self.admin_list_panel.admins_data = self.admins_data
        self.admin_list_panel.current_page = 1
        self.admin_list_panel.refresh_list()

    def sync_account_status(self):
        if not self.usuario_e_master:
            return
        if self.selected_admin_name:
            if self._is_self_account_selected():
                current_status = self.admins_data[self.selected_admin_name].get("status", "Ativo")
                if current_status == "Ativo":
                    self.account_status_switch.select()
                else:
                    self.account_status_switch.deselect()
                return

            is_active = bool(self.account_status_switch.get())
            self.admins_data[self.selected_admin_name]["status"] = "Ativo" if is_active else "Inativo"

    def sync_permission(self, perm_name):
        if not self.usuario_e_master:
            return
        if self.selected_admin_name:
            new_state = self.switch_widgets[perm_name].get()
            self.admins_data[self.selected_admin_name]["perms"][perm_name] = new_state

    def toggle_switches_state(self, state):
        for sw in self.switch_widgets.values():
            sw.configure(state=state)

        if self._is_self_account_selected():
            self.account_status_switch.configure(state="disabled")
        else:
            self.account_status_switch.configure(state=state)

    def save_to_database(self):
        if not self.usuario_e_master:
            messagebox.showerror("Acesso negado", "Somente a conta principal da clínica pode salvar permissões.")
            return

        if not self.selected_admin_id:
            messagebox.showwarning("Aviso", "Selecione um administrador para salvar permissões")
            return

        novo_status = "Ativo" if self.account_status_switch.get() else "Inativo"
        if self._is_self_account_selected() and novo_status == "Inativo":
            messagebox.showerror(
                "Erro",
                "Não é permitido desativar a própria conta."
            )
            return

        try:
            gerente_id = self.selected_admin_id
            todas_permissoes = GerenciamentoController.listar_permissoes_disponiveis()
            permissao_map = {p['codigo']: p['id'] for p in todas_permissoes}
            permissoes_selecionadas = []
            for perm_nome in self.permissions_list:
                if self.switch_widgets[perm_nome].get():
                    codigo_real = MAPA_PERMISSOES.get(perm_nome)
                    if not codigo_real:
                        messagebox.showerror(
                            "Erro",
                            f"A permissão marcada '{perm_nome}' não possui código configurado."
                        )
                        return
                    permissao_id = permissao_map.get(codigo_real)
                    if permissao_id is None:
                        messagebox.showerror(
                            "Erro",
                            f"A permissão '{perm_nome}' ({codigo_real}) não existe no banco de dados."
                        )
                        return
                    permissoes_selecionadas.append((perm_nome, permissao_id))

            resultado_permissoes = GerenciamentoController.remover_todas_permissoes_gerente(
                gerente_id,
                clinica_id=self.clinica_id,
                current_user_type=self.tipo_usuario
            )
            if not resultado_permissoes.get("sucesso"):
                messagebox.showerror("Erro", resultado_permissoes.get("mensagem", "Erro ao salvar permissões"))
                return
            for perm_nome, permissao_id in permissoes_selecionadas:
                resultado_permissao = GerenciamentoController.adicionar_permissao_gerente(
                    gerente_id,
                    permissao_id,
                    clinica_id=self.clinica_id,
                    current_user_type=self.tipo_usuario
                )
                if not resultado_permissao.get("sucesso"):
                    messagebox.showerror("Erro", resultado_permissao.get("mensagem", "Erro ao salvar permissões"))
                    return
            if self.account_status_switch.get():
                resultado_status = GerenciamentoController.ativar_gerente(
                    gerente_id,
                    clinica_id=self.clinica_id,
                    current_user_type=self.tipo_usuario
                )
                if not resultado_status.get("sucesso"):
                    messagebox.showerror("Erro", resultado_status.get("mensagem", "Erro ao salvar permissões"))
                    return
            else:
                resultado = GerenciamentoController.desativar_gerente(
                    gerente_id,
                    current_user_id=self.usuario_logado_id,
                    clinica_id=self.clinica_id,
                    current_user_type=self.tipo_usuario
                )
                if not resultado.get("sucesso"):
                    messagebox.showerror("Erro", resultado.get("mensagem", "Erro ao salvar permissões"))
                    return
            self.admins_data = self.load_gerentes_from_database()
            messagebox.showinfo("Sucesso", "✅ Permissões e status da conta salvos com sucesso!")
            self.admin_list_panel.admins_data = self.admins_data
            self.admin_list_panel.refresh_list()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar permissões: {str(e)}")
            import traceback
            traceback.print_exc()