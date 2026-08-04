import os, sys
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SISTEMA_DIR = os.path.join(PROJECT_ROOT, 'SistemaDesktop')
if SISTEMA_DIR not in sys.path:
    sys.path.insert(0, SISTEMA_DIR)

import customtkinter as ctk
import tkinter
from SistemaDesktop.views.cadastro import Cadastro
from SistemaDesktop.views.permissao import Permissoes
from SistemaDesktop.views.agenda import Agenda
from SistemaDesktop.views.gerenciamento import Gerenciamento

ctk.set_appearance_mode('light')
root = ctk.CTk()
root.geometry('1200x800')

views = [
    ('Cadastro', Cadastro(root)),
    ('Permissoes', Permissoes(root)),
    ('Agenda', Agenda(root)),
    ('Gerenciamento', Gerenciamento(root))
]

# helper
def widget_info(w):
    cls = w.__class__.__name__
    parent = w.master
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
    props = {}
    for key in ('fg_color','bg','border_width','border_color','corner_radius','width','height'):
        try:
            props[key] = w.cget(key)
        except Exception:
            pass
    return dict(name=str(w), obj=w, cls=cls, parent=parent, pack=pack, grid=grid, place=place, width=w_width, height=w_height, x=x, y=y, props=props)

root.update()

for name, view in views:
    print('\n=== VIEW:', name, '===')
    view.pack(fill='both', expand=True)
    root.update()
    # is instance of BaseScreen?
    is_base = view.__class__.__mro__
    print('Class MRO:', [c.__name__ for c in view.__class__.__mro__[:4]])
    content_card = getattr(view, 'content_card', None)
    print('has content_card?', bool(content_card))
    if content_card:
        info = widget_info(content_card)
        print(' content_card size:', info['width'], info['height'], 'props:', info['props'])
    # inner card (if present)
    inner_card = getattr(view, 'cadastro_card', None) or getattr(view, 'admin_list_panel', None) or getattr(view, 'right_card', None) or getattr(view, 'panel', None)
    print('named inner_card attribute found?', bool(inner_card), 'attribute object:', inner_card)
    # find any CTkScrollableFrame under the view
    scroll_frames = []
    def find_scrolls(w):
        for ch in w.winfo_children():
            if ch.__class__.__name__ == 'CTkScrollableFrame':
                scroll_frames.append(ch)
            find_scrolls(ch)
    find_scrolls(view)
    print('CTkScrollableFrame count in view:', len(scroll_frames))
    for i, sf in enumerate(scroll_frames):
        print('\n scroll_frame', i, 'obj:', sf)
        # find parent_frame and parent_canvas attributes if present
        parent_frame = getattr(sf, '_parent_frame', None)
        parent_canvas = getattr(sf, '_parent_canvas', None)
        create_id = getattr(sf, '_create_window_id', None)
        print('  master (w.master)=', sf.master)
        print('  parent_frame=', parent_frame)
        if parent_frame:
            print('   parent_frame size req/actual:', parent_frame.winfo_reqwidth(), parent_frame.winfo_reqheight(), parent_frame.winfo_width(), parent_frame.winfo_height())
            try:
                print('   parent_frame.pack_info:', parent_frame.pack_info())
            except:
                pass
        if parent_canvas:
            print('   parent_canvas size req/actual:', parent_canvas.winfo_reqwidth(), parent_canvas.winfo_reqheight(), parent_canvas.winfo_width(), parent_canvas.winfo_height())
            try:
                bbox = parent_canvas.bbox(create_id)
                print('   canvas.bbox(create_window_id):', bbox)
            except Exception as e:
                print('   canvas.bbox error:', e)
        # print props
        try:
            props = {k: sf.cget(k) for k in ('fg_color','corner_radius','border_width','border_color')}
        except Exception:
            props = {}
        print('   sf props:', props)
        # print packing of sf
        try:
            print('   sf.pack_info:', sf.pack_info())
        except:
            pass
        try:
            print('   sf.grid_info:', sf.grid_info())
        except:
            pass
    # print canvases under view and check if any extend outside content_card
    canvases = []
    def find_canv(w):
        for ch in w.winfo_children():
            if isinstance(ch, tkinter.Canvas):
                canvases.append(ch)
            find_canv(ch)
    find_canv(view)
    print('\n canvases count:', len(canvases))
    for c in canvases:
        px=c.winfo_rootx(); py=c.winfo_rooty(); pw=c.winfo_width(); ph=c.winfo_height()
        parent = c.master
        print('  Canvas', c, 'pos', px,py, 'size', pw,ph, 'parent', parent)
        if content_card:
            cx = content_card.winfo_rootx(); cy = content_card.winfo_rooty(); cw = content_card.winfo_width(); ch = content_card.winfo_height()
            left_out = max(0, cx - px)
            right_out = max(0, (px+pw) - (cx+cw))
            top_out = max(0, cy - py)
            bottom_out = max(0, (py+ph) - (cy+ch))
            if any((left_out,right_out,top_out,bottom_out)):
                print('   extends outside content_card by', left_out,right_out,top_out,bottom_out)
    view.pack_forget()
    root.update()

root.destroy()
print('\nAll done')
