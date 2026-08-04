import os, sys, inspect
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
SISTEMA_DIR = os.path.join(PROJECT_ROOT, 'SistemaDesktop')
if SISTEMA_DIR not in sys.path:
    sys.path.insert(0, SISTEMA_DIR)

import customtkinter as ctk
from SistemaDesktop.views.cadastro import Cadastro
import tkinter

ctk.set_appearance_mode('light')
root = ctk.CTk()
root.geometry('1200x800')

cad = Cadastro(root)
cad.pack(fill='both', expand=True)
root.update()

# find CTkScrollableFrame object as attribute on cad
sf_obj = getattr(cad, 'scroll_frame', None)

print('found scroll_frame object:', sf_obj)
if not sf_obj:
    root.destroy()
    sys.exit(1)

# access internals
parent_frame = getattr(sf_obj, '_parent_frame', None)
parent_canvas = getattr(sf_obj, '_parent_canvas', None)
create_win_id = getattr(sf_obj, '_create_window_id', None)

print('parent_frame class, size, reqsize:', parent_frame.__class__.__name__, parent_frame.winfo_width(), parent_frame.winfo_height(), parent_frame.winfo_reqwidth(), parent_frame.winfo_reqheight())
print('parent_canvas size, reqsize:', parent_canvas.winfo_width(), parent_canvas.winfo_height(), parent_canvas.winfo_reqwidth(), parent_canvas.winfo_reqheight())
print('scroll_frame (self) size, reqsize:', sf_obj.winfo_width(), sf_obj.winfo_height(), sf_obj.winfo_reqwidth(), sf_obj.winfo_reqheight())

# print bounding box of window item
try:
    bbox = parent_canvas.bbox(create_win_id)
    print('canvas.bbox(create_window_id):', bbox)
except Exception as e:
    print('error getting bbox:', e)

# print sum of children requested heights in the frame (self) — aggregate
sum_h = 0
for ch in sf_obj.winfo_children():
    h = ch.winfo_reqheight()
    sum_h += h
    print('child', ch, 'reqh', h, 'actualh', ch.winfo_height())
print('sum of direct children req heights:', sum_h)

# drill into container_conteudo
container = getattr(cad, 'container_conteudo', None)
if container:
    print('container_conteudo req size:', container.winfo_reqwidth(), container.winfo_reqheight(), 'actual:', container.winfo_width(), container.winfo_height())
    # compute vertical stacked height by iterating visible children and summing reqheight
    total = 0
    for ch in container.winfo_children():
        print(' container child', ch, 'reqh', ch.winfo_reqheight(), 'h', ch.winfo_height())
        total += ch.winfo_reqheight()
    print('sum container child req heights:', total)

# print whether pack_propagate/grid_propagate used on frames
print('cadastro_card grid/pack propagate?')
cadastro_card = getattr(cad, 'cadastro_card', None)
if cadastro_card:
    try:
        print('cadastro_card.pack_info', cadastro_card.pack_info())
    except:
        pass

root.destroy()
print('done')
