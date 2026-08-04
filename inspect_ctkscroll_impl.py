import inspect
import customtkinter as ctk
from customtkinter import CTkScrollableFrame

print('CTkScrollableFrame class file:', inspect.getsourcefile(CTkScrollableFrame))
src = inspect.getsource(CTkScrollableFrame)
# print only relevant chunks around key method names
for name in ['__init__', '_create_window_id', '_fit_frame_dimensions_to_canvas', '_parent_canvas', '_get_window_scaling', '_apply_window_scaling']:
    sig = 'def ' + name
    start = src.find(sig)
    if start != -1:
        end = src.find('\ndef ', start+1)
        chunk = src[start:end if end != -1 else None]
        print('\n--- SOURCE for', name, '---')
        print(chunk[:4000])
    else:
        print('\n---', name, 'NOT FOUND in source ---')

# search for create_window and bind and update_idletasks
search_terms = ["create_window(", "bind(\"<Configure>\"", "bind('<Configure>'", 'update_idletasks', 'canvas.configure', 'create_window', 'window_create']
print('\nSearching keywords in source:')
for k in search_terms:
    idx = src.find(k)
    print(k, 'found at', idx)

# print entire source length
print('\nSource length:', len(src))
# print area around create_window
idx = src.find('create_window(')
if idx != -1:
    start = max(0, idx-200)
    end = min(len(src), idx+800)
    print('\n--- AROUND create_window ---')
    print(src[start:end])
else:
    print('\ncreate_window not found')
# print around _create_grid
idx = src.find('def _create_grid')
if idx != -1:
    start = max(0, idx-200)
    end = min(len(src), idx+1200)
    print('\n--- AROUND _create_grid ---')
    print(src[start:end])
else:
    print('\n_create_grid not found')
