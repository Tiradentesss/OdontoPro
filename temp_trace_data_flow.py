import os
import sys
import queue
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.getcwd(), 'SistemaDesktop'))

from views.agenda import Agenda
from controllers.consulta_controller import ConsultaController

# Cria objeto Agenda mínimo para testar callback e thread
agenda = Agenda.__new__(Agenda)
agenda.data_var = SimpleNamespace(get=lambda: '25/07/2026')
agenda.medico_var = SimpleNamespace(get=lambda: 'Todos')
agenda.status_var = SimpleNamespace(get=lambda: 'Todos')
agenda.especialidade_var = SimpleNamespace(get=lambda: 'Todos')
agenda._trace_enabled = True
agenda.medico_opcoes = []
agenda.especialidade_opcoes = []
agenda.pagina_atual = 0
agenda.limite_por_pagina = 20
agenda.clinica_id = 1
agenda._load_queue = queue.Queue()
agenda._current_thread_id = 1
agenda._loading = False
agenda.filtro_data = None
agenda.filtro_medico = None
agenda.filtro_status = None
agenda.filtro_especialidade = None
agenda.filtro_medico_id = None
agenda.filtro_especialidade_id = None

# Stub refresh_data para não iniciar thread real
agenda.refresh_data = lambda: print('[TRACE] refresh_data stub called')

print('=== Chamando aplicar_filtros() ===')
agenda.aplicar_filtros()
print('=== Fim aplicar_filtros ===\n')

# Agora simular thread de carga direto com o filtro setado
agenda._load_data_thread()
print('=== Fim _load_data_thread ===\n')
