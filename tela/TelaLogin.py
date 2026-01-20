import customtkinter as ctk
from PIL import Image
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Login - OdontoPro")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()
app.geometry(f"{largura}x{altura}")

caminho = os.path.dirname(__file__)

# ===== IMAGENS PROPORCIONAIS =====
logo_original = Image.open(os.path.join(caminho, "logo.png"))
proporcao = logo_original.width / logo_original.height

img_logo = ctk.CTkImage(
    logo_original,
    size=(int(75 * proporcao), 75)   # LOGO MENOR E CORRETA
)

img_dentista = ctk.CTkImage(
    Image.open(os.path.join(caminho, "dentistalogin.png")),
    size=(largura // 2, altura)
)

# ===== GRID 50/50 =====
app.grid_columnconfigure(0, weight=1, uniform="a")
app.grid_columnconfigure(1, weight=1, uniform="a")
app.grid_rowconfigure(0, weight=1)

# ===== ESQUERDA - IMAGEM =====
frame_img = ctk.CTkFrame(app, fg_color="black", corner_radius=0)
frame_img.grid(row=0, column=0, sticky="nsew")

ctk.CTkLabel(frame_img, text="", image=img_dentista).place(relwidth=1, relheight=1)

# ===== DIREITA - LOGIN =====
frame_login = ctk.CTkFrame(app, fg_color="#F2F3F5", corner_radius=0)
frame_login.grid(row=0, column=1, sticky="nsew")

# >>> CONTEÚDO TODO À ESQUERDA E NO TOPO <<<
conteudo = ctk.CTkFrame(frame_login, fg_color="transparent")
conteudo.pack(anchor="nw", padx=70, pady=40)

# ----- LOGO -----
ctk.CTkLabel(conteudo, text="", image=img_logo).pack(anchor="w", pady=(0, 10))

# ----- TITULOS -----
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
).pack(anchor="w", pady=(0, 20))

# ----- CAMPOS (BRANCOS E SEM BORDA) -----
usuario = ctk.CTkEntry(
    conteudo,
    width=420,
    height=50,
    placeholder_text="Usuário",
    fg_color="white",
    border_width=0
)
usuario.pack(pady=8, anchor="w")

senha = ctk.CTkEntry(
    conteudo,
    width=420,
    height=50,
    placeholder_text="Senha",
    show="*",
    fg_color="white",
    border_width=0
)
senha.pack(pady=8, anchor="w")

# ----- OPÇÕES -----
linha = ctk.CTkFrame(conteudo, fg_color="transparent")
linha.pack(fill="x", pady=5)

ctk.CTkCheckBox(linha, text="Lembrar-me").grid(row=0, column=0)

ctk.CTkLabel(
    linha,
    text="Esqueci minha senha",
    text_color="#0A66C2"
).grid(row=0, column=1, sticky="e")

linha.grid_columnconfigure(1, weight=1)

# ----- BOTÃO ENTRAR (COR CORRETA) -----
ctk.CTkButton(
    conteudo,
    text="ENTRAR",
    width=420,
    height=50,
    fg_color="#0A66C2",
    hover_color="#0959A8",
    corner_radius=8
).pack(pady=15, anchor="w")

# ----- SEPARADOR -----
ctk.CTkLabel(
    conteudo,
    text="────────────  ou continue com  ────────────",
    text_color="#999"
).pack(pady=10, anchor="w")

# ----- BOTÕES SOCIAIS (MESMA COR CORRETA) -----
ctk.CTkButton(
    conteudo,
    text="Entrar com Google",
    width=420,
    height=48,
    fg_color="#0A66C2",
    hover_color="#0959A8",
    corner_radius=8
).pack(pady=5, anchor="w")

ctk.CTkButton(
    conteudo,
    text="Entrar com Facebook",
    width=420,
    height=48,
    fg_color="#0A66C2",
    hover_color="#0959A8",
    corner_radius=8
).pack(pady=5, anchor="w")

# ----- CADASTRO -----
rodape = ctk.CTkFrame(conteudo, fg_color="transparent")
rodape.pack(pady=10, anchor="w")

ctk.CTkLabel(rodape, text="Não tem conta?").grid(row=0, column=0)

ctk.CTkLabel(
    rodape,
    text=" Cadastre-se",
    text_color="#0A66C2",
    font=("Arial", 13, "bold")
).grid(row=0, column=1)

app.mainloop()