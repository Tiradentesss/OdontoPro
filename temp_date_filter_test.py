import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'SistemaDesktop'))
from controllers.consulta_controller import ConsultaController

def run():
    data = '2026-08-14'
    where, params = ConsultaController._build_filters(1, data=data, status=None, medico=None, especialidade=None, medico_id=None, especialidade_id=None)
    print('WHERE:', where)
    print('PARAMS:', params)
    try:
        rows = ConsultaController.listar_por_clinica(1, data=data)
        print('ROWS', len(rows))
        if rows:
            print(rows[0])
    except Exception as e:
        print('ERROR', e)

if __name__ == '__main__':
    run()
