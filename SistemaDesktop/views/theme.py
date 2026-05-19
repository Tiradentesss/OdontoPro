import customtkinter as ctk
import json
import os

# Aparência padrão
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Modo escuro global
DARK_MODE = False

# Caminho do arquivo de configuração
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "theme_config.json")

# Paleta de cores - Modo Claro
COLORS_LIGHT = {
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
    "tab_inactive": "transparent",
    "row_bg": "#FFFFFF",
    "row_hover": "#F0F9FF",
    "divider": "#E5E7EB"
}

# Paleta de cores - Modo Escuro
COLORS_DARK = {
    "bg": "#0F172A",
    "content_bg": "#1E293B",
    "card": "#1E293B",
    "card_soft": "#334155",
    "primary": "#06B6D4",
    "primary_dark": "#0891B2",
    "primary_soft": "#164E63",
    "secondary": "#3B82F6",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
    "border": "#334155",
    "hover": "#334155",
    "selected_row": "#1E3A4C",
    "success": "#10B981",
    "success_light": "#065F46",
    "warning": "#F59E0B",
    "warning_light": "#78350F",
    "danger": "#EF4444",
    "danger_light": "#7F1D1D",
    "accent": "#06B6D4",
    "accent_hover": "#0891B2",
    "accent_light": "#164E63",
    "text_primary": "#F1F5F9",
    "text_secondary": "#CBD5E1",
    "text_muted": "#64748B",
    "bg_soft": "#1E293B",
    "bg_header": "#0F172A",
    "input_bg": "#334155",
    "tab_active": "#1E293B",
    "tab_inactive": "transparent",
    "row_bg": "#1E293B",
    "row_hover": "#334155",
    "divider": "#334155"
}

# Paleta ativa (começará com modo claro)
COLORS = COLORS_LIGHT.copy()

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

def toggle_dark_mode():
    """Alterna entre modo escuro e claro, e salva a preferência"""
    global DARK_MODE, COLORS
    DARK_MODE = not DARK_MODE
    
    # Atualizar a paleta COLORS com base no modo
    if DARK_MODE:
        COLORS.clear()
        COLORS.update(COLORS_DARK)
        ctk.set_appearance_mode("dark")
    else:
        COLORS.clear()
        COLORS.update(COLORS_LIGHT)
        ctk.set_appearance_mode("light")
    
    # Salvar preferência
    _save_theme_preference()
    return DARK_MODE

def _save_theme_preference():
    """Salva a preferência de tema em arquivo"""
    try:
        config = {"dark_mode": DARK_MODE}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Erro ao salvar preferência de tema: {e}")

def load_theme_preference():
    """Carrega a preferência de tema salva"""
    global DARK_MODE, COLORS
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                DARK_MODE = config.get("dark_mode", False)
        
        # Aplicar o tema carregado
        if DARK_MODE:
            COLORS.clear()
            COLORS.update(COLORS_DARK)
            ctk.set_appearance_mode("dark")
        else:
            COLORS.clear()
            COLORS.update(COLORS_LIGHT)
            ctk.set_appearance_mode("light")
    except Exception as e:
        print(f"Erro ao carregar preferência de tema: {e}")

def get_dark_mode():
    """Retorna o estado atual do modo escuro"""
    return DARK_MODE
