import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk(fg_color="#EBEBEB")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()

app.title("login")
# app.geometry(f"{largura}x{altura}")
app.geometry("700x700")

frame_centro = ctk.CTkFrame(app, fg_color="transparent")
frame_centro.pack(pady=20)


frame_login = ctk.CTkFrame(frame_centro, height=300, width=400, corner_radius=10, fg_color="#E0E0E0")
frame_login.grid(pady=20, padx=20, column=1, row=0)

label1 = ctk.CTkLabel(frame_login, text="Login User", font=("Arial", 24))
label1.pack(pady=50)

usuario = ctk.CTkEntry(frame_login, width=300, height=45, placeholder_text="usuario", border_color="gray", fg_color="white", corner_radius=10)
usuario.pack(pady=12, padx=10)

senha = ctk.CTkEntry(frame_login, width=300, height=45, placeholder_text="senha", show="*", border_color="gray", fg_color="white", corner_radius=10)
senha.pack(pady=12, padx=10)

login_botão = ctk.CTkButton(frame_login, text="entrar", height=40, width=120).pack(pady=50)

# ___________________

frame_login2 = ctk.CTkFrame(frame_centro, height=300, width=400, corner_radius=10, fg_color="#E0E0E0")
frame_login2.grid(pady=20, padx=20, column=2, row=0)

label1 = ctk.CTkLabel(frame_login2, text="Login Admin", font=("Arial", 24))
label1.pack(pady=50)

usuario = ctk.CTkEntry(frame_login2, width=300, height=45, placeholder_text="usuario", border_color="gray", fg_color="white", corner_radius=10)
usuario.pack(pady=12, padx=10)

senha = ctk.CTkEntry(frame_login2, width=300, height=45, placeholder_text="senha", show="*", border_color="gray", fg_color="white", corner_radius=10)
senha.pack(pady=12, padx=10)

login_botão = ctk.CTkButton(frame_login2, text="entrar", height=40, width=120).pack(pady=50)



app.mainloop()