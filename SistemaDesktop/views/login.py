import customtkinter as ctk
import os
from PIL import Image
from tkinter import messagebox

from controllers.auth_controller import AuthController
from controllers.gerenciamento_controller import GerenciamentoController
from services.remember_me_service import carregar_credenciais, salvar_credenciais, limpar_credenciais
from .theme import font, ICON_SIZE, COLORS, ASSETS_DIR, get_brand_logo_path, get_dark_mode


class Login(ctk.CTk):
    def __init__(self, on_success=None, auto_login_enabled=False):
        super().__init__()
        self.on_success = on_success
        self.auto_login_enabled = auto_login_enabled  # Flag para permitir auto-login
        self.title("Login - OdontoPro")

        self.update_idletasks()

        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()

        self.geometry(f"{largura}x{altura}+0+0")

        self.configure(fg_color=COLORS["content_bg"])

        # ================= GRID 50/50 =================
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= IMAGENS =================
        # Carrega logo do brand ou usa fallback silencioso se não existir
        logo_img = None
        try:
            logo_path = get_brand_logo_path() or os.path.join(ASSETS_DIR, "logo.png")
            if logo_path and os.path.exists(logo_path):
                logo_pil = Image.open(logo_path)
                logo_prop = logo_pil.width / logo_pil.height
                logo_w = 260
                logo_h = int(logo_w / logo_prop)
                logo_img = ctk.CTkImage(
                    light_image=logo_pil,
                    dark_image=logo_pil,
                    size=(logo_w, logo_h)
                )
        except Exception:
            logo_img = None

        # Imagem lateral (dentista) — se não existir, ignorar
        dentista_img = None
        try:
            dentista_path = os.path.join(ASSETS_DIR, "dentistalogin.png")
            if os.path.exists(dentista_path):
                dentista_pil = Image.open(dentista_path)
                dentista_prop = dentista_pil.width / dentista_pil.height
                dentista_w = int(largura * 0.42)
                dentista_h = int(dentista_w / dentista_prop)
                dentista_img = ctk.CTkImage(
                    light_image=dentista_pil,
                    dark_image=dentista_pil,
                    size=(dentista_w, dentista_h)
                )
        except Exception:
            dentista_img = None


        # ================= ESQUERDA =================
        frame_img = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        frame_img.grid(row=0, column=0, sticky="nsew")

        if dentista_img:
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
        conteudo.pack(anchor="center", pady=(60, 0))

        # ================= CONTEÚDO =================

        # Exibe um badge com a marca no topo da área de login (procura por imagens OdontoHub)
        brand_badge_img = None
        try:
            # Se estiver em tema escuro, usar a versão branca/clara
            if get_dark_mode():
                brand_logo_path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf (1).png")
            else:
                brand_logo_path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf.png")
            
            if os.path.exists(brand_logo_path):
                pil = Image.open(brand_logo_path)
                prop = pil.width / pil.height if pil.height else 1
                w = 450
                h = int(w / prop)
                brand_badge_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(w, h))
            elif logo_img:
                # usar o logo já carregado como fallback
                brand_badge_img = logo_img
        except Exception:
            brand_badge_img = logo_img

        if brand_badge_img:
            badge_frame = ctk.CTkFrame(conteudo, fg_color=COLORS["card"], corner_radius=12)
            badge_frame.pack(anchor="center", pady=(0, 16))
            ctk.CTkLabel(
                badge_frame,
                text="",
                image=brand_badge_img
            ).pack(padx=12, pady=12)
        else:
            ctk.CTkLabel(
                conteudo,
                text="OdontoHub",
                font=font("title", "bold"),
                text_color=COLORS["primary"]
            ).pack(anchor="center", pady=(0, 20))

        ctk.CTkLabel(
            conteudo,
            text="Acesse sua conta",
            font=font("title", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="center")

        ctk.CTkLabel(
            conteudo,
            text="Bem-vindo de volta! Entre com seus dados.",
            font=font("subtitle"),
            text_color=COLORS["muted"]
        ).pack(anchor="center", pady=(0, 20))

        self.ent_user = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Usuário",
            fg_color=COLORS["card"],
            border_width=0
        )
        self.ent_user.pack(pady=(0, 10), anchor="center")

        self.ent_pass = ctk.CTkEntry(
            conteudo,
            width=420,
            height=50,
            placeholder_text="Senha",
            show="*",
            fg_color=COLORS["card"],
            border_width=0
        )
        self.ent_pass.pack(pady=(0, 10), anchor="center")

        self.remember_var = ctk.BooleanVar(value=False)
        linha = ctk.CTkFrame(conteudo, fg_color="transparent")
        linha.pack(anchor="center", pady=(0, 12))

        chk = ctk.CTkCheckBox(linha, text="Lembrar-me", variable=self.remember_var)
        chk.pack(side="left", padx=(0, 8))
        # Quando o usuário alterna 'Lembrar-me', salvar/limpar credenciais imediatamente
        try:
            # trace_add para tkinter moderno
            self.remember_var.trace_add('write', lambda *args: self._on_remember_toggle())
        except AttributeError:
            # fallback para versões antigas
            self.remember_var.trace('w', lambda *args: self._on_remember_toggle())
        ctk.CTkLabel(
            linha,
            text="Esqueci minha senha",
            text_color=COLORS["primary"]
        ).pack(side="left")

        ctk.CTkButton(
            conteudo,
            text="ENTRAR",
            width=420,
            height=50,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=font("button", "bold"),
            command=self.autenticar
        ).pack(pady=(20, 15), anchor="center")

        ctk.CTkLabel(
            conteudo,
            text="────────────  ou continue com  ────────────",
            text_color=COLORS["muted"]
        ).pack(pady=(15, 12))

        ctk.CTkButton(
            conteudo,
            text="Entrar com Google",
            width=420,
            height=48,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=font("button", "bold")
        ).pack(pady=(0, 6), anchor="center")

        ctk.CTkButton(
            conteudo,
            text="Entrar com Facebook",
            width=420,
            height=48,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=font("button", "bold")
        ).pack(pady=(0, 16), anchor="center")

        rodape = ctk.CTkFrame(conteudo, fg_color="transparent")
        rodape.pack(anchor="center", pady=(0, 0))

        ctk.CTkLabel(rodape, text="Não tem conta?").grid(row=0, column=0)
        ctk.CTkLabel(
            rodape,
            text=" Cadastre-se",
            text_color=COLORS["primary"],
            font=font("button", "bold")
        ).grid(row=0, column=1)

        self._carregar_credenciais_salvas()

        # Salvar automaticamente os campos quando perderem foco se 'Lembrar-me' estiver ativo
        try:
            self.ent_user.bind("<FocusOut>", self._on_field_focus_out)
            self.ent_pass.bind("<FocusOut>", self._on_field_focus_out)
        except Exception:
            pass

    def _on_remember_toggle(self):
        """Handler chamado quando o checkbox 'Lembrar-me' muda de estado."""
        if self.remember_var.get():
            email = self.ent_user.get().strip()
            senha = self.ent_pass.get().strip()
            # Salvar mesmo que campos estejam vazios — manter último estado
            salvar_credenciais(email, senha)
        else:
            limpar_credenciais()

    def _on_field_focus_out(self, event):
        """Se 'Lembrar-me' estiver ativo, salva campos ao perder foco."""
        if self.remember_var.get():
            email = self.ent_user.get().strip()
            senha = self.ent_pass.get().strip()
            salvar_credenciais(email, senha)

    def _carregar_credenciais_salvas(self):
        """Carrega credenciais salvas e pré-preenche os campos
        
        Auto-login é feito apenas se auto_login_enabled=True (primeira inicialização)
        """
        dados = carregar_credenciais()
        if not dados:
            return

        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            return

        # Pré-preencher os campos com credenciais salvas
        self.ent_user.insert(0, email)
        self.ent_pass.insert(0, senha)
        self.remember_var.set(True)
        
        # Fazer auto-login apenas se habilitado (primeira inicialização)
        if self.auto_login_enabled:
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

        # Se estiver usando callback (modo com MainWindow), chamar callback
        if self.on_success:
            # Destruir a janela de login
            self.withdraw()  # Esconder antes de destruir
            self.destroy()
            
            # Chamar callback com dados do usuário
            self.on_success(
                usuario["nome"],
                usuario["id"],
                usuario["tipo"],
                usuario["clinica_id"]
            )
        else:
            # Modo CTk puro (compatibilidade com versão anterior)
            self.destroy()

            from app import App
            app = App(
                usuario_nome=usuario["nome"],
                usuario_id=usuario["id"],
                tipo_usuario=usuario["tipo"],
                clinica_id=usuario["clinica_id"]
            )
            app.mainloop()