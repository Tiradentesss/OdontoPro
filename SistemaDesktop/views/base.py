import customtkinter as ctk

class BaseScreen(ctk.CTkFrame):
    def __init__(self, parent, title):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1F2937"
        ).pack(anchor="w", pady=(0, 20))

        self.content_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=18,
            border_width=1,
            border_color="#E5E7EB"
        )
        self.content_card.pack(expand=True, fill="both")
