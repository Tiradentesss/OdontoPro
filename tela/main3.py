import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk(fg_color="#EBEBEB")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()

app.title("login")
# app.geometry(f"{largura}x{altura}")
app.geometry("700x700")

container = ctk.CTkFrame(app, corner_radius=20)
container.pack(expand=True, fill="both", padx=30, pady=30)

top_frame = ctk.CTkFrame(container, fg_color="transparent")
top_frame.pack(fill="x", pady=(10, 20))

def criar_card(parent, titulo, valor):
    card = ctk.CTkFrame(parent, height=120, corner_radius=15)
    card.pack(side="left", expand=True, fill="both", padx=10)

    ctk.CTkLabel(card, text=titulo, font=("Arial", 16)).pack(pady=(20, 5))
    ctk.CTkLabel(card, text=valor, font=("Arial", 16, "bold")).pack()

criar_card(top_frame, "👨usuarios", "128")
criar_card(top_frame, "💰vendas", "R$ 9.450")
criar_card(top_frame, "⚠️alertas", "3")

table_frame = ctk.CTkFrame(container)
table_frame.pack(expand=True, fill="both", padx=10, pady=10)

table_frame.grid_columnconfigure((0, 1, 2), weight=1)

headers = ["Nome", "Email", "Status"]
for col, texto in enumerate(headers):
    ctk.CTkLabel(table_frame,text=texto, font=("Arial", 16, "bold")).grid(row=0, column=col, padx=10, pady=10)

    dados = [
        ("Ana", "ana@gmail.com", "Ativo"),
        ("Carlos", "carlos@gmail.com", "Inativo"),
        ("Maria", "maria@gmail.com", "Ativo")
    ]

    for row, linha in enumerate(dados, start=1):
        for col, valor in enumerate(linha):
            ctk.CTkLabel(table_frame, text=valor, font=("Arial", 14),).grid(row=row, column=col, padx=10, pady=8)

app.mainloop()