from .base import BaseScreen
import customtkinter as ctk

class Configuracoes(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Configurações")
        ctk.CTkLabel(self.content_card, text="Configurações do sistema.", font=ctk.CTkFont(size=14)).pack(pady=40)
    pass
