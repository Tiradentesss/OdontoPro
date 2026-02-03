import customtkinter as ctk

class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(anchor="w", pady=(0, 20))

        self.content_card = ctk.CTkFrame(self, corner_radius=18)
        self.content_card.pack(expand=True, fill="both")
