import os, sys, time
import customtkinter as ctk
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_PATH = os.path.join(ROOT_DIR, 'SistemaDesktop')
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

from SistemaDesktop.views.cadastro import Cadastro
from SistemaDesktop.views.theme import INNER_CARD_BORDER, INNER_CARD_RADIUS, COLORS

root = ctk.CTk()
root.geometry('1200x900')
root.update_idletasks()

cad = Cadastro(root, clinica_id=7)
cad.pack(fill='both', expand=True)
root.update()

def layout_info(widget):
    manager = None
    options = {}
    for m in ('pack', 'grid', 'place'):
        try:
            info = getattr(widget, f'{m}_info')()
            if info:
                manager = m
                options = info
                break
        except Exception:
            pass
    return {
        'path': widget._w,
        'class': widget.__class__.__name__,
        'fg_color': widget.cget('fg_color') if 'fg_color' in widget.keys() else None,
        'border_width': widget.cget('border_width') if 'border_width' in widget.keys() else None,
        'border_color': widget.cget('border_color') if 'border_color' in widget.keys() else None,
        'corner_radius': widget.cget('corner_radius') if 'corner_radius' in widget.keys() else None,
        'x': widget.winfo_x(), 'y': widget.winfo_y(), 'w': widget.winfo_width(), 'h': widget.winfo_height(),
        'manager': manager,
        'options': options
    }

root.update_idletasks()
print('CONTENT_CARD')
print(layout_info(cad.content_card))

for i, child in enumerate(cad.content_card.winfo_children()):
    print(f'CHILD {i}:', layout_info(child))
    for j, sub in enumerate(child.winfo_children()):
        print(f'  SUB {j}:', layout_info(sub))

print('\nSCROLL_FRAME info:')
print(layout_info(cad.scroll_frame))

print('\nCONTAINER_OUTER info:')
print(layout_info(cad.container_outer))

# keep window open briefly so you can visually inspect if running interactively
root.after(2000, root.destroy)
root.mainloop()
