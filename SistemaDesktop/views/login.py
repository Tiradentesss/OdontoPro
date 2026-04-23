import customtkinter as ctk
import os
from PIL import Image
from tkinter import messagebox

from controllers.auth_controller import AuthController
from controllers.gerenciamento_controller import GerenciamentoController
from services.remember_me_service import carregar_credenciais, salvar_credenciais, limpar_credenciais
from .theme import font, ICON_SIZE, COLORS


class Login(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - OdontoPro")

        self.update_idletasks()

        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()

        self.geometry(f"{largura}x{altura}+0+0")

        self.configure(fg_color=COLORS["content_bg"])

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
        frame_img = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        frame_img.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            frame_img,
            text="",
            image=dentista_img
        ).place(relx=0.5, rely=0.5, anchor="center")

        # ================= DIREITA =================
        frame_login = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
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
            font=font("title", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="Bem-vindo de volta! Entre com seus dados.",
            font=font("subtitle"),
            text_color=COLORS["muted"]
        ).pack(anchor="w", pady=(0, 25))

        self.ent_user = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Usuário",
            fg_color=COLORS["card"],
            border_width=0
        )
        self.ent_user.pack(pady=10, anchor="w")

        self.ent_pass = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Senha",
            show="*",
            fg_color=COLORS["card"],
            border_width=0
        )
        self.ent_pass.pack(pady=10, anchor="w")

        self.remember_var = ctk.BooleanVar(value=False)
        linha = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha.pack(fill="x", pady=10)

        ctk.CTkCheckBox(linha, text="Lembrar-me", variable=self.remember_var).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            linha,
            text="Esqueci minha senha",
            text_color=COLORS["primary"]
        ).grid(row=0, column=1, sticky="e")
        linha.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            conteudo,
            text="ENTRAR",
            width=420,
            height=50,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=font("button", "bold"),
            command=self.autenticar
        ).pack(pady=15, anchor="w")

        ctk.CTkLabel(
            conteudo,
            text="────────────  ou continue com  ────────────",
            text_color=COLORS["muted"]
        ).pack(pady=15)

        ctk.CTkButton(
            conteudo,
            text="Entrar com Google",
            width=420,
            height=48,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=font("button", "bold")
        ).pack(pady=5)

        ctk.CTkButton(
            conteudo,
            text="Entrar com Facebook",
            width=420,
            height=48,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=font("button", "bold")
        ).pack(pady=5)

        rodape = ctk.CTkFrame(conteudo, fg_color="transparent")
        rodape.pack(pady=15)

        ctk.CTkLabel(rodape, text="Não tem conta?").grid(row=0, column=0)
        ctk.CTkLabel(
            rodape,
            text=" Cadastre-se",
            text_color=COLORS["primary"],
            font=font("button", "bold")
        ).grid(row=0, column=1)

        self._carregar_credenciais_salvas()

    def _carregar_credenciais_salvas(self):
        dados = carregar_credenciais()
        if not dados:
            return

        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            return

        self.ent_user.insert(0, email)
        self.ent_pass.insert(0, senha)
        self.remember_var.set(True)
        self.after(300, lambda: self.autenticar(auto_login=True))

    def autenticar(self, auto_login=False):
        email = self.ent_user.get().strip()
        senha = self.ent_pass.get().strip()

        if not email or not senha:
            if not auto_login:
                messagebox.showwarning("Atenção", "Preencha e-mail e senha")
            return

        try:
            resultado = AuthController.autenticar(email, senha)
        except Exception as e:
            if not auto_login:
                messagebox.showerror("Erro de conexão", f"Falha ao conectar ao banco: {e}")
            return

        if not resultado:
            if not auto_login:
                messagebox.showwarning("Atenção", "E-mail ou senha inválidos ou servidor indisponível")
            return

        if self.remember_var.get():
            salvar_credenciais(email, senha)
        else:
            limpar_credenciais()

        usuario = resultado["usuario"]

        # Inicializar permissões padrão no BD (se não existirem)
        resultado_perms = GerenciamentoController.inicializar_permissoes_padrao()
        if not resultado_perms.get("sucesso"):
            print(f"[AVISO LOGIN] Falha ao inicializar permissões: {resultado_perms.get('mensagem')}")

        self.destroy()

        from app import App
        app = App(
            usuario_nome=usuario["nome"],
            usuario_id=usuario["id"],
            tipo_usuario=usuario["tipo"],
            clinica_id=usuario["clinica_id"]
        )
        app.mainloop()