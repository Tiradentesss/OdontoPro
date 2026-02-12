import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os
from tkinter import messagebox, filedialog

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
            0: {"weight": 0, "minsize": 70},   # Avatar (Fixo)
            1: {"weight": 1, "minsize": 150},  # Nome (Expande)
            2: {"weight": 1, "minsize": 140},  # Email (Expande mais)
            3: {"weight": 1, "minsize": 120},  # Nível (Expande)
            4: {"weight": 0, "minsize": 140},  # Status (Fixo)
        }

        # --- Cabeçalho Principal (Título) ---
        header_content = ctk.CTkFrame(self, fg_color="transparent")
        header_content.grid(row=0, column=0, padx=20, pady=15, sticky="ew")
        
        self.lbl_title = ctk.CTkLabel(header_content, text="Administradores Atuais", font=("Roboto", 18, "bold"), text_color="#1F2937")
        self.lbl_title.pack(side="left")

        self.lbl_count = ctk.CTkLabel(header_content, text=f"{len(admins_data)} ativos", text_color="#9CA3AF", font=("Roboto", 13))
        self.lbl_count.pack(side="left", padx=12)

        # --- Frame da Tabela ---
        table_container = ctk.CTkFrame(self, fg_color="transparent")
        table_container.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        table_container.grid_rowconfigure(1, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        # --- Cabeçalho da Tabela ---
        header_bg = ctk.CTkFrame(table_container, fg_color="#F3F4F6", height=45, corner_radius=6)
        header_bg.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 5))
        header_bg.grid_propagate(False) 
        
        # Aplica configuração no Header
        for col_idx, conf in self.col_config.items():
            header_bg.grid_columnconfigure(col_idx, weight=conf["weight"], minsize=conf["minsize"])

        headers = ["Avatar", "Nome", "Email", "Nível", "Status"]
        anchors = ["center", "center", "w", "w", "e"]
        paddings = [5, 5, 50, 30, 50] 

        for i, text in enumerate(headers):
            ctk.CTkLabel(
                header_bg, text=text, font=("Roboto", 11, "bold"), 
                text_color="#4B5563", anchor=anchors[i]
            ).grid(row=0, column=i, sticky="ew", padx=paddings[i], pady=10)

        # --- ALTERAÇÃO AQUI: CTkFrame em vez de CTkScrollableFrame ---
        self.scroll_list = ctk.CTkFrame(table_container, fg_color="white")
        self.scroll_list.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.scroll_list.grid_columnconfigure(0, weight=1) 

        # --- Rodapé com Paginação ---
        # ALTERAÇÃO: Adicionado corner_radius=15 para arredondar o rodapé
        self.footer_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", corner_radius=15)
        self.footer_frame.grid(row=2, column=0, padx=0, pady=0, sticky="ew")

        footer_content = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_content.pack(fill="x", padx=20, pady=15)

        self.lbl_pagination = ctk.CTkLabel(footer_content, text="", font=("Roboto", 12, "bold"), text_color="#1F2937")
        self.lbl_pagination.pack(side="left")

        buttons_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        buttons_frame.pack(side="right")

        self.btn_anterior = ctk.CTkButton(buttons_frame, text="Anterior", width=110, height=36, 
                                          font=("Roboto", 12), fg_color="white", border_width=2, 
                                          border_color="#60A5FA", text_color="#60A5FA", hover_color="#F3F4F6",
                                          command=self.previous_page)
        self.btn_anterior.pack(side="left", padx=5)

        self.btn_proximo = ctk.CTkButton(buttons_frame, text="Próximo", width=110, height=36, 
                                         font=("Roboto", 12), fg_color="white", border_width=2, 
                                         border_color="#60A5FA", text_color="#60A5FA", hover_color="#F3F4F6",
                                         command=self.next_page)
        self.btn_proximo.pack(side="left", padx=5)

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
        row_frame = ctk.CTkFrame(self.scroll_list, fg_color="transparent", corner_radius=6, height=50)
        row_frame.pack(fill="x", pady=2, padx=5)
        
        for col_idx, conf in self.col_config.items():
            row_frame.grid_columnconfigure(col_idx, weight=conf["weight"], minsize=conf["minsize"])

        def on_row_click(event=None):
            self.highlight_row(row_frame)
            self.on_click_callback(None, nome)

        row_frame.bind("<Button-1>", on_row_click)
        row_frame.configure(cursor="hand2")
        self.admin_rows.append(row_frame)

        # --- Avatar (Coluna 0) ---
        colors = ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#EC4899"]
        color_rgb = tuple(int(colors[hash(nome) % len(colors)].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        
        if "photo_path" in info and os.path.exists(info["photo_path"]):
            try:
                img = Image.open(info["photo_path"])
                size = min(img.size)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                img = self.create_rounded_image(img, 28)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(28, 28))
            except:
                letter_img = self.create_letter_avatar(nome[0].upper(), color_rgb, 28)
                ctk_img = ctk.CTkImage(light_image=letter_img, dark_image=letter_img, size=(28, 28))
        else:
            letter_img = self.create_letter_avatar(nome[0].upper(), color_rgb, 28)
            ctk_img = ctk.CTkImage(light_image=letter_img, dark_image=letter_img, size=(28, 28))

        av_cont = ctk.CTkFrame(row_frame, fg_color="transparent")
        av_cont.grid(row=0, column=0, sticky="ew") 
        av_cont.bind("<Button-1>", on_row_click)

        avatar_label = ctk.CTkLabel(av_cont, image=ctk_img, text="")
        avatar_label.pack(pady=5)
        avatar_label.bind("<Button-1>", lambda e: self.upload_photo(nome)) 
        avatar_label.configure(cursor="hand2")
        self.avatar_labels[nome] = avatar_label

        # --- Labels de Texto (Colunas 1, 2, 3) ---
        nome_label = ctk.CTkLabel(row_frame, text=nome, font=("Roboto", 11, "bold"), text_color="#1F2937", anchor="center")
        nome_label.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        nome_label.bind("<Button-1>", on_row_click)

        email = info.get("email", "sem@email.com")
        email_label = ctk.CTkLabel(row_frame, text=email, font=("Roboto", 11), text_color="#6B7280", anchor="w")
        email_label.grid(row=0, column=2, sticky="ew", padx=30, pady=5)
        email_label.bind("<Button-1>", on_row_click)

        level = info.get("level", "Nível não definido")
        nivel_label = ctk.CTkLabel(row_frame, text=level, font=("Roboto", 11), text_color="#6B7280", anchor="w")
        nivel_label.grid(row=0, column=3, sticky="ew", padx=26, pady=5)
        nivel_label.bind("<Button-1>", on_row_click)

        # --- Status (Coluna 4) ---
        status = info.get("status", "Ativo")
        status_colors = {"Ativo": "#10B981", "Pendente": "#F59E0B", "Inativo": "#EF4444"}
        status_color = status_colors.get(status, "#10B981")
        
        status_container = ctk.CTkFrame(row_frame, fg_color="transparent")
        status_container.grid(row=0, column=4, sticky="ew", padx=20)
        status_container.bind("<Button-1>", on_row_click)

        status_label = ctk.CTkLabel(status_container, text=status, font=("Roboto", 11, "bold"), 
                                   text_color="white", fg_color=status_color, corner_radius=6, width=80)
        status_label.pack(pady=5)
        status_label.bind("<Button-1>", on_row_click)

    def highlight_row(self, frame_to_select):
        if self.selected_row_frame is not None:
            try:
                self.selected_row_frame.configure(fg_color="transparent")
            except:
                pass 
        frame_to_select.configure(fg_color="#DBEAFE") 
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
                size = min(img.size)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                img = self.create_rounded_image(img, 30)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(30, 30))
                
                avatar_label = self.avatar_labels.get(admin_name)
                if avatar_label:
                    avatar_label.configure(image=ctk_img)

                messagebox.showinfo("Sucesso", f"Foto de {admin_name} atualizada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar imagem: {str(e)}")

    def create_rounded_image(self, img, size):
        img = img.convert("RGBA")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        scale = 4
        big_size = (size * scale, size * scale)
        mask = Image.new('L', big_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, big_size[0] - 1, big_size[1] - 1], fill=255)
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)
        img.putalpha(mask)
        return img

    def create_letter_avatar(self, letter, color, size):
        img = Image.new("RGBA", (size, size), color=color)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", int(size * 0.55))
        except:
            font = ImageFont.load_default()

        draw.text((size // 2, size // 2), letter, fill="white", font=font, anchor="mm")

        scale = 4
        big_size = (size * scale, size * scale)
        mask = Image.new("L", big_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, big_size[0] - 1, big_size[1] - 1), fill=255)
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)
        img.putalpha(mask)
        return img


class Permissoes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#F3F4F6")

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=4)
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
            "John Doe": {"level": "Admin", "email": "john.doe@email.com", "status": "Ativo", "perms": {p: False for p in self.permissions_list}},
            "Jane Smith": {"level": "Billing", "email": "jane.smith@email.com", "status": "Ativo", "perms": {p: True for p in self.permissions_list}},
            "Alice Brown": {"level": "Reporting", "email": "alice.b@email.com", "status": "Ativo", "perms": {p: False for p in self.permissions_list}},
            "Locaritn Ltrntan": {"level": "Somente Leitura", "email": "loc@email.com", "status": "Pendente", "perms": {p: False for p in self.permissions_list}},
        }

    def setup_ui(self):
        # COLUNA ESQUERDA
        self.admin_list_panel = AdminListFrame(self, admins_data=self.admins_data, on_click_callback=self.on_admin_click, fg_color="white", corner_radius=15)
        self.admin_list_panel.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # COLUNA DIREITA
        self.right_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        self.right_card.grid_rowconfigure(1, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.right_card, text="Configurar Permissões", font=("Arial", 18, "bold"), text_color="#111827").grid(row=0, column=0, sticky="w", pady=20, padx=20)

        # --- ALTERAÇÃO AQUI: CTkFrame em vez de CTkScrollableFrame ---
        self.scroll_container = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.scroll_container.grid(row=1, column=0, sticky="nsew", padx=10)
        self.scroll_container.grid_columnconfigure((0, 1, 2), weight=1)

        icons_map = {"Painel": "📊", "Agenda": "📅", "Financeiro": "💰", "Configurações": "⚙️", "Cadastro": "📝", "Permissões": "🔐"}

        for index, perm_name in enumerate(self.permissions_list):
            row, col = divmod(index, 3)
            card = ctk.CTkFrame(self.scroll_container, fg_color="#F8F9FA", corner_radius=12, border_width=1, border_color="#E5E7EB")
            card.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card, text=icons_map.get(perm_name, "🛡️"), font=("Arial", 22)).grid(row=0, column=0, padx=12, pady=12)
            ctk.CTkLabel(card, text=perm_name, font=("Arial", 11, "bold"), text_color="#374151").grid(row=0, column=1, sticky="w")

            sw = ctk.CTkSwitch(card, text="", width=45, height=24, progress_color="#1CE437", command=lambda p=perm_name: self.sync_permission(p))
            sw.grid(row=0, column=2, padx=(5, 15))
            self.switch_widgets[perm_name] = sw

        self.save_btn = ctk.CTkButton(self.right_card, text="Salvar Alterações", font=("Arial", 14, "bold"), fg_color="#2563EB", height=45, width=220, corner_radius=8, command=self.save_to_database)
        self.save_btn.grid(row=2, column=0, pady=25)

        self.toggle_switches_state("disabled")

    def on_admin_click(self, frame, admin_name):
        self.selected_admin_name = admin_name
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
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")