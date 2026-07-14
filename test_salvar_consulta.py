"""
Teste de salvamento de consulta após correção
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from controllers.consulta_controller import ConsultaController
from datetime import datetime, timedelta

print("=" * 60)
print("TESTE: Salvando uma nova consulta")
print("=" * 60)

# IDs válidos da clínica (admin)
clinica_id = 1
paciente_id = 1  # Primeiro paciente
medico_id = 1    # Primeiro médico
especialidade_id = 1

# Data e hora para amanhã às 14:30
amanha = datetime.now() + timedelta(days=1)
data_hora = amanha.replace(hour=14, minute=30, second=0, microsecond=0)

print(f"\nDados para salvamento:")
print(f"  clinica_id: {clinica_id}")
print(f"  paciente_id: {paciente_id}")
print(f"  medico_id: {medico_id}")
print(f"  especialidade_id: {especialidade_id}")
print(f"  data_hora: {data_hora}")

resultado = ConsultaController.salvar_nova_consulta(
    clinica_id=clinica_id,
    paciente_id=paciente_id,
    medico_id=medico_id,
    data_hora=data_hora,
    especialidade="Ortodontista",
    status="agendada",
    observacoes="Consulta de teste",
    especialidade_id=especialidade_id
)

print("\n" + "=" * 60)
print("RESULTADO:")
print(f"Sucesso: {resultado.get('sucesso')}")
print(f"Mensagem: {resultado.get('mensagem')}")
if resultado.get('consulta_id'):
    print(f"ID da Consulta: {resultado.get('consulta_id')}")
if resultado.get('erro'):
    print(f"Erro: {resultado.get('erro')}")
print("=" * 60)
