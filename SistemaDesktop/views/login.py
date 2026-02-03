import customtkinter as ctk
from models.data import USUARIOS
from views.app_view import App

class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login")
        self.geometry("400x300")

        self.user = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.user.pack(pady=10)

        self.senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.senha.pack(pady=10)

        ctk.CTkButton(self, text="Entrar", command=self.login).pack(pady=20)

    def login(self):
        u = self.user.get()
        s = self.senha.get()

        if u in USUARIOS and USUARIOS[u]["senha"] == s:
            self.destroy()
            App(USUARIOS[u]["nome"]).mainloop()
