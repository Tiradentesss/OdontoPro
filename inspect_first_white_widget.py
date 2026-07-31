import os
import sys
sys.path.insert(0, os.path.join(r'c:\Users\58143406\Documents\Desktop_2\OdontoPro', 'SistemaDesktop'))
import customtkinter as ctk
from SistemaDesktop.views.gerenciamento import Gerenciamento
from SistemaDesktop.views.painel import Painel
from SistemaDesktop.views.theme import COLORS

root = ctk.CTk()
root.withdraw()

TARGET_COLORS = {'#FFFFFF', COLORS['card']}


def get_fg(widget):
    try:
        return widget.cget('fg_color')
    except Exception:
        return None


def widget_info(widget, path):
    return {
        'path': path,
        'widget_name': widget.winfo_name(),
        'class': widget.__class__.__name__,
        'parent': widget.master.__class__.__name__ if widget.master else None,
        'fg_color': get_fg(widget),
        'border_width': widget.cget('border_width') if hasattr(widget, 'cget') else None,
        'border_color': widget.cget('border_color') if hasattr(widget, 'cget') else None,
        'corner_radius': widget.cget('corner_radius') if hasattr(widget, 'cget') else None,
        'width': widget.winfo_reqwidth(),
        'height': widget.winfo_reqheight(),
    }


def find_first(widget, path):
    fg = get_fg(widget)
    if fg in TARGET_COLORS:
        return widget_info(widget, path)
    for child in widget.winfo_children():
        child_path = f"{path} > {child.winfo_name()}({child.__class__.__name__})"
        found = find_first(child, child_path)
        if found:
            return found
    return None

for name, cls, args in [
    ('Gerenciamento', Gerenciamento, {'clinica_id': None}),
    ('Painel', Painel, {'clinica_id': None, 'usuario_id': None, 'tipo_usuario': None}),
]:
    print(f'--- {name} ---')
    screen = cls(root, **args)
    result = find_first(screen, f'{name}({screen.__class__.__name__})')
    print(result)
    print()
