import customtkinter as ctk

# Aparência padrão
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Paleta de cores centralizada
COLORS = {
    "bg": "#F3F6FB",
    "content_bg": "#F8FAFC",
    "card": "#FFFFFF",
    "card_soft": "#EDF5FF",
    "primary": "#0D99C7",
    "primary_dark": "#0B86AF",
    "primary_soft": "#E8F6FF",
    "secondary": "#2563EB",
    "text": "#0F172A",
    "muted": "#64748B",
    "border": "#E5E7EB",
    "hover": "#F0F9FF",
    "selected_row": "#EAF6FF",
    "success": "#22C55E",
    "success_light": "#D1FAE5",
    "warning": "#F59E0B",
    "warning_light": "#FEF3C7",
    "danger": "#EF4444",
    "danger_light": "#FEE2E2",
    "accent": "#0D99C7",
    "accent_hover": "#0B86AF",
    "accent_light": "#E8F6FF",
    "text_primary": "#0F172A",
    "text_secondary": "#64748B",
    "text_muted": "#94A3B8",
    "bg_soft": "#F8FBFF",
    "bg_header": "#F4F8FD",
    "input_bg": "#F9FAFB",
    "tab_active": "#FFFFFF",
    "tab_inactive": "transparent"
}

# Fonte e tamanhos padrão (centralizar aqui para padronizar todas as páginas)
FONT_FAMILY = "Poppins"

# Tamanhos padrão de texto
TEXT_SIZES = {
    "title": 24,
    "subtitle": 16,
    "text": 13,
    "small": 12,
    "button": 12,
    "button_large": 15,
    "card_title": 18,
    "large_title": 28,
    "tiny": 10,
    "text_large": 14
}

# Tamanho de ícone padrão (use onde for aplicável)
ICON_SIZE = 20

# Paddings padrão
PADDINGS = {
    "content": (25, 25),  # padx, pady para content areas
    "section": (60, (16, 8)),  # padx, pady para seções
    "card": (20, 20)  # padx, pady para cards internos
}

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
