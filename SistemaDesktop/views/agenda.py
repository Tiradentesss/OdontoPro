from views.base import BaseScreen
from models.data import CONSULTAS_DATA
import customtkinter as ctk

class Agenda(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Agenda")

        for nome, data, hora, status in CONSULTAS_DATA:
            ctk.CTkLabel(
                self.content_card,
                text=f"{nome} - {data} {hora} ({status})"
            ).pack(anchor="w", padx=20, pady=5)
