import sys
import time
import pathlib
import customtkinter as ctk

root = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'SistemaDesktop'))

from views.agenda import Agenda
from controllers.consulta_controller import ConsultaController

app = ctk.CTk()
frame = ctk.CTkFrame(app)
frame.pack()
agenda = Agenda(frame, clinica_id=1)
print('initial data_var:', agenda.data_var.get(), 'filtro_data:', agenda.filtro_data)

# wait for initial render background thread to start
for _ in range(20):
    app.update()
    time.sleep(0.1)

print('after init data_var:', agenda.data_var.get(), 'filtro_data:', agenda.filtro_data)

# select a date from options
try:
    datas, medicos, especialidades = ConsultaController.listar_opcoes_filtro(1)
    print('datas len', len(datas), 'first', datas[0] if datas else None)
    if datas:
        value = datas[0].strftime('%d/%m/%Y')
        print('setting data', value)
        agenda.data_var.set(value)
        for _ in range(20):
            app.update()
            time.sleep(0.1)
        print('after set data_var:', agenda.data_var.get(), 'filtro_data:', agenda.filtro_data, 'data_sql:', agenda._get_data_sql())
except Exception as e:
    print('exception', e)
finally:
    app.destroy()
