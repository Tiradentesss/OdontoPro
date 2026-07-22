import sys
import pathlib
import os
import time
import customtkinter as ctk

root = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'SistemaDesktop'))
from views.agenda import Agenda

app = ctk.CTk()
app.withdraw()
frame = ctk.CTkFrame(app)
frame.pack()
agenda = Agenda(frame, clinica_id=1)
print('AGENDA created, filtro_data=', agenda.filtro_data, 'filtro_medico=', agenda.filtro_medico, 'filtro_status=', agenda.filtro_status, 'filtro_especialidade=', agenda.filtro_especialidade)
# give some time for the thread to execute
for _ in range(50):
    app.update()
    time.sleep(0.05)
print('after updates:', agenda._loading, agenda.current_snapshot)
app.destroy()
