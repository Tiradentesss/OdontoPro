import sys
import pathlib
import os

root = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'SistemaDesktop'))
from controllers.consulta_controller import ConsultaController

cid = 1
print('========== DEBUG AGENDA ==========', flush=True)
print('Clínica ID:', cid, flush=True)
data = None
medico = None
status = None
especialidade = None
print('Data recebida:', data, flush=True)
print('Médico recebido:', medico, flush=True)
print('Status recebido:', status, flush=True)
print('Especialidade recebida:', especialidade, flush=True)
print('===============================', flush=True)
print('========== SQL ==========', flush=True)
where_clause, params = ConsultaController._build_filters(cid, data, status, medico, especialidade)
query = f"SELECT c.id,p.nome,c.data_hora,c.status,p.telefone,p.email,p.sexo,p.data_nascimento,p.cpf,p.foto,c.observacoes,m.nome AS medico_nome,COALESCE(e.nome, '') AS especialidade FROM odontoPro_consulta c LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id LEFT JOIN odontoPro_medico m ON c.medico_id = m.id LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id WHERE {where_clause} ORDER BY c.data_hora DESC LIMIT %s OFFSET %s"
print('SQL FINAL:', query, flush=True)
print('Parâmetros:', params + [20, 0], flush=True)
print('=========================', flush=True)
rows = ConsultaController.listar_por_clinica(cid)
print('Quantidade encontrada:', len(rows), flush=True)
print('IDs encontrados:', [r[0] for r in rows], flush=True)
print('Status encontrados:', [r[3] for r in rows], flush=True)
