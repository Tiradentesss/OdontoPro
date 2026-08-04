import customtkinter as ctk
import sys
import inspect
import os

# ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SISTEMA_DIR = os.path.join(PROJECT_ROOT, 'SistemaDesktop')
if SISTEMA_DIR not in sys.path:
    sys.path.insert(0, SISTEMA_DIR)

from SistemaDesktop.views.cadastro import Cadastro

ctk.set_appearance_mode('light')
root = ctk.CTk()
root.geometry('1200x800')

cad = Cadastro(root)
# pack the Cadastro screen into root
cad.pack(fill='both', expand=True)
root.update()

out = []

def widget_info(w):
    cls = w.__class__.__name__
    parent = w.master.__class__.__name__ if hasattr(w, 'master') and w.master else None
    try:
        pack = w.pack_info()
    except Exception:
        pack = None
    try:
        grid = w.grid_info()
    except Exception:
        grid = None
    try:
        place = w.place_info()
    except Exception:
        place = None
    try:
        w_width = w.winfo_width()
        w_height = w.winfo_height()
        x = w.winfo_rootx()
        y = w.winfo_rooty()
    except Exception:
        w_width = w_height = x = y = None
    # cget useful props
    props = {}
    for key in ('fg_color','bg','border_width','border_color','corner_radius','width','height'):
        try:
            val = w.cget(key)
            props[key] = val
        except Exception:
            pass
    # try to get configure dict
    try:
        cfg = w.configure()
    except Exception:
        cfg = None
    info = dict(name=str(w), cls=cls, parent=parent, pack=pack, grid=grid, place=place,
                width=w_width, height=w_height, x=x, y=y, props=props)
    return info


def recurse(w, depth=0, results=None):
    if results is None:
        results = []
    info = widget_info(w)
    info['depth'] = depth
    results.append(info)
    for child in w.winfo_children():
        recurse(child, depth+1, results)
    return results

results = recurse(cad)

# find content_card if present
content_card = getattr(cad, 'content_card', None)
def print_widget_details(w, label=None):
    if not w:
        print(f"{label} - NOT FOUND")
        return
    print(f"--- {label or w.__class__.__name__} ---")
    info = widget_info(w)
    print(f"class: {info['cls']}")
    print(f"parent: {info['parent']}")
    print(f"pack: {info['pack']}")
    print(f"grid: {info['grid']}")
    print(f"place: {info['place']}")
    print(f"rendered size: {info['width']}x{info['height']} at {info['x']},{info['y']}")
    for k,v in info['props'].items():
        print(f"{k}: {v}")
    print()

print_widget_details(content_card, 'content_card (BaseScreen)')

# find cadastro_card
cadastro_card = getattr(cad, 'cadastro_card', None)
print_widget_details(cadastro_card, 'cadastro_card')

scroll_frame = getattr(cad, 'scroll_frame', None)
print_widget_details(scroll_frame, 'scroll_frame (CTkScrollableFrame)')

container_conteudo = getattr(cad, 'container_conteudo', None)
print_widget_details(container_conteudo, 'container_conteudo')

# Inspect internal canvas of CTkScrollableFrame
if scroll_frame:
    print('CTkScrollableFrame attributes:')
    for attr in dir(scroll_frame):
        if 'canvas' in attr.lower() or 'window' in attr.lower():
            try:
                val = getattr(scroll_frame, attr)
                print(f"  {attr} -> {type(val)}")
            except Exception:
                print(f"  {attr} -> <error accessing>")
    # search for tkinter.Canvas children inside
    import tkinter
    canv = [w for w in scroll_frame.winfo_children() if isinstance(w, tkinter.Canvas)]
    print('tkinter.Canvas children count in scroll_frame:', len(canv))
    for c in canv:
        print('  Canvas', c, 'size', c.winfo_width(), c.winfo_height(), 'pos', c.winfo_rootx(), c.winfo_rooty())

    # also locate the canvas objects anywhere under cad
    all_canvases = []
    def find_canv(w):
        for ch in w.winfo_children():
            if isinstance(ch, tkinter.Canvas):
                all_canvases.append(ch)
            find_canv(ch)
    find_canv(cad)
    print('\nAll Canvas instances under Cadastro:')
    for c in all_canvases:
        px = c.winfo_rootx(); py = c.winfo_rooty(); pw = c.winfo_width(); ph = c.winfo_height()
        print(' Canvas', c, 'pos', px,py, 'size', pw,ph, 'parent', c.master)
        # check overlap with cadastro_card
        if cadastro_card:
            cx = cadastro_card.winfo_rootx(); cy = cadastro_card.winfo_rooty(); cw = cadastro_card.winfo_width(); ch = cadastro_card.winfo_height()
            overlap_x = max(0, min(px+pw, cx+cw) - max(px, cx))
            overlap_y = max(0, min(py+ph, cy+ch) - max(py, cy))
            print('   overlaps cadastro_card by', overlap_x, 'x', overlap_y)
            # check if canvas extends outside cadastro_card bounds (i.e., covers border area)
            left_out = max(0, cx - px)
            right_out = max(0, (px+pw) - (cx+cw))
            top_out = max(0, cy - py)
            bottom_out = max(0, (py+ph) - (cy+ch))
            if any((left_out, right_out, top_out, bottom_out)):
                print('   extends outside cadastro_card by left,right,top,bottom:', left_out, right_out, top_out, bottom_out)

print('\nDone\n')

# Additionally, search for any tkinter.Canvas instances under cadastro
import tkinter
canvases = []
for w in cad.winfo_children():
    for child in w.winfo_children():
        for desc in child.winfo_children():
            if isinstance(desc, tkinter.Canvas):
                canvases.append(desc)
# Also recursively
for w in cad.winfo_children():
    for ch in w.winfo_children():
        for d in ch.winfo_children():
            for sub in d.winfo_children():
                if isinstance(sub, tkinter.Canvas):
                    canvases.append(sub)

print('--- Found Canvas instances:')
for c in canvases:
    print('Canvas', c, 'size', c.winfo_width(), c.winfo_height(), 'pos', c.winfo_rootx(), c.winfo_rooty())

# Inspect CTkScrollableFrame attributes
from customtkinter import CTkScrollableFrame
scroll_frames = [w for w in results if w['cls'] == 'CTkScrollableFrame']
print('--- CTkScrollableFrame summary:')
for sf in scroll_frames:
    print(sf)

# Attempt to locate scroll_frame object
sf_obj = None
for obj in cad.winfo_children():
    if obj.__class__.__name__ == 'CTkFrame':
        # dive
        for c in obj.winfo_children():
            if c.__class__.__name__ == 'CTkScrollableFrame':
                sf_obj = c
                break

if sf_obj:
    print('Found scroll_frame object:', sf_obj)
    # inspect attributes
    for attr in dir(sf_obj):
        if attr.startswith('__'):
            continue
        if 'canvas' in attr.lower() or 'frame' in attr.lower():
            try:
                val = getattr(sf_obj, attr)
                print('  ', attr, '->', type(val), val)
            except Exception:
                pass

print('\nDone')

# exit
root.destroy()
# Now run same checks for Permissoes view for comparison
from SistemaDesktop.views.permissao import Permissoes
root = ctk.CTk()
root.geometry('1200x800')
perms = Permissoes(root)
perms.pack(fill='both', expand=True)
root.update()

print('\n=== Permissoes diagnostics ===\n')
pc = getattr(perms, 'content_card', None)
print_widget_details(pc, 'perms content_card')
admin_list = getattr(perms, 'admin_list_panel', None)
print_widget_details(admin_list, 'admin_list_panel')
right_card = getattr(perms, 'right_card', None)
print_widget_details(right_card, 'right_card')

import tkinter
canvs = []
def find_canv_w(w):
    for ch in w.winfo_children():
        if isinstance(ch, tkinter.Canvas):
            canvs.append(ch)
        find_canv_w(ch)
find_canv_w(perms)
print('Permissoes - Canvas count:', len(canvs))
for c in canvs:
    px=c.winfo_rootx(); py=c.winfo_rooty(); pw=c.winfo_width(); ph=c.winfo_height()
    print(' Canvas', c, 'pos', px,py, 'size', pw,ph, 'parent', c.master)
    if pc:
        cx = pc.winfo_rootx(); cy = pc.winfo_rooty(); cw = pc.winfo_width(); ch = pc.winfo_height()
        left_out = max(0, cx - px)
        right_out = max(0, (px+pw) - (cx+cw))
        top_out = max(0, cy - py)
        bottom_out = max(0, (py+ph) - (cy+ch))
        if any((left_out,right_out,top_out,bottom_out)):
            print('  extends outside content_card by', left_out,right_out,top_out,bottom_out)
print('\nPermissoes diag done')
root.destroy()
