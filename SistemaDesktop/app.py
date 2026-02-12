import customtkinter as ctk
import sys
print("PYTHON EXECUTÁVEL:", sys.executable)

from views.painel import Painel
from views.agenda import Agenda
from views.financeiro import Financeiro
from views.cadastro import Cadastro
from views.configuracoes import Configuracoes
from views.login import Login
from views.permissao import Permissoes

from PIL import Image
import customtkinter as ctk
import os


class App(ctk.CTk):
    def logout(self):
        self.withdraw()  # esconde a janela sem matar o Tk

        def abrir_login():
            self.destroy()  # agora sim, depois que o loop esvaziar
            login = Login()
            login.mainloop()

        self.after(100, abrir_login)    

    def __init__(self, usuario_nome="Usuário", tipo_usuario=None, clinica_id=None):
        self.clinica_id = clinica_id
        super().__init__()

        self.usuario_nome = usuario_nome
        self.tipo_usuario = tipo_usuario

        self.title("OdontoPro - Sistema de Gerenciamento")
        self.geometry("1150x750")
        self.minsize(1000, 650)
        self.configure(fg_color="#F5F6FA")

        # Grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.usuario_nome = usuario_nome


        self.title("OdontoPro - Sistema de Gerenciamento")
        self.geometry("1150x750")
        self.minsize(1000, 650)
        self.configure(fg_color="#F5F6FA")

        # Grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= Sidebar =================
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E5E7EB"
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Nome
        ctk.CTkLabel(
            self.sidebar,
            text="OdontoPro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#0d99c7"
        ).pack(pady=(40, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="Clinical Management",
            font=ctk.CTkFont(size=11),
            text_color="#9CA3AF"
        ).pack(pady=(0, 30))

        # Menu
        self.buttons = {}
        if self.tipo_usuario == "gerenciamento":
            self.menu_items = [
                ("▣  Painel", "painel"),
                ("🗓  Agenda", "agenda"),
                ("💰  Financeiro", "financeiro"),
                ("⚙  Configurações", "config"),
            ]
        else:  # clinica
            self.menu_items = [
                ("▣  Painel", "painel"),
                ("🗓  Agenda", "agenda"),
                ("💰  Financeiro", "financeiro"),
                ("⚙  Configurações", "config"),
                ("👤  Cadastro", "cadastro"),
                ("🔒  Permissões", "permissao"),
        ]


        for text, name in self.menu_items:
            self.buttons[name] = self.create_menu_button(text, name)

        # Sair
        ctk.CTkButton(
            self.sidebar,
            text="⎋  Sair do Sistema",
            fg_color="transparent",
            text_color="#EF4444",
            hover_color="#FEE2E2",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.logout
        ).pack(side="bottom", fill="x", padx=20, pady=30)

        # ================= Área Principal =================
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        self.frames = {
            "painel": Painel(self.container),
            "agenda": Agenda(self.container, self.clinica_id),
            "financeiro": Financeiro(self.container),
            "config": Configuracoes(self.container),
            "cadastro": Cadastro(self.container),
            "permissao": Permissoes(self.container),
        }

        self.current_frame = None
        self.show_frame("painel")

    def create_menu_button(self, text, name):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            fg_color="transparent",
            text_color="#4B5563",
            hover_color="#F0F9FF",
            height=46,
            corner_radius=10,
            font=ctk.CTkFont(size=14),
            command=lambda: self.show_frame(name)
        )
        btn.pack(fill="x", padx=16, pady=6)
        return btn

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.pack_forget()

        self.current_frame = self.frames[name]
        self.current_frame.pack(expand=True, fill="both")
        self.update_active_button(name)

    def update_active_button(self, active):
        for name, btn in self.buttons.items():
            if name == active:
                btn.configure(
                    fg_color="#0d99c7",
                    text_color="white",
                    hover_color="#0b86af"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color="#4B5563",
                    hover_color="#F0F9FF"
                )

    pass

if __name__ == "__main__":
    Login().mainloop()
