from .base import BaseScreen
import customtkinter as ctk



class Permissoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Permissões") # "Permissões" serve para o título da tela

        # Limpa layout padrão do BaseScreen
        for widget in self.winfo_children():
            widget.destroy()

        # Grid principal
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # Títulos
        ctk.CTkLabel(
            self,
            text="Current Administrators",
            font=("Arial", 18, "bold"),
            text_color="#111827"
        ).grid(row=0, column=0, sticky="w", pady=(0, 15))

        ctk.CTkLabel(
            self,
            text="Add New Administrator",
            font=("Arial", 18, "bold"),
            text_color="#111827"
        ).grid(row=0, column=1, sticky="w", pady=(0, 15), padx=20)

        # ===============================
        # COLUNA ESQUERDA - TABELA
        # ===============================
        left_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 20))

        headers = ["Avatar", "Name", "Email", "Permission Level"]
        header_frame = ctk.CTkFrame(left_card, fg_color="#F3F4F6", height=40)
        header_frame.pack(fill="x", padx=15, pady=15)

        for i, h in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=h,
                font=("Arial", 12, "bold"),
                text_color="#374151"
            ).grid(row=0, column=i, padx=15, sticky="w")

        admins = [
            ("John Doe", "Admin", "180", "Admin", "#9CA3AF"),
            ("Jane Smith", "Manager", "189", "Billing", "#9CA3AF"),
            ("Jane Smith", "Repager", "192", "Reporting", "#10B981"),
            ("Locaritn Ltrntan", "Repular", "128", "Read-Only", "#10B981"),
        ]

        for nome, role, num, perm_text, perm_color in admins:
            row = ctk.CTkFrame(left_card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)

            avatar = ctk.CTkFrame(row, width=34, height=34, corner_radius=17, fg_color="#E5E7EB")
            avatar.pack(side="left", padx=(10, 15))
            ctk.CTkLabel(avatar, text="👤").place(relx=0.5, rely=0.5, anchor="center")

            ctk.CTkLabel(row, text=nome).pack(side="left")

            perm_badge = ctk.CTkFrame(row, fg_color=perm_color, corner_radius=6)
            perm_badge.pack(side="right")
            ctk.CTkLabel(
                perm_badge,
                text=perm_text,
                text_color="white",
                font=("Arial", 11, "bold"),
                padx=10
            ).pack(pady=2)

        # ===============================
        # COLUNA DIREITA - FORMULÁRIO
        # ===============================
        right_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        right_card.grid(row=1, column=1, sticky="nsew")

        ctk.CTkLabel(
            right_card,
            text="System Permissions",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 15))

        ctk.CTkEntry(
            right_card,
            placeholder_text="Full Name",
            height=35
        ).pack(fill="x", padx=25, pady=5)

        ctk.CTkEntry(
            right_card,
            placeholder_text="Email Address",
            height=35
        ).pack(fill="x", padx=25, pady=5)

        perms = [
            "Analytics",
            "User Management",
            "Billing Reporting",
            "Content Moderation"
        ]

        for perm in perms:
            row = ctk.CTkFrame(right_card, fg_color="transparent")
            row.pack(fill="x", padx=25, pady=6)

            ctk.CTkLabel(row, text=perm).pack(side="left")
            ctk.CTkSwitch(row, text="").pack(side="right")

        ctk.CTkButton(
            right_card,
            text="Save Administrator",
            fg_color="#2563EB",
            height=40
        ).pack(pady=25)
    pass
