import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk(fg_color="#EBEBEB")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()

app.title("Login")
app.geometry(f"{largura}x{altura}")

# ===== CONTAINER CENTRAL =====
container = ctk.CTkFrame(app, fg_color="transparent")
container.pack(expand=True)

# ===== PAINEL ESQUERDO =====
frame_esquerdo = ctk.CTkFrame(
    container,
    width=450,
    height=520,
    corner_radius=20,
    fg_color="#2ECC71"
)
frame_esquerdo.grid(row=0, column=0, padx=20, pady=20)

titulo = ctk.CTkLabel(
    frame_esquerdo,
    text="Bem-vindo!",
    font=("Arial", 32, "bold"),
    text_color="white"
)
titulo.pack(pady=(100, 20))

descricao = ctk.CTkLabel(
    frame_esquerdo,
    text="Acesse sua conta\npara continuar",
    font=("Arial", 18),
    text_color="white"
)
descricao.pack()

# ===== PAINEL DIREITO (FORM) =====
frame_direito = ctk.CTkFrame(
    container,
    width=450,
    height=520,
    corner_radius=20,
    fg_color="white"
)
frame_direito.grid(row=0, column=1, padx=20, pady=20)

# ---- ESPAÇO PARA LOGO ----
logo = ctk.CTkLabel(
    frame_direito,
    text="[ SEU LOGO AQUI ]",
    font=("Arial", 18),
    text_color="#999",
    width=200,
    height=80
)
logo.pack(pady=(30, 10))

titulo_login = ctk.CTkLabel(
    frame_direito,
    text="Faça Login com sua conta",
    font=("Arial", 22, "bold"),
    text_color="#333"
)
titulo_login.pack(pady=10)

usuario = ctk.CTkEntry(
    frame_direito,
    width=320,
    height=45,
    placeholder_text="Usuário",
    border_color="#CCC",
    fg_color="white",
    corner_radius=12
)
usuario.pack(pady=10)

senha = ctk.CTkEntry(
    frame_direito,
    width=320,
    height=45,
    placeholder_text="Senha",
    show="*",
    border_color="#CCC",
    fg_color="white",
    corner_radius=12
)
senha.pack(pady=10)

# ---- BOTÃO PRINCIPAL ----
botao_login = ctk.CTkButton(
    frame_direito,
    text="Entrar",
    height=45,
    width=220,
    corner_radius=12,
    fg_color="#2ECC71",
    hover_color="#28B463",
    font=("Arial", 16, "bold")
)
botao_login.pack(pady=20)

# ---- OUTROS BOTÕES ----
botao_cadastro = ctk.CTkButton(
    frame_direito,
    text="Criar nova conta",
    height=40,
    width=220,
    corner_radius=12,
    fg_color="#3498DB",
    hover_color="#2E86C1",
    font=("Arial", 14)
)
botao_cadastro.pack(pady=5)

botao_esqueci = ctk.CTkButton(
    frame_direito,
    text="Esqueci minha senha",
    height=35,
    width=220,
    corner_radius=12,
    fg_color="#95A5A6",
    hover_color="#7F8C8D",
    font=("Arial", 13)
)
botao_esqueci.pack(pady=5)

app.mainloop()
