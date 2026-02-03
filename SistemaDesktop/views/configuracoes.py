from views.base import BaseScreen
import customtkinter as ctk

class Configuracoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Configurações")
        ctk.CTkLabel(self.content_card, text="Configurações").pack(pady=40)
