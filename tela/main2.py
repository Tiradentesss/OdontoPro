import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

app = ctk.CTk(fg_color="#EBEBEB")

largura = app.winfo_screenwidth()
altura = app.winfo_screenheight()

app.title("login")
# app.geometry(f"{largura}x{altura}")
app.geometry("700x700")

frame_centro = ctk.CTkFrame(app, fg_color="gray")
frame_centro.pack(expand=True, fill="both",  padx=30, pady=30)

label1 = ctk.CTkLabel(frame_centro, text="faça login", font=("Arial", 24))
label1.pack(pady=50)

frame_login = ctk.CTkFrame(frame_centro, height=300, width=400, corner_radius=10, fg_color="#E0E0E0")
frame_login.pack(side="left", expand=True, fill="both",  padx=30, pady=30)

label1 = ctk.CTkLabel(frame_login, text="Login User1", font=("Arial", 24))
label1.pack(pady=50)

# ___________________

frame_login2 = ctk.CTkFrame(frame_centro, height=300, width=400, corner_radius=10, fg_color="#E0E0E0")
frame_login2.pack(expand=True, fill="both",  padx=30, pady=30)

label1 = ctk.CTkLabel(frame_login2, text="Login User2", font=("Arial", 24))
label1.pack(pady=50)


frame_login3 = ctk.CTkFrame(frame_centro, height=300, width=400, corner_radius=10, fg_color="#E0E0E0")
frame_login3.pack(expand=True, fill="both",  padx=30, pady=30)

label1 = ctk.CTkLabel(frame_login3, text="Login User3", font=("Arial", 24))
label1.pack(pady=50)



app.mainloop()