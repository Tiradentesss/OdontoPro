import os
import sys
import customtkinter as ctk

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SISTEMA_DIR = os.path.join(PROJECT_ROOT, 'SistemaDesktop')
if SISTEMA_DIR not in sys.path:
    sys.path.insert(0, SISTEMA_DIR)

from SistemaDesktop.views.configuracoes import Configuracoes

root = ctk.CTk()
root.geometry('1200x900')
view = Configuracoes(root)
view.pack(fill='both', expand=True)
root.update()

container = getattr(view, 'clinic_photos_container', None)
print('clinic_photos_container', container, 'exists', container is not None)

def info(widget):
    data = {
        'class': widget.__class__.__name__,
        'name': widget.winfo_name(),
        'fg_color': None,
        'border_width': None,
        'border_color': None,
        'corner_radius': None,
        'pack_info': None,
        'grid_info': None,
        'pack_propagate': None,
        'grid_propagate': None,
        'width': widget.winfo_width(),
        'height': widget.winfo_height(),
        'rootx': widget.winfo_rootx(),
        'rooty': widget.winfo_rooty(),
    }
    for prop in ('fg_color', 'border_width', 'border_color', 'corner_radius'):
        try:
            data[prop] = widget.cget(prop)
        except Exception:
            data[prop] = None
    try:
        data['pack_info'] = widget.pack_info()
    except Exception:
        data['pack_info'] = None
    try:
        data['grid_info'] = widget.grid_info()
    except Exception:
        data['grid_info'] = None
    try:
        data['pack_propagate'] = widget.pack_propagate()
    except Exception:
        data['pack_propagate'] = None
    try:
        data['grid_propagate'] = widget.grid_propagate()
    except Exception:
        data['grid_propagate'] = None
    return data


def dump(widget, depth=0):
    inf = info(widget)
    indent = '  ' * depth
    print(indent + str(inf))
    for child in widget.winfo_children():
        dump(child, depth + 1)

if container:
    dump(container)
    cur = container
    while cur is not None:
        man = cur.winfo_manager()
        print('PARENT', cur.__class__.__name__, cur.winfo_name(), 'manager=' + man,
              'pack=' + repr(cur.pack_info() if man == 'pack' else None),
              'grid=' + repr(cur.grid_info() if man == 'grid' else None))
        cur = cur.master
root.destroy()
