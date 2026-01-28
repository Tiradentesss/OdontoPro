import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk(fg_color="#EBEBEB")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()

app.title("login")
# app.geometry(f"{largura}x{altura}")
app.geometry("1000x600")

container = ctk.CTkFrame(app, corner_radius=20)
container.pack(expand=True, fill="both", padx=20, pady=20)

container.grid_columnconfigure((0, 1, 2), weight=1)
container.grid_rowconfigure((1, 2), weight=1)

ctk.CTkLabel(container, text="Painel Administrativo", font=("Arial", 30, "bold"))

cards = [
    "usuarios",
    "produtos",
    "financeiro",
    "configurações",
    "banco de dados"
]

linha = 1
coluna = 0

for card in cards:
    frame = ctk.CTkFrame(container, height=120)
    frame.grid(row=linha, column=coluna, padx=15, pady=15, sticky="nsew")
    frame.grid_propagate(False)

    ctk.CTkLabel(frame, text=card, font=("Arial", 18)).pack(expand=True)

    coluna += 1
    if coluna > 2:
        coluna = 0
        linha += 1

app.mainloop()