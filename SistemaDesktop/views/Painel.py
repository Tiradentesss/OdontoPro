from views.base import BaseScreen
import customtkinter as ctk

class Painel(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Painel")
        ctk.CTkLabel(self.content_card, text="Painel principal").pack(pady=40)
