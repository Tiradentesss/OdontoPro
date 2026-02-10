import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
import os
from tkinter import messagebox, filedialog
from services.permissoes_service import carregar_permissoes, salvar_permissoes

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
        self.avatar_inners = {}
        self.selected_row = None
        self.current_page = 1
        self.items_per_page = 5

        # Configuração do Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Cabeçalho Principal ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")
        
        header_content = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        self.lbl_title = ctk.CTkLabel(header_content, text="Administradores Atuais", font=("Roboto", 18, "bold"), text_color="#1F2937")
        self.lbl_title.pack(side="left")

        self.lbl_count = ctk.CTkLabel(header_content, text=f"{len(admins_data)} ativos", text_color="#9CA3AF", font=("Roboto", 13))
        self.lbl_count.pack(side="left", padx=12)

        # --- Cabeçalho da Tabela ---
        self.table_header = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=0, height=50)
        self.table_header.grid(row=1, column=0, padx=0, pady=0, sticky="ew")
        self.table_header.grid_propagate(False)
        self.table_header.grid_columnconfigure(0, weight=0)  # Nome
        self.table_header.grid_columnconfigure(1, weight=1)  # Email
        self.table_header.grid_columnconfigure(2, weight=1)  # Nível
        self.table_header.grid_columnconfigure(3, weight=1)  # Status

        header_labels = [
            ("Nome", 0),
            ("Email", 1),
            ("Nível", 2),
            ("Status", 3)
        ]
        
        for label, col in header_labels:
            lbl = ctk.CTkLabel(self.table_header, text=label, font=("Roboto", 12, "bold"), text_color="#6B7280")
            lbl.grid(row=0, column=col, sticky="w", padx=15, pady=12)

        # --- Tabela Rolável ---
        self.scroll_list = ctk.CTkScrollableFrame(self, label_text="", fg_color="white", corner_radius=0)
        self.scroll_list.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")
        self.scroll_list.grid_columnconfigure(0, weight=1)

        # --- Rodapé com Paginação ---
        self.footer_frame = ctk.CTkFrame(self, fg_color="#F9FAFB", corner_radius=0)
        self.footer_frame.grid(row=3, column=0, padx=0, pady=0, sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1)

        footer_content = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        footer_content.pack(fill="x", padx=20, pady=15)

        self.lbl_pagination_title = ctk.CTkLabel(footer_content, text="", font=("Roboto", 12, "bold"), text_color="#1F2937")
        self.lbl_pagination_title.pack(side="left")

        self.lbl_pagination_subtitle = ctk.CTkLabel(footer_content, text="", font=("Roboto", 12), text_color="#9CA3AF")
        self.lbl_pagination_subtitle.pack(side="left", padx=10)

        # Botões de Paginação
        buttons_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        buttons_frame.pack(side="right")

        self.btn_anterior = ctk.CTkButton(buttons_frame, text="Anterior", width=110, height=36, 
                                          font=("Roboto", 12),
                                          fg_color="white", border_width=2, border_color="#60A5FA", 
                                          text_color="#60A5FA", hover_color="#F3F4F6",
                                          command=self.previous_page)
        self.btn_anterior.pack(side="left", padx=5)

        self.btn_proximo = ctk.CTkButton(buttons_frame, text="Próximo", width=110, height=36, 
                                         font=("Roboto", 12),
                                         fg_color="white", border_width=2, border_color="#60A5FA", 
                                         text_color="#60A5FA", hover_color="#F3F4F6",
                                         command=self.next_page)
        self.btn_proximo.pack(side="left", padx=5)

        self.populate_list()

    def populate_list(self):
        # Limpar linhas antigas
        for row in self.admin_rows:
            row.destroy()
        self.admin_rows = []

        # Calcular paginação
        admin_list = list(self.admins_data.items())
        total_pages = max(1, (len(admin_list) + self.items_per_page - 1) // self.items_per_page)
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_data = admin_list[start_idx:end_idx]

        # Atualizar rótulos de paginação
        self.lbl_pagination_title.configure(text=f"Página {self.current_page} de {total_pages}")
        self.lbl_pagination_subtitle.configure(text=f"Página {self.current_page} de {total_pages}")

        # Atualizar estado dos botões
        self.btn_anterior.configure(state="normal" if self.current_page > 1 else "disabled")
        self.btn_proximo.configure(state="normal" if self.current_page < total_pages else "disabled")

        # Preencher tabela
        for index, (nome, info) in enumerate(page_data):
            self.create_admin_row(nome, info, index)

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
        """Abre o seletor de arquivos e atualiza a foto do administrador"""
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.admins_data[admin_name]["photo_path"] = file_path
            
            try:
                img = Image.open(file_path)
                # Redimensionar e cortar a imagem para formato quadrado
                size = min(img.size)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                # Criar imagem arredondada (anti-aliased)
                img = self.create_rounded_image(img, 40)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))

                # Colocar nova imagem dentro do container existente (preserva layout)
                container = self.avatar_labels.get(admin_name)
                if container:
                    # remover filho anterior
                    for child in container.winfo_children():
                        try:
                            child.destroy()
                        except Exception:
                            pass
                    new_inner = ctk.CTkLabel(container, image=ctk_img, text="", width=40, height=40, fg_color="transparent", padx=0, pady=0)
                    new_inner.place(relx=0.5, rely=0.5, anchor="center")
                    new_inner.configure(cursor="hand2")
                    new_inner.bind("<Button-1>", lambda e, n=admin_name: self.upload_photo(n))
                    self.avatar_inners[admin_name] = new_inner

                messagebox.showinfo("Sucesso", f"Foto de {admin_name} atualizada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao processar imagem: {str(e)}")

    def create_rounded_image(self, img, size):
        """Cria uma imagem arredondada (circular)"""
        # Converter para RGBA primeiro
        img = img.convert("RGBA")
        # Redimensionar com alta qualidade
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        # Criar máscara em alta resolução (4x) para anti-alias suave
        scale = 4
        big_size = (size * scale, size * scale)
        mask = Image.new('L', big_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse([0, 0, big_size[0] - 1, big_size[1] - 1], fill=255)
        # Reduzir a máscara para suavizar as bordas
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)
        img.putalpha(mask)
        return img

    def create_letter_avatar(self, letter, color, size):
        """Cria um avatar circular com uma letra perfeitamente centralizada"""
        img = Image.new("RGBA", (size, size), color=color)
        draw = ImageDraw.Draw(img)

        # Fonte consistente (evita variação visual)
        try:
            font = ImageFont.truetype("arial.ttf", int(size * 0.55))
        except:
            font = ImageFont.load_default()

        # Texto SEMPRE centralizado
        draw.text(
            (size // 2, size // 2),
            letter,
            fill="white",
            font=font,
            anchor="mm"  # 🔥 isso resolve tudo
        )

        # Máscara circular com anti-alias
        scale = 4
        big_size = (size * scale, size * scale)
        mask = Image.new("L", big_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse(
            (0, 0, big_size[0] - 1, big_size[1] - 1),
            fill=255
        )
        mask = mask.resize((size, size), Image.Resampling.LANCZOS)
        img.putalpha(mask)

        return img

    def create_admin_row(self, nome, info, index):
        row = ctk.CTkFrame(self.scroll_list, fg_color="white", corner_radius=0, border_width=0, height=60)
        row.grid(row=index, column=0, padx=0, pady=0, sticky="ew")
        row.grid_propagate(False)
        row.grid_columnconfigure(0, weight=0)  # Avatar + Nome
        row.grid_columnconfigure(1, weight=1)  # Email
        row.grid_columnconfigure(2, weight=1)  # Nível
        row.grid_columnconfigure(3, weight=1)  # Status

        # Evento de clique na linha
        def on_row_click(event=None):
            self.on_click_callback(row, nome)
            self.select_row(row)

        # --- COLUNA 0: Avatar + Nome (horizontal) ---
        col0_frame = ctk.CTkFrame(row, fg_color="transparent", height=60)
        col0_frame.grid_propagate(False)
        col0_frame.grid(row=0, column=0, padx=15, sticky="w")
        col0_frame.grid_columnconfigure(0, weight=0)
        col0_frame.grid_columnconfigure(1, weight=0)
        col0_frame.grid_rowconfigure(0, weight=1)

        # Avatar
        avatar_container = ctk.CTkFrame(col0_frame, fg_color="transparent", width=44, height=44, border_width=0)
        avatar_container.grid_propagate(False)
        avatar_container.grid(row=0, column=0, padx=(0, 10), sticky="w")

        photo_path = info.get("photo_path")
        if photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path)
                size = min(img.size)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                img = img.crop((left, top, left + size, top + size))
                img = self.create_rounded_image(img, 40)
                avatar_img = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
                inner = ctk.CTkLabel(avatar_container, image=avatar_img, text="", width=40, height=40, fg_color="transparent", padx=0, pady=0)
            except Exception:
                colors = ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#EC4899"]
                color_rgb = tuple(int(colors[hash(nome) % len(colors)].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                letter_img = self.create_letter_avatar(nome[0].upper(), color_rgb, 40)
                letter_ctk_img = ctk.CTkImage(light_image=letter_img, dark_image=letter_img, size=(40, 40))
                inner = ctk.CTkLabel(avatar_container, image=letter_ctk_img, text="", width=40, height=40, fg_color="transparent", padx=0, pady=0)
        else:
            colors = ["#EF4444", "#F97316", "#EAB308", "#22C55E", "#EC4899"]
            color_rgb = tuple(int(colors[hash(nome) % len(colors)].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            letter_img = self.create_letter_avatar(nome[0].upper(), color_rgb, 40)
            letter_ctk_img = ctk.CTkImage(light_image=letter_img, dark_image=letter_img, size=(40, 40))
            inner = ctk.CTkLabel(avatar_container, image=letter_ctk_img, text="", width=40, height=40, fg_color="transparent", padx=0, pady=0)

        inner.place(relx=0.5, rely=0.5, anchor="center")
        self.avatar_labels[nome] = avatar_container
        self.avatar_inners[nome] = inner
        inner.bind("<Button-1>", lambda e: self.upload_photo(nome))
        inner.configure(cursor="hand2")

        # Nome ao lado do avatar
        lbl_name = ctk.CTkLabel(col0_frame, text=nome, font=("Roboto", 12, "bold"), text_color="#1F2937")
        lbl_name.grid(row=0, column=1, sticky="w", padx=(5, 0))
        lbl_name.bind("<Button-1>", on_row_click)

        # --- COLUNA 1: Email ---
        email = info.get("email", "sem@email.com")
        lbl_email = ctk.CTkLabel(row, text=email, font=("Roboto", 11), text_color="#6B7280")
        lbl_email.grid(row=0, column=1, padx=15, sticky="w", pady=(18, 18))
        lbl_email.bind("<Button-1>", on_row_click)

        # --- COLUNA 2: Nível ---
        level = info.get("level", "Nível não definido")
        lbl_level = ctk.CTkLabel(row, text=level, font=("Roboto", 11), text_color="#6B7280")
        lbl_level.grid(row=0, column=2, padx=15, sticky="w", pady=(18, 18))
        lbl_level.bind("<Button-1>", on_row_click)

        # --- COLUNA 3: Status ---
        status = info.get("status", "Ativo")
        status_colors = {
            "Ativo": "#10B981",
            "Pendente": "#F59E0B",
            "Inativo": "#EF4444"
        }
        status_color = status_colors.get(status, "#10B981")
        
        lbl_status = ctk.CTkLabel(row, text=status, font=("Roboto", 11, "bold"), 
                                 text_color="white", fg_color=status_color, 
                                 corner_radius=6, width=75, height=24)
        lbl_status.grid(row=0, column=3, padx=15, sticky="w", pady=(18, 18))
        lbl_status.bind("<Button-1>", on_row_click)

        # --- Linha Divisória ---
        separator = ctk.CTkFrame(row, fg_color="#E5E7EB", height=1)
        separator.grid(row=1, column=0, columnspan=4, sticky="ew", padx=0, pady=0)

        # Evento de clique na linha
        row.bind("<Button-1>", on_row_click)
        col0_frame.bind("<Button-1>", on_row_click)
        
        self.admin_rows.append(row)

    def select_row(self, selected_frame):
        """Destaca a linha selecionada"""
        for row in self.admin_rows:
            row.configure(fg_color="white")
        selected_frame.configure(fg_color="#EBF5FF")

class Permissoes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#F3F4F6")

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(0, weight=1)

        self.selected_admin_name = None
        self.switch_widgets = {}
        self.permissions_list = ["Painel", "Agenda", "Financeiro", "Configurações", "Cadastro", "Permissões"]

        # Tentar carregar dados
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

        self.scroll_container = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
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
        for row in self.admin_list_panel.admin_rows:
            row.configure(fg_color="#F8F9FA", border_color="#E5E7EB")
        
        frame.configure(fg_color="#EBF5FF", border_color="#3B8ED0")
        self.selected_admin_name = admin_name
        self.toggle_switches_state("normal")

        admin_perms = self.admins_data[admin_name].get("perms", {})
        for p_name in self.permissions_list:
            if admin_perms.get(p_name, False): self.switch_widgets[p_name].select()
            else: self.switch_widgets[p_name].deselect()

    def sync_permission(self, perm_name):
        if self.selected_admin_name:
            if "perms" not in self.admins_data[self.selected_admin_name]:
                self.admins_data[self.selected_admin_name]["perms"] = {}
            self.admins_data[self.selected_admin_name]["perms"][perm_name] = bool(self.switch_widgets[perm_name].get())

    def toggle_switches_state(self, state):
        for sw in self.switch_widgets.values(): sw.configure(state=state)

    def save_to_database(self):
        salvar_permissoes(self.admins_data)
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Permissões Pro")
        self.geometry("1100x700")
        Permissoes(self).pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()