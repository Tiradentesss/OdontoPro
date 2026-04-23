import customtkinter as ctk
from .theme import font, COLORS

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
