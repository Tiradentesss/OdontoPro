import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'SistemaDesktop'))
import customtkinter as ctk
from views.cadastro import Cadastro

root = ctk.CTk()
root.geometry('1200x900')
root.title('Debug Cadastro')

cadastro = Cadastro(root)
cadastro.pack(expand=True, fill='both')
root.update_idletasks()
root.update()

inspect_names = [
    'content_card',
    'cadastro_card',
    'scroll_frame',
]

widgets = []
for name in inspect_names:
    obj = getattr(cadastro, name, None)
    if obj is None:
        print(f'{name}: MISSING')
        continue
    widgets.append((name, obj))
    print(f'=== {name} ===')
    print('class:', obj.__class__.__name__)
    print('widget_path:', obj.winfo_pathname(obj.winfo_id()))
    print('master:', obj.master.__class__.__name__, obj.master)
    print('width:', obj.winfo_width())
    print('height:', obj.winfo_height())
    print('x:', obj.winfo_x())
    print('y:', obj.winfo_y())
    print('winfo_manager:', obj.winfo_manager())
    if obj.winfo_manager() == 'pack':
        print('pack_info:', obj.pack_info())
    elif obj.winfo_manager() == 'grid':
        print('grid_info:', obj.grid_info())
    print()
    print('direct children:')
    for child in obj.winfo_children():
        chname = getattr(child, 'name', None) or child.winfo_name()
        print('  ---')
        print('  variable:', chname)
        print('  class:', child.__class__.__name__)
        print('  widget_path:', child.winfo_pathname(child.winfo_id()))
        print('  master:', child.master.__class__.__name__, child.master)
        print('  width:', child.winfo_width())
        print('  height:', child.winfo_height())
        print('  x:', child.winfo_x())
        print('  y:', child.winfo_y())
        print('  winfo_manager:', child.winfo_manager())
        if child.winfo_manager() == 'pack':
            print('  pack_info:', child.pack_info())
        elif child.winfo_manager() == 'grid':
            print('  grid_info:', child.grid_info())
        print()

# inspect scroll_frame internals if available
sf = cadastro.scroll_frame
if hasattr(sf, '_parent_frame'):
    pf = sf._parent_frame
    print('=== scroll_frame._parent_frame ===')
    print('class:', pf.__class__.__name__)
    print('widget_path:', pf.winfo_pathname(pf.winfo_id()))
    print('master:', pf.master.__class__.__name__, pf.master)
    print('width:', pf.winfo_width())
    print('height:', pf.winfo_height())
    print('x:', pf.winfo_x())
    print('y:', pf.winfo_y())
    print('winfo_manager:', pf.winfo_manager())
    if pf.winfo_manager() == 'pack':
        print('pack_info:', pf.pack_info())
    elif pf.winfo_manager() == 'grid':
        print('grid_info:', pf.grid_info())
    print('direct children:')
    for child in pf.winfo_children():
        chname = getattr(child, 'name', None) or child.winfo_name()
        print('  ---')
        print('  variable:', chname)
        print('  class:', child.__class__.__name__)
        print('  widget_path:', child.winfo_pathname(child.winfo_id()))
        print('  master:', child.master.__class__.__name__, child.master)
        print('  width:', child.winfo_width())
        print('  height:', child.winfo_height())
        print('  x:', child.winfo_x())
        print('  y:', child.winfo_y())
        print('  winfo_manager:', child.winfo_manager())
        if child.winfo_manager() == 'pack':
            print('  pack_info:', child.pack_info())
        elif child.winfo_manager() == 'grid':
            print('  grid_info:', child.grid_info())
        print()

if hasattr(sf, '_parent_canvas'):
    pc = sf._parent_canvas
    print('=== scroll_frame._parent_canvas ===')
    print('class:', pc.__class__.__name__)
    print('widget_path:', pc.winfo_pathname(pc.winfo_id()))
    print('master:', pc.master.__class__.__name__, pc.master)
    print('width:', pc.winfo_width())
    print('height:', pc.winfo_height())
    print('x:', pc.winfo_x())
    print('y:', pc.winfo_y())
    print('winfo_manager:', pc.winfo_manager())
    if pc.winfo_manager() == 'pack':
        print('pack_info:', pc.pack_info())
    elif pc.winfo_manager() == 'grid':
        print('grid_info:', pc.grid_info())
    print('direct children:')
    for child in pc.winfo_children():
        chname = getattr(child, 'name', None) or child.winfo_name()
        print('  ---')
        print('  variable:', chname)
        print('  class:', child.__class__.__name__)
        print('  widget_path:', child.winfo_pathname(child.winfo_id()))
        print('  master:', child.master.__class__.__name__, child.master)
        print('  width:', child.winfo_width())
        print('  height:', child.winfo_height())
        print('  x:', child.winfo_x())
        print('  y:', child.winfo_y())
        print('  winfo_manager:', child.winfo_manager())
        if child.winfo_manager() == 'pack':
            print('  pack_info:', child.pack_info())
        elif child.winfo_manager() == 'grid':
            print('  grid_info:', child.grid_info())
        print()

if hasattr(sf, '_scrollbar'):
    sb = sf._scrollbar
    print('=== scroll_frame._scrollbar ===')
    print('class:', sb.__class__.__name__)
    print('widget_path:', sb.winfo_pathname(sb.winfo_id()))
    print('master:', sb.master.__class__.__name__, sb.master)
    print('width:', sb.winfo_width())
    print('height:', sb.winfo_height())
    print('x:', sb.winfo_x())
    print('y:', sb.winfo_y())
    print('winfo_manager:', sb.winfo_manager())
    if sb.winfo_manager() == 'pack':
        print('pack_info:', sb.pack_info())
    elif sb.winfo_manager() == 'grid':
        print('grid_info:', sb.grid_info())
    print('direct children:')
    for child in sb.winfo_children():
        chname = getattr(child, 'name', None) or child.winfo_name()
        print('  ---')
        print('  variable:', chname)
        print('  class:', child.__class__.__name__)
        print('  widget_path:', child.winfo_pathname(child.winfo_id()))
        print('  master:', child.master.__class__.__name__, child.master)
        print('  width:', child.winfo_width())
        print('  height:', child.winfo_height())
        print('  x:', child.winfo_x())
        print('  y:', child.winfo_y())
        print('  winfo_manager:', child.winfo_manager())
        if child.winfo_manager() == 'pack':
            print('  pack_info:', child.pack_info())
        elif child.winfo_manager() == 'grid':
            print('  grid_info:', child.grid_info())
        print()

print('=== direct children of cadastro_card ===')
for child in cadastro.cadastro_card.winfo_children():
    chname = getattr(child, 'name', None) or child.winfo_name()
    print('  ---')
    print('  variable:', chname)
    print('  class:', child.__class__.__name__)
    print('  widget_path:', child.winfo_pathname(child.winfo_id()))
    print('  master:', child.master.__class__.__name__, child.master)
    print('  width:', child.winfo_width())
    print('  height:', child.winfo_height())
    print('  x:', child.winfo_x())
    print('  y:', child.winfo_y())
    print('  winfo_manager:', child.winfo_manager())
    if child.winfo_manager() == 'pack':
        print('  pack_info:', child.pack_info())
    elif child.winfo_manager() == 'grid':
        print('  grid_info:', child.grid_info())
    print()

print('=== direct children of container_conteudo ===')
for child in cadastro.container_conteudo.winfo_children():
    chname = getattr(child, 'name', None) or child.winfo_name()
    print('  ---')
    print('  variable:', chname)
    print('  class:', child.__class__.__name__)
    print('  widget_path:', child.winfo_pathname(child.winfo_id()))
    print('  master:', child.master.__class__.__name__, child.master)
    print('  width:', child.winfo_width())
    print('  height:', child.winfo_height())
    print('  x:', child.winfo_x())
    print('  y:', child.winfo_y())
    print('  winfo_manager:', child.winfo_manager())
    if child.winfo_manager() == 'pack':
        print('  pack_info:', child.pack_info())
    elif child.winfo_manager() == 'grid':
        print('  grid_info:', child.grid_info())
    print()

root.destroy()
