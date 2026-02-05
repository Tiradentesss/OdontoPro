import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
from services.permissoes_service import carregar_permissoes, salvar_permissoes

# Configuração de aparência global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class Permissoes(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#F3F4F6")

        # ===============================
        # GRID
        # ===============================
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=1)

        # ===============================
        # ESTADO
        # ===============================
        self.selected_admin_name = None
        self.selected_admin_frame = None
        self.admin_rows = []
        self.switch_widgets = {}

        # ===============================
        # PERMISSÕES ATUALIZADAS
        # ===============================
        self.permissions_list = [
            "Painel", "Agenda", "Financeiro", 
            "Configurações", "Cadastro", "Permissões"
        ]

        # ===============================
        # DADOS PADRÃO (fallback)
        # ===============================
        self.default_admins_data = {
            "John Doe": {"level": "Admin", "color": "#9CA3AF", "perms": {p: False for p in self.permissions_list}},
            "Jane Smith": {"level": "Billing", "color": "#9CA3AF", "perms": {p: True for p in self.permissions_list}},
            "Alice Brown": {"level": "Reporting", "color": "#10B981", "perms": {p: (i % 2 == 0) for i, p in enumerate(self.permissions_list)}},
            "Locaritn Ltrntan": {"level": "Read-Only", "color": "#10B981", "perms": {p: False for p in self.permissions_list}},
        }

        # ===============================
        # 🔵 CARREGAR JSON
        # ===============================
        try:
            dados_salvos = carregar_permissoes()
        except:
            dados_salvos = None

        if dados_salvos:
            self.admins_data = dados_salvos
        else:
            self.admins_data = self.default_admins_data

        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="Administradores Atuais", font=("Arial", 18, "bold"), text_color="#111827").grid(row=0, column=0, sticky="w", pady=(20, 15), padx=20)
        ctk.CTkLabel(self, text="Configurar Permissões", font=("Arial", 18, "bold"), text_color="#111827").grid(row=0, column=1, sticky="w", pady=(20, 15), padx=20)

        # ===============================
        # ESQUERDA (Lista de Admins)
        # ===============================
        self.left_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.left_card.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))

        header_frame = ctk.CTkFrame(self.left_card, fg_color="#F9FAFB", height=40)
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure((0, 1, 2), weight=1)

        for i, h in enumerate(["Avatar", "Nome", "Nível"]):
            ctk.CTkLabel(header_frame, text=h, font=("Arial", 12, "bold"), text_color="#6B7280").grid(row=0, column=i, sticky="w", padx=10)

        self.admin_list_container = ctk.CTkFrame(self.left_card, fg_color="transparent")
        self.admin_list_container.pack(fill="both", expand=True, padx=15)

        for nome, info in self.admins_data.items():
            self.create_admin_row(nome, info["level"], info["color"])

        # ===============================
        # DIREITA (Cards de Permissões)
        # ===============================
        self.right_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.right_card.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))
        self.right_card.grid_rowconfigure(0, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=(20, 10))
        self.scroll_container.grid_columnconfigure((0, 1, 2), weight=1)

        # Ícones novos para as novas permissões
        icons_map = {
            "Painel": "📊",
            "Agenda": "📅",
            "Financeiro": "💰",
            "Configurações": "⚙️",
            "Cadastro": "📝",
            "Permissões": "🔐"
        }

        for index, perm_name in enumerate(self.permissions_list):
            row, col = divmod(index, 3)
            icon = icons_map.get(perm_name, "🛡️")

            card = ctk.CTkFrame(self.scroll_container, fg_color="#F8F9FA", corner_radius=12, border_width=1, border_color="#E5E7EB")
            card.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(card, text=icon, font=("Arial", 22)).grid(row=0, column=0, padx=(12, 5), pady=12)
            ctk.CTkLabel(card, text=perm_name, font=("Arial", 11, "bold"), text_color="#374151").grid(row=0, column=1, sticky="w")

            sw = ctk.CTkSwitch(
                card, text="", width=45, height=24, progress_color="#1CE437",
                command=lambda p=perm_name: self.sync_permission(p)
            )
            sw.grid(row=0, column=2, padx=(5, 15))
            self.switch_widgets[perm_name] = sw

        self.save_btn = ctk.CTkButton(
            self.right_card, text="Salvar Alterações", font=("Arial", 14, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8", height=45, width=220,
            corner_radius=8, command=self.save_to_database
        )
        self.save_btn.grid(row=1, column=0, pady=25)

        self.toggle_switches_state("disabled")

    def create_admin_row(self, nome, level_text, color):
        row_frame = ctk.CTkFrame(self.admin_list_container, fg_color="transparent", corner_radius=10, cursor="hand2")
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_columnconfigure((0, 1, 2), weight=1)

        lbl_avatar = ctk.CTkLabel(row_frame, text="👤", font=("Arial", 16), text_color=color)
        lbl_avatar.grid(row=0, column=0, sticky="w", padx=15, pady=10)

        lbl_nome = ctk.CTkLabel(row_frame, text=nome, font=("Arial", 12, "bold"), text_color="#374151")
        lbl_nome.grid(row=0, column=1, sticky="w", padx=5)

        lbl_level = ctk.CTkLabel(row_frame, text=level_text, font=("Arial", 11), text_color="#6B7280")
        lbl_level.grid(row=0, column=2, sticky="w", padx=5)

        widgets = [row_frame, lbl_avatar, lbl_nome, lbl_level]
        for w in widgets:
            w.bind("<Button-1>", lambda e, f=row_frame, n=nome: self.on_admin_click(f, n))

        self.admin_rows.append(row_frame)

    def on_admin_click(self, frame, admin_name):
        for row in self.admin_rows:
            row.configure(fg_color="transparent")
        
        frame.configure(fg_color="#F3F4F6")
        self.selected_admin_name = admin_name
        self.toggle_switches_state("normal")

        # Garantir que as chaves de permissão existam para evitar erros se o JSON for antigo
        admin_perms = self.admins_data[admin_name].get("perms", {})
        
        for p_name in self.permissions_list:
            status = admin_perms.get(p_name, False)
            if status:
                self.switch_widgets[p_name].select()
            else:
                self.switch_widgets[p_name].deselect()

    def sync_permission(self, perm_name):
        if self.selected_admin_name:
            new_val = self.switch_widgets[perm_name].get()
            if "perms" not in self.admins_data[self.selected_admin_name]:
                self.admins_data[self.selected_admin_name]["perms"] = {}
            self.admins_data[self.selected_admin_name]["perms"][perm_name] = bool(new_val)

    def toggle_switches_state(self, state):
        for sw in self.switch_widgets.values():
            sw.configure(state=state)

    def save_to_database(self):
        salvar_permissoes(self.admins_data)
        messagebox.showinfo("Sucesso", "Permissões salvas com sucesso!")

# =========================================================
# APP
# =========================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Permissões Pro")
        self.geometry("1100x700")
        tela = Permissoes(self)
        tela.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()