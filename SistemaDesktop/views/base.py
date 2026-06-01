import customtkinter as ctk
from .theme import font, COLORS

class ActionButtons(ctk.CTkFrame):
    """Componente padronizado para botões de ação (Salvar/Cancelar ou Salvar/Limpar)"""
    def __init__(self, parent, primary_text="SALVAR", secondary_text="CANCELAR", 
                 on_primary=None, on_secondary=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Botão Primário (Salvar)
        self.primary_btn = ctk.CTkButton(
            self,
            text=primary_text,
            font=font("button_large", "bold"),
            height=40,
            width=180,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            corner_radius=6,
            border_width=0,
            command=on_primary
        )
        self.primary_btn.pack(side="left", padx=(0, 12))
        
        # Botão Secundário (Cancelar/Limpar)
        self.secondary_btn = ctk.CTkButton(
            self,
            text=secondary_text,
            font=font("button_large", "bold"),
            height=40,
            width=140,
            fg_color="#DC2626",
            hover_color="#991B1B",
            text_color="white",
            border_width=2,
            border_color="#7F1D1D",
            corner_radius=6,
            command=on_secondary
        )
        self.secondary_btn.pack(side="left")

class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text=title,
            font=font("title", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 20))

        self.content_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.content_card.pack(expand=True, fill="both", padx=20, pady=20)
