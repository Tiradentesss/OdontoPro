import customtkinter as ctk
import os
from PIL import Image
from tkinter import messagebox

from controllers.auth_controller import AuthController


class Login(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login - OdontoPro")

        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()
        self.geometry(f"{largura}x{altura}")
        self.configure(fg_color="#F2F3F5")

        BASE_DIR = os.path.dirname(os.path.dirname(__file__))

        ASSETS_DIR = os.path.join(BASE_DIR, "assets")

        # ================= GRID 50/50 =================
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= IMAGENS =================
        logo_pil = Image.open(os.path.join(ASSETS_DIR, "logo.png"))

        logo_prop = logo_pil.width / logo_pil.height
        logo_w = 260
        logo_h = int(logo_w / logo_prop)

        logo_img = ctk.CTkImage(
            light_image=logo_pil,
            dark_image=logo_pil,
            size=(logo_w, logo_h)
        )

        dentista_pil = Image.open(os.path.join(ASSETS_DIR, "dentistalogin.png"))

        dentista_prop = dentista_pil.width / dentista_pil.height
        dentista_w = int(largura * 0.42)
        dentista_h = int(dentista_w / dentista_prop)

        dentista_img = ctk.CTkImage(
            light_image=dentista_pil,
            dark_image=dentista_pil,
            size=(dentista_w, dentista_h)
        )


        # ================= ESQUERDA =================
        frame_img = ctk.CTkFrame(self, fg_color="#F2F3F5", corner_radius=0)
        frame_img.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            frame_img,
            text="",
            image=dentista_img
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ================= DIREITA =================
        frame_login = ctk.CTkFrame(self, fg_color="#F2F3F5", corner_radius=0)
        frame_login.grid(row=0, column=1, sticky="nsew")

        # 🔑 SCROLL REAL (FUNCIONA)
        scroll = ctk.CTkScrollableFrame(
            frame_login,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True)

        conteudo = ctk.CTkFrame(scroll, fg_color="transparent")
        conteudo.pack(anchor="center", pady=40)

        # ================= CONTEÚDO =================

        ctk.CTkLabel(
            conteudo,
            text="",
            image=logo_img
        ).pack(anchor="w", pady=(0, 40))

        ctk.CTkLabel(
            conteudo,
            text="Acesse sua conta",
            font=("Arial", 28, "bold"),
            text_color="#1C1C1C"
        ).pack(anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="Bem-vindo de volta! Entre com seus dados.",
            font=("Arial", 14),
            text_color="#666666"
        ).pack(anchor="w", pady=(0, 25))

        self.ent_user = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Usuário",
            fg_color="white",
            border_width=0
        )
        self.ent_user.pack(pady=10, anchor="w")

        self.ent_pass = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Senha",
            show="*",
            fg_color="white",
            border_width=0
        )
        self.ent_pass.pack(pady=10, anchor="w")

        linha = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha.pack(fill="x", pady=10)

        ctk.CTkCheckBox(linha, text="Lembrar-me").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            linha,
            text="Esqueci minha senha",
            text_color="#0A66C2"
        ).grid(row=0, column=1, sticky="e")
        linha.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            conteudo,
            text="ENTRAR",
            width=420,
            height=50,
            fg_color="#0A66C2",
            hover_color="#0959A8",
            font=("Arial", 12, "bold"),
            command=self.autenticar
        ).pack(pady=15, anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="────────────  ou continue com  ────────────",
            text_color="#999"
        ).pack(pady=15)

        ctk.CTkButton(
            conteudo,
            text="Entrar com Google",
            width=420,
            height=48,
            fg_color="#0A66C2",
            hover_color="#0959A8",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        ctk.CTkButton(
            conteudo,
            text="Entrar com Facebook",
            width=420,
            height=48,
            fg_color="#0A66C2",
            hover_color="#0959A8",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        rodape = ctk.CTkFrame(conteudo, fg_color="transparent")
        rodape.pack(pady=15)

        ctk.CTkLabel(rodape, text="Não tem conta?").grid(row=0, column=0)
        ctk.CTkLabel(
            rodape,
            text=" Cadastre-se",
            text_color="#0A66C2",
            font=("Arial", 13, "bold")
        ).grid(row=0, column=1)

    def autenticar(self):
        email = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()

        if not email or not senha:
            messagebox.showwarning("Atenção", "Preencha e-mail e senha")
            return

        resultado = AuthController.autenticar(email, senha)

        if not resultado:
            messagebox.showwarning("Atenção", "E-mail ou senha inválidos")
            return

        usuario = resultado["usuario"]

        self.destroy()

        from app import App
        app = App(
            usuario_nome=usuario["nome"],
            tipo_usuario=usuario["tipo"]
        )
        app.mainloop()