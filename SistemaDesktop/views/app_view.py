import customtkinter as ctk
from views.Painel import Painel
from views.agenda import Agenda
from views.financeiro import Financeiro
from views.cadastro import Cadastro
from views.configuracoes import Configuracoes

class App(ctk.CTk):
    def __init__(self, usuario_nome):
        super().__init__()

        self.title("OdontoPro")
        self.geometry("1100x700")

        menu = ctk.CTkFrame(self, width=200)
        menu.pack(side="left", fill="y")

        container = ctk.CTkFrame(self)
        container.pack(side="right", expand=True, fill="both")

        self.frames = {
            "painel": Painel(container),
            "agenda": Agenda(container),
            "financeiro": Financeiro(container),
            "cadastro": Cadastro(container),
            "config": Configuracoes(container),
        }

        for f in self.frames.values():
            f.pack_forget()

        def show(name):
            for f in self.frames.values():
                f.pack_forget()
            self.frames[name].pack(expand=True, fill="both")

        for txt, key in [
            ("Painel", "painel"),
            ("Agenda", "agenda"),
            ("Financeiro", "financeiro"),
            ("Cadastro", "cadastro"),
            ("Config", "config"),
        ]:
            ctk.CTkButton(menu, text=txt, command=lambda k=key: show(k)).pack(fill="x", padx=10, pady=5)

        show("painel")