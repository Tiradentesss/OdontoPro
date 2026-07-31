import os
import sys
root_dir = r'c:\Users\58143406\Documents\Desktop_2\OdontoPro'
sys.path.insert(0, os.path.join(root_dir, 'SistemaDesktop'))
import customtkinter as ctk
from SistemaDesktop.views.gerenciamento import Gerenciamento
from SistemaDesktop.views.painel import Painel

root = ctk.CTk()
root.withdraw()

def get_opt(widget, name):
    try:
        return widget.cget(name)
    except Exception:
        return None


def print_tree(widget, depth=0):
    indent = '  ' * depth
    info = {
        'name': widget.winfo_name(),
        'class': widget.__class__.__name__,
        'parent': widget.master.__class__.__name__ if widget.master else None,
        'fg_color': get_opt(widget, 'fg_color'),
        'bg_color': get_opt(widget, 'bg_color'),
        'border_width': get_opt(widget, 'border_width'),
        'border_color': get_opt(widget, 'border_color'),
        'corner_radius': get_opt(widget, 'corner_radius'),
        'width': widget.winfo_reqwidth(),
        'height': widget.winfo_reqheight(),
    }
    print(indent + str(info))
    for child in widget.winfo_children():
        print_tree(child, depth + 1)

print('--- Gerenciamento ---')
g = Gerenciamento(root, clinica_id=None)
print_tree(g)
print('--- Painel ---')
p = Painel(root, clinica_id=None, usuario_id=None, tipo_usuario=None)
print_tree(p)
