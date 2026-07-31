import os
import sys
sys.path.insert(0, os.path.join(r'c:\Users\58143406\Documents\Desktop_2\OdontoPro', 'SistemaDesktop'))
import customtkinter as ctk
from SistemaDesktop.views.gerenciamento import Gerenciamento
from SistemaDesktop.views.painel import Painel


def measure_screen(cls, args):
    root = ctk.CTk()
    root.geometry('1200x900')
    root.update_idletasks()
    screen = cls(root, **args)
    screen.pack(fill='both', expand=True)
    root.update_idletasks()
    # find content_card: first CTkFrame in screen children with border_width 2 and fg_color '#FFFFFF'
    content_card = None
    for child in screen.winfo_children():
        if child.__class__.__name__ == 'CTkFrame':
            try:
                if child.cget('border_width') == 2:
                    content_card = child
                    break
            except Exception:
                pass
    if not content_card:
        raise RuntimeError('content_card not found')
    if not content_card.winfo_children():
        raise RuntimeError('content_card has no children')
    first_child = content_card.winfo_children()[0]

    def box(widget):
        return {
            'name': widget.winfo_name(),
            'class': widget.__class__.__name__,
            'width': widget.winfo_width(),
            'height': widget.winfo_height(),
            'x': widget.winfo_x(),
            'y': widget.winfo_y(),
        }

    cc = box(content_card)
    fc = box(first_child)
    spacing = {
        'top': fc['y'],
        'left': fc['x'],
        'right': cc['width'] - fc['x'] - fc['width'],
        'bottom': cc['height'] - fc['y'] - fc['height'],
    }

    # find any widget occupying full content_card area
    full_widgets = []
    def search(widget, path):
        w = box(widget)
        if w['x'] == 0 and w['y'] == 0 and w['width'] == cc['width'] and w['height'] == cc['height']:
            full_widgets.append({'path': path, **w})
        for child in widget.winfo_children():
            search(child, path + ' > ' + f"{child.winfo_name()}({child.__class__.__name__})")
    for child in content_card.winfo_children():
        search(child, 'content_card > ' + f"{child.winfo_name()}({child.__class__.__name__})")

    result = {
        'content_card': cc,
        'first_child': {'path': f'content_card > {first_child.winfo_name()}({first_child.__class__.__name__})', **fc},
        'spacing': spacing,
        'full_widgets': full_widgets,
    }
    root.destroy()
    return result

for name, cls, args in [
    ('Gerenciamento', Gerenciamento, {'clinica_id': None}),
    ('Painel', Painel, {'clinica_id': None, 'usuario_id': None, 'tipo_usuario': None}),
]:
    print('---', name, '---')
    try:
        res = measure_screen(cls, args)
        print(res)
    except Exception as e:
        print('ERROR:', e)
    print()
