import customtkinter as ctk

# Tema geral
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

COLORS = {
    "bg": "#F5F7FA",
    "card": "#FFFFFF",
    "primary": "#16A34A",
    "text": "#111827",
    "muted": "#6B7280",
}

FONTS = {
    "title": ctk.CTkFont(size=28, weight="bold"),
    "subtitle": ctk.CTkFont(size=18, weight="bold"),
    "text": ctk.CTkFont(size=14),
}
