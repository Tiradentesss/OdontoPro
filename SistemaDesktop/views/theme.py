import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#F5F6FA",
    "card": "#FFFFFF",
    "primary": "#0d99c7",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB"
}

def font_title():
    return ctk.CTkFont(size=28, weight="bold")

def font_subtitle():
    return ctk.CTkFont(size=16, weight="bold")

def font_text():
    return ctk.CTkFont(size=13)
