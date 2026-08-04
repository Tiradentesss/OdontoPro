import os, sys
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SISTEMA_DIR = os.path.join(PROJECT_ROOT, 'SistemaDesktop')
if SISTEMA_DIR not in sys.path:
    sys.path.insert(0, SISTEMA_DIR)
import customtkinter as ctk
from SistemaDesktop.views.cadastro import Cadastro
from SistemaDesktop.views.gerenciamento import Gerenciamento

ctk.set_appearance_mode('light')
root = ctk.CTk()
root.geometry('1200x800')

cad = Cadastro(root)
ger = Gerenciamento(root)

for name, view in [('Cadastro', cad), ('Gerenciamento', ger)]:
    view.pack(fill='both', expand=True)
    root.update()
    scroll_frames = []
    def find(w):
        for ch in w.winfo_children():
            if ch.__class__.__name__ == 'CTkScrollableFrame':
                scroll_frames.append(ch)
            find(ch)
    find(view)
    print('\n===', name, '===')
    for i, sf in enumerate(scroll_frames):
        print('scroll', i, 'obj', sf)
        print('  widget path:', sf._name)
        print('  master:', sf.master)
        print('  parent_frame:', getattr(sf, '_parent_frame', None))
        print('  parent_canvas:', getattr(sf, '_parent_canvas', None))
        print('  create_window_id:', getattr(sf, '_create_window_id', None))
        if getattr(sf, '_parent_canvas', None) is not None:
            try:
                print('  bbox', sf._parent_canvas.bbox(sf._create_window_id))
            except Exception as e:
                print('  bbox err', e)
        for attr in ('fg_color', 'corner_radius', 'border_width', 'border_color', 'width', 'height'):
            try:
                print('   ', attr, ':', sf.cget(attr))
            except Exception:
                pass
        try:
            print('  pack_info:', sf.pack_info())
        except Exception as e:
            print('  pack_info err', e)
        try:
            print('  grid_info:', sf.grid_info())
        except Exception as e:
            print('  grid_info err', e)
        print('  actual size: w', sf.winfo_width(), 'h', sf.winfo_height())
        if getattr(sf, '_parent_frame', None):
            p = sf._parent_frame
            print('  parent_frame size req/actual', p.winfo_reqwidth(), p.winfo_reqheight(), p.winfo_width(), p.winfo_height())
            try:
                print('   parent_frame pack_info:', p.pack_info())
            except Exception as e:
                print('   parent_frame pack_info err', e)
        if getattr(sf, '_parent_canvas', None):
            c = sf._parent_canvas
            print('  parent_canvas size req/actual', c.winfo_reqwidth(), c.winfo_reqheight(), c.winfo_width(), c.winfo_height())
            try:
                print('   parent_canvas pack_info:', c.pack_info())
            except Exception as e:
                print('   parent_canvas pack_info err', e)
        chain = []
        w2 = sf
        while w2 is not None:
            try:
                name = w2.winfo_name()
            except Exception:
                name = str(w2)
            chain.append(f'{w2.__class__.__name__}({name})')
            if hasattr(w2, 'master') and w2.master is not None and w2.master != w2:
                w2 = w2.master
            else:
                break
        print('  chain:', ' <- '.join(chain))
    view.pack_forget()
    root.update()
root.destroy()
print('\nAll done')
