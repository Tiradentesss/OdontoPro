import os
import sys
import customtkinter as ctk
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_PATH = os.path.join(ROOT_DIR, 'SistemaDesktop')
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

from SistemaDesktop.views.permissao import Permissoes
from SistemaDesktop.views.cadastro import Cadastro
from SistemaDesktop.views.painel import Painel
from SistemaDesktop.views.gerenciamento import Gerenciamento
from SistemaDesktop.views.theme import INNER_CARD_BORDER, INNER_CARD_RADIUS


root = ctk.CTk()
root.geometry('1200x900')
root.update_idletasks()

print('Creating Permissoes...')
perm = Permissoes(root, clinica_id=7)
perm.pack(fill='both', expand=True)
root.update_idletasks()

print('Creating Cadastro...')
cad = Cadastro(root, clinica_id=7)
cad.pack_forget()
root.update_idletasks()

print('Creating Painel...')
pain = Painel(root)
pain.pack_forget()
root.update_idletasks()

print('Creating Gerenciamento...')
ger = Gerenciamento(root, clinica_id=7)
ger.pack_forget()
root.update_idletasks()


def safe_cget(widget, option):
    try:
        return widget.cget(option)
    except Exception:
        return None


def safe_geom_info(widget, manager):
    try:
        info = getattr(widget, f"{manager}_info")()
        return bool(info)
    except Exception:
        return False


def geom(widget):
    if safe_geom_info(widget, 'grid'):
        return 'grid'
    if safe_geom_info(widget, 'pack'):
        return 'pack'
    if safe_geom_info(widget, 'place'):
        return 'place'
    return 'none'


counter = 0

def widget_info(widget):
    parent_name = widget.winfo_parent()
    return {
        'class': widget.__class__.__name__,
        'path': widget._w,
        'parent': parent_name,
        'fg_color': safe_cget(widget, 'fg_color'),
        'bg_color': safe_cget(widget, 'bg_color'),
        'border_width': safe_cget(widget, 'border_width'),
        'border_color': safe_cget(widget, 'border_color'),
        'corner_radius': safe_cget(widget, 'corner_radius'),
        'geom': geom(widget),
        'x': widget.winfo_x(),
        'y': widget.winfo_y(),
        'width': widget.winfo_width(),
        'height': widget.winfo_height(),
    }


def walk(widget, depth=0):
    global counter
    counter += 1
    info = widget_info(widget)
    info['order'] = counter
    indent = '    ' * depth
    attrs = (
        f"class={info['class']}",
        f"parent={info['parent']}",
        f"fg_color={info['fg_color']}",
        f"bg_color={info['bg_color']}",
        f"border_width={info['border_width']}",
        f"border_color={info['border_color']}",
        f"corner_radius={info['corner_radius']}",
        f"geom={info['geom']}",
        f"order={info['order']}",
        f"x={info['x']}",
        f"y={info['y']}",
        f"w={info['width']}",
        f"h={info['height']}"
    )
    print(f"{indent}- {' | '.join(attrs)}")
    for child in widget.winfo_children():
        walk(child, depth + 1)


def print_tree(title, widget):
    print(f"\n{title}")
    print(f"{widget.__class__.__name__} ({widget._w})")
    walk(widget)

# Print trees for comparison
print_tree('PERMISSÕES content_card tree', perm.content_card)
print_tree('CADASTRO content_card tree', cad.content_card)
print_tree('CADASTRO container_outer tree', cad.container_outer)
print_tree('CADASTRO scroll_frame tree', cad.scroll_frame)
print_tree('PAINEL card tree', pain._criar_card('Teste','sub',0,0))
print_tree('GERENCIAMENTO main container (left/right) tree', ger)

# Analysis: find which direct child of content_card draws border and which children cover width

def analyze_content(widget):
    print(f"\nANALYZE: {widget._w}")
    for child in widget.winfo_children():
        info = widget_info(child)
        same_color = info['fg_color'] == safe_cget(widget, 'fg_color')
        covers_width = (info['x'] <= 1) and (info['width'] >= widget.winfo_width() - 2)
        print(f" child {info['class']} path={info['path']} fg={info['fg_color']} same_as_parent={same_color} covers_width={covers_width} geom={info['geom']} border_width={info['border_width']} corner_radius={info['corner_radius']}")

analyze_content(perm.content_card)
analyze_content(cad.content_card)

print('\nDone')
