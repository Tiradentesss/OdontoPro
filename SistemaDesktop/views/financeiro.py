from views.base import BaseScreen
import customtkinter as ctk

class Financeiro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Financeiro")
        ctk.CTkLabel(self.content_card, text="Financeiro").pack(pady=40)
