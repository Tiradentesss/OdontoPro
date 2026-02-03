# views/app.py

import customtkinter as ctk
from views.painel import Painel
from views.agenda import Agenda
from views.financeiro import Financeiro
from views.cadastro import Cadastro
from views.configuracoes import Configuracoes

class App(ctk.CTk):
    def __init__(self, usuario_nome):
        super().__init__()

        self.title("OdontoPro")
        self.geometry("1150x750")

        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {
            "painel": Painel(self.container),
            "agenda": Agenda(self.container),
            "financeiro": Financeiro(self.container),
            "cadastro": Cadastro(self.container),
            "config": Configuracoes(self.container),
        }

        self.show_frame("painel")

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
