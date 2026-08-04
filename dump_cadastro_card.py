import os, sys
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SISTEMA_DIR = os.path.join(PROJECT_ROOT, 'SistemaDesktop')
if SISTEMA_DIR not in sys.path:
    sys.path.insert(0, SISTEMA_DIR)
import customtkinter as ctk
from SistemaDesktop.views.cadastro import Cadastro

ctk.set_appearance_mode('light')
root = ctk.CTk()
root.geometry('1200x800')
view = Cadastro(root)
view.pack(fill='both', expand=True)
root.update()

cadastro_card = getattr(view, 'cadastro_card', None)
if cadastro_card is None:
    raise RuntimeError('cadastro_card not found')

card_x = cadastro_card.winfo_rootx()
card_y = cadastro_card.winfo_rooty()
card_w = cadastro_card.winfo_width()
card_h = cadastro_card.winfo_height()
print('cadastro_card', cadastro_card, 'root_coords', card_x, card_y, 'size', card_w, card_h)
print('border width', cadastro_card.cget('border_width'), 'border_color', cadastro_card.cget('border_color'))


def rel_coords(widget):
    x = widget.winfo_rootx() - card_x
    y = widget.winfo_rooty() - card_y
    w = widget.winfo_width()
    h = widget.winfo_height()
    return x, y, w, h


def bg_info(widget):
    info = {}
    for attr in ('fg_color', 'bg', 'bg_color', 'border_color', 'border_width'):
        try:
            info[attr] = widget.cget(attr)
        except Exception:
            pass
    return info


def overlaps_border(x, y, w, h, card_w, card_h):
    return {
        'left': x <= 0,
        'right': x + w >= card_w,
        'top': y <= 0,
        'bottom': y + h >= card_h,
    }


def dump_tree(widget, depth=0):
    prefix = '  ' * depth
    x, y, w, h = rel_coords(widget)
    overlap = overlaps_border(x, y, w, h, card_w, card_h)
    bg = bg_info(widget)
    print(f"{prefix}{widget.__class__.__name__} {widget.winfo_name()} x={x} y={y} w={w} h={h} overlap={overlap} bg={bg}")
    children = widget.winfo_children()
    print(f"{prefix} children count={len(children)}")
    for i, child in enumerate(children):
        print(f"{prefix}  child[{i}] stacking-order index={i}")
        dump_tree(child, depth + 2)

print('--- hierarchy dump ---')
dump_tree(cadastro_card)

# identify direct widgets overlapping border
print('--- direct children overlapping border ---')
for i, child in enumerate(cadastro_card.winfo_children()):
    x, y, w, h = rel_coords(child)
    overlap = overlaps_border(x, y, w, h, card_w, card_h)
    print(i, child.__class__.__name__, child.winfo_name(), 'rel', x, y, w, h, overlap, bg_info(child))

import tkinter

# locate Canvas descendants overlapping border
print('--- canvas descendants overlapping border ---')
for child in cadastro_card.winfo_children():
    for desc in child.winfo_children():
        if isinstance(desc, tkinter.Canvas) or desc.__class__.__name__ == 'CTkCanvas':
            x, y, w, h = rel_coords(desc)
            overlap = overlaps_border(x, y, w, h, card_w, card_h)
            print('Canvas', desc.__class__.__name__, desc.winfo_name(), 'rel', x, y, w, h, overlap, 'parent', desc.master)

root.destroy()
print('done')
