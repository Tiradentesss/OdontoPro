from views.base import BaseScreen
import customtkinter as ctk

class Cadastro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Cadastro")
        ctk.CTkEntry(self.content_card, placeholder_text="Nome").pack(padx=40, pady=10)
        ctk.CTkButton(self.content_card, text="Salvar").pack(pady=20)
