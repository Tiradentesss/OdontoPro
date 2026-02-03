import customtkinter as ctk
from views.theme import COLORS, FONTS

class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color=COLORS["bg"])

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            header,
            text=title,
            font=FONTS["title"],
            text_color=COLORS["text"]
        ).pack(anchor="w")

        self.content_card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=18
        )
        self.content_card.pack(
            expand=True,
            fill="both",
            padx=30,
            pady=20
        )
