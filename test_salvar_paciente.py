"""
Teste isolado para debugar o salvamento de pacientes
"""

import sys
import os

# Adicionar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from controllers.paciente_controller import PacienteController

# Teste 1: Tentar salvar paciente com todos os campos
print("=" * 60)
print("TESTE: Salvando um novo paciente")
print("=" * 60)

clinica_id = 1  # ID da clínica do admin

# Dados completos
resultado = PacienteController.criar_paciente(
    nome="João da Silva Teste",
    cpf="12345678901",
    sexo="M",
    email="joao.teste@email.com",
    data_nascimento="1990-01-01",
    telefone="11999999999",
    clinica_id=clinica_id,
    senha="senha123"
)

print("\n" + "=" * 60)
print("RESULTADO:")
print(f"Sucesso: {resultado.get('sucesso')}")
print(f"Mensagem: {resultado.get('mensagem')}")
if resultado.get('id'):
    print(f"ID do paciente: {resultado.get('id')}")
print("=" * 60)

# Teste 2: Tentar salvar paciente sem nome
print("\n\nTESTE 2: Salvando paciente SEM NOME (deve falhar)")
print("=" * 60)

resultado2 = PacienteController.criar_paciente(
    nome="",  # VAZIO!
    cpf="99999999999",
    sexo="F",
    email="maria@email.com",
    data_nascimento="1995-05-05",
    telefone="11888888888",
    clinica_id=clinica_id,
    senha="senha456"
)

print("\n" + "=" * 60)
print("RESULTADO:")
print(f"Sucesso: {resultado2.get('sucesso')}")
print(f"Mensagem: {resultado2.get('mensagem')}")
print("=" * 60)

# Teste 3: Tentar salvar paciente com None no nome
print("\n\nTESTE 3: Salvando paciente com nome=None (deve falhar)")
print("=" * 60)

resultado3 = PacienteController.criar_paciente(
    nome=None,  # None!
    cpf="88888888888",
    sexo="M",
    email="pedro@email.com",
    data_nascimento="1988-03-15",
    telefone="11777777777",
    clinica_id=clinica_id,
    senha="senha789"
)

print("\n" + "=" * 60)
print("RESULTADO:")
print(f"Sucesso: {resultado3.get('sucesso')}")
print(f"Mensagem: {resultado3.get('mensagem')}")
print("=" * 60)
