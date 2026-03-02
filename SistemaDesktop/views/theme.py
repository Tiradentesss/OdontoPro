import customtkinter as ctk

# Aparência padrão
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Paleta de cores centralizada
COLORS = {
    "bg": "#F5F6FA",
    "card": "#FFFFFF",
    "primary": "#0d99c7",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB"
}

# Fonte e tamanhos padrão (centralizar aqui para padronizar todas as páginas)
FONT_FAMILY = "Poppins"

# Tamanhos padrão de texto
TEXT_SIZES = {
    "title": 24,
    "subtitle": 16,
    "text": 13,
    "small": 12,
    "button": 12
}

# Tamanho de ícone padrão (use onde for aplicável)
ICON_SIZE = 20

def font(size_key="text", weight="normal"):
    """Retorna um ctk.CTkFont padronizado.

    size_key pode ser uma chave de TEXT_SIZES (ex: 'title') ou um inteiro
    para valores personalizados.
    """
    if isinstance(size_key, int):
        size = size_key
    else:
        size = TEXT_SIZES.get(size_key, TEXT_SIZES["text"])
    return ctk.CTkFont(FONT_FAMILY, size=size, weight=weight)

def font_title():
    return font("title", weight="bold")

def font_subtitle():
    return font("subtitle", weight="bold")

def font_text():
    return font("text")
