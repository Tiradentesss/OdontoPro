import sys
import os
import time

root_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(root_dir, 'SistemaDesktop'))

import customtkinter as ctk
from views.agenda import Agenda

print('starting test')
root = ctk.CTk()
root.withdraw()
frame = Agenda(root, clinica_id=1)
root.update()
print('frame created, waiting...')
for i in range(10):
    root.update()
    time.sleep(0.5)
print('done waiting')
root.destroy()
