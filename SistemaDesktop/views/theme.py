import customtkinter as ctk
import json
import os

# Pasta de ativos compartilhados
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")

LOGO_CANDIDATES = {
    "light": ["OdontoHub.png", "logo.png"],
    "dark": ["OdontoHub_dark.png", "logo.png"]
}

# Aparência padrão
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Modo escuro global
DARK_MODE = False

# Caminho do arquivo de configuração
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "theme_config.json")

# Paleta de cores - Modo Claro (Melhorado)
COLORS_LIGHT = {
    "bg": "#FAFBFC",
    "content_bg": "#FFFFFF",
    "card": "#FFFFFF",
    "card_soft": "#F8FAFC",
    "primary": "#0891B2",
    "primary_dark": "#0679A7",
    "primary_soft": "#E0F2FE",
    "secondary": "#3B82F6",
    "text": "#1F2937",
    "muted": "#6B7280",
    "border": "#E5E7EB",
    "hover": "#F3F4F6",
    "selected_row": "#DBEAFE",
    "success": "#10B981",
    "success_light": "#D1FAE5",
    "warning": "#F59E0B",
    "warning_light": "#FEF3C7",
    "danger": "#EF4444",
    "danger_light": "#FEE2E2",
    "accent": "#0891B2",
    "accent_hover": "#0679A7",
    "accent_light": "#E0F2FE",
    "text_primary": "#1F2937",
    "text_secondary": "#6B7280",
    "text_muted": "#9CA3AF",
    "bg_soft": "#F9FAFB",
    "bg_header": "#F3F4F6",
    "input_bg": "#F3F4F6",
    "tab_active": "#FFFFFF",
    "tab_inactive": "transparent",
    "row_bg": "#FFFFFF",
    "row_hover": "#F9FAFB",
    "divider": "#D1D5DB"
}

# Paleta de cores - Modo Escuro
COLORS_DARK = {
    # Fundos
    "bg": "#0D1117",
    "content_bg": "#161B22",
    "card": "#161B22",
    "card_soft": "#21262D",
    "bg_soft": "#161B22",
    "bg_header": "#111827",
    "input_bg": "#21262D",
    "sidebar_bg": "#111827",
    
    # Destaques - Cyan
    "primary": "#06B6D4",
    "primary_dark": "#0891B2",
    "primary_soft": "#164E63",
    "secondary": "#3B82F6",
    
    # Textos
    "text": "#F8FAFC",
    "text_primary": "#F8FAFC",
    "text_secondary": "#CBD5E1",
    "text_muted": "#94A3B8",
    "muted": "#94A3B8",
    
    # Acentos
    "accent": "#06B6D4",
    "accent_hover": "#0891B2",
    "accent_light": "#164E63",
    
    # Estados e Bordas
    "border": "#30363D",
    "hover": "#262C36",
    "selected_row": "#083344",
    "divider": "#30363D",
    
    # Abas/Tabs
    "tab_active": "#161B22",
    "tab_inactive": "transparent",
    
    # Linhas/Rows
    "row_bg": "#161B22",
    "row_hover": "#262C36",
    
    # Status
    "success": "#10B981",
    "success_light": "#083B2A",
    "warning": "#F59E0B",
    "warning_light": "#78350F",
    "danger": "#EF4444",
    "danger_light": "#7F1D1D",
    
    # Efeitos
    "focus": "#0E7490"
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


def get_brand_logo_path():
    """Retorna o caminho do logo da marca apropriado ao tema atual."""
    mode = "dark" if DARK_MODE else "light"

    for filename in LOGO_CANDIDATES[mode]:
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            return path

    for filenames in LOGO_CANDIDATES.values():
        for filename in filenames:
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                return path

    return None
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
