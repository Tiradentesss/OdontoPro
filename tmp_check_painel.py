import sys
sys.path.append('SistemaDesktop')
from views.painel import Painel
from controllers.consulta_controller import ConsultaController

consultas = ConsultaController.listar_por_clinica(1, pagina=0, limite=10000)
print('consultas retornadas:', len(consultas))
print('resumo:', Painel._resumir_status_consultas(consultas))
