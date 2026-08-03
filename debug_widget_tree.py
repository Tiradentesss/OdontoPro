import sys
import os
import customtkinter as ctk

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_PATH = os.path.join(ROOT_DIR, 'SistemaDesktop')
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

from SistemaDesktop.views.permissao import Permissoes
from SistemaDesktop.views.painel import Painel

root = ctk.CTk()
root.geometry('1200x900')
root.update_idletasks()

perm = Permissoes(root, clinica_id=7)
perm.pack(fill='both', expand=True)
root.update_idletasks()

painel = Painel(root)
painel.pack_forget()
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


counter = 0


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

print_tree('PERMISSÕES content_card tree', perm.content_card)
print_tree('PERMISSÕES admin_list_panel tree', perm.admin_list_panel)
print_tree('PERMISSÕES right_card tree', perm.right_card)

card = painel._criar_card('Teste', 'sub', row=0, col=0, padx=(0,0))
root.update_idletasks()
print_tree('PAINEL card tree', card)


# Analysis helpers
print('\nANALYSIS:')
for desc, widget in [
    ('Permissões content_card', perm.content_card),
    ('Permissões admin_list_panel', perm.admin_list_panel),
    ('Permissões right_card', perm.right_card),
    ('Painel card', card)
]:
    children = widget.winfo_children()
    print(f"\n{desc}: {len(children)} direct children")
    for child in children:
        info = widget_info(child)
        same_color = info['fg_color'] == safe_cget(widget, 'fg_color')
        covers_width = info['x'] <= 1 and info['width'] >= widget.winfo_width() - 2
        print(f"  child {child.__class__.__name__} path={child._w} fg={info['fg_color']} same_as_parent={same_color} covers_width={covers_width} geom={info['geom']} padx? n/a")
