import os, sys
import customtkinter as ctk
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_PATH = os.path.join(ROOT_DIR, 'SistemaDesktop')
if SYS_PATH not in sys.path:
    sys.path.insert(0, SYS_PATH)

from SistemaDesktop.views.permissao import Permissoes

root = ctk.CTk()
root.geometry('1200x900')
root.update_idletasks()
perm = Permissoes(root)
perm.pack(fill='both', expand=True)
root.update()

print('CONTENT_CARD')
print({'path': perm.content_card._w, 'class': perm.content_card.__class__.__name__, 'w': perm.content_card.winfo_width(), 'h': perm.content_card.winfo_height(), 'x': perm.content_card.winfo_x(), 'y': perm.content_card.winfo_y()})
for i, child in enumerate(perm.content_card.winfo_children()):
    print(f'CHILD {i}:', {'path': child._w, 'class': child.__class__.__name__, 'w': child.winfo_width(), 'h': child.winfo_height(), 'x': child.winfo_x(), 'y': child.winfo_y()})
    for j, sub in enumerate(child.winfo_children()):
        print(f'  SUB {j}:', {'path': sub._w, 'class': sub.__class__.__name__, 'w': sub.winfo_width(), 'h': sub.winfo_height(), 'x': sub.winfo_x(), 'y': sub.winfo_y()})

root.after(2000, root.destroy)
root.mainloop()
