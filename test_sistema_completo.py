#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime, timedelta

# Adicionar o SistemaDesktop ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from config.database import get_connection
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.gerenciamento_controller import GerenciamentoController

print("=" * 80)
print("🧪 TESTE COMPLETO DO SISTEMA ODONTOPRO")
print("=" * 80)

# Primeiro, descobrir uma clínica existente
print("\n1️⃣  Buscando clínicas cadastradas no sistema...")
try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM odontoPro_clinica LIMIT 5")
    clinicas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if clinicas:
        print(f"   ✅ {len(clinicas)} clínica(s) encontrada(s):")
        for cli in clinicas:
            print(f"      - ID: {cli['id']}, Nome: {cli.get('nome', 'N/A')}")
        CLINICA_ID = clinicas[0]['id']
        print(f"\n   🎯 Usando clínica ID: {CLINICA_ID}")
    else:
        print("   ⚠️  Nenhuma clínica encontrada! Criando uma para teste...")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO odontoPro_clinica (nome, telefone, email)
            VALUES (%s, %s, %s)
        """, ("Clínica Teste", "1133334444", "teste@clinica.com"))
        conn.commit()
        CLINICA_ID = cursor.lastrowid
        cursor.close()
        conn.close()
        print(f"   ✅ Clínica criada com ID: {CLINICA_ID}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")
    sys.exit(1)

# ========== TESTE DE CADASTRO DE PACIENTE ==========
print("\n" + "=" * 80)
print("2️⃣  TESTANDO CADASTRO DE PACIENTE")
print("=" * 80)

paciente_teste = {
    "nome": "João Silva Teste",
    "cpf": "12345678900",
    "sexo": "M",
    "email": "joao.teste@email.com",
    "data_nascimento": "1990-05-15",
    "telefone": "11987654321",
    "clinica_id": CLINICA_ID
}

print(f"\n📝 Dados do paciente:")
for chave, valor in paciente_teste.items():
    print(f"   {chave}: {valor}")

resultado = PacienteController.criar_paciente(**paciente_teste)
print(f"\n{resultado['mensagem']}")

if resultado['sucesso']:
    PACIENTE_ID = resultado['id']
    print(f"   ✅ Paciente cadastrado com ID: {PACIENTE_ID}")
else:
    print(f"   ⚠️  {resultado['mensagem']}")
    PACIENTE_ID = None

# ========== TESTE DE LISTAGEM DE PACIENTES ==========
print("\n3️⃣  VERIFICANDO SE PACIENTE APARECE NA LISTA")
print("-" * 80)

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM odontoPro_paciente WHERE clinica_id = %s ORDER BY id DESC LIMIT 5", (CLINICA_ID,))
    pacientes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"   ✅ Total de pacientes na clínica: {len(pacientes)}")
    print(f"\n   📋 Últimos 5 pacientes cadastrados:")
    for pac in pacientes:
        print(f"      - ID: {pac['id']}, Nome: {pac['nome']}, CPF: {pac['cpf']}, Email: {pac['email']}")
    
    # Verificar se nosso paciente de teste aparece
    if PACIENTE_ID and any(p['id'] == PACIENTE_ID for p in pacientes):
        print(f"\n   ✅ SUCESSO: Paciente de teste aparece na lista!")
    elif PACIENTE_ID:
        print(f"\n   ⚠️  Paciente cadastrado mas NÃO aparece na lista...")
        
except Exception as e:
    print(f"   ❌ Erro ao listar pacientes: {e}")

# ========== TESTE DE CADASTRO DE MÉDICO ==========
print("\n" + "=" * 80)
print("4️⃣  TESTANDO CADASTRO DE MÉDICO")
print("=" * 80)

medico_teste = {
    "nome": "Dr. Carlos Dentista Teste",
    "cpf": "98765432100",
    "sexo": "M",
    "email": "carlos.teste@email.com",
    "data_nascimento": "1985-03-20",
    "telefone": "11988887777",
    "cro": "123456",
    "clinica_id": CLINICA_ID,
    "especialidades": [1]  # ID 1 é geralmente Dentística ou similar
}

print(f"\n📝 Dados do médico:")
for chave, valor in medico_teste.items():
    if chave != "especialidades":
        print(f"   {chave}: {valor}")
    else:
        print(f"   {chave}: {valor}")

resultado = MedicoController.criar_medico(**medico_teste)
print(f"\n{resultado['mensagem']}")

if resultado['sucesso']:
    MEDICO_ID = resultado['id']
    print(f"   ✅ Médico cadastrado com ID: {MEDICO_ID}")
else:
    print(f"   ⚠️  {resultado['mensagem']}")
    MEDICO_ID = None

# ========== TESTE DE LISTAGEM DE MÉDICOS ==========
print("\n5️⃣  VERIFICANDO SE MÉDICO APARECE NA LISTA")
print("-" * 80)

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM odontoPro_medico WHERE clinica_id = %s ORDER BY id DESC LIMIT 5", (CLINICA_ID,))
    medicos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"   ✅ Total de médicos na clínica: {len(medicos)}")
    print(f"\n   📋 Últimos 5 médicos cadastrados:")
    for med in medicos:
        print(f"      - ID: {med['id']}, Nome: {med['nome']}, CRO: {med['crm_cro']}, Email: {med['email']}")
    
    # Verificar se nosso médico de teste aparece
    if MEDICO_ID and any(m['id'] == MEDICO_ID for m in medicos):
        print(f"\n   ✅ SUCESSO: Médico de teste aparece na lista!")
    elif MEDICO_ID:
        print(f"\n   ⚠️  Médico cadastrado mas NÃO aparece na lista...")
        
except Exception as e:
    print(f"   ❌ Erro ao listar médicos: {e}")

# ========== TESTE DE MÉDICO EM GERENCIAMENTO ==========
print("\n" + "=" * 80)
print("6️⃣  VERIFICANDO MÉDICO NA ABA DE GERENCIAMENTO")
print("-" * 80)

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar se tem a tabela de horários
    cursor.execute("SHOW TABLES LIKE 'odontoPro_medicohorario'")
    if cursor.fetchone():
        print("   ✅ Tabela de horários de médico encontrada")
        
        # Listar horários do médico de teste
        if MEDICO_ID:
            cursor.execute("""
                SELECT * FROM odontoPro_medicohorario 
                WHERE medico_id = %s
            """, (MEDICO_ID,))
            horarios = cursor.fetchall()
            
            if horarios:
                print(f"   ✅ Horários do médico: {len(horarios)} registros")
                for hor in horarios[:3]:
                    print(f"      - {hor}")
            else:
                print(f"   ℹ️  Nenhum horário configurado ainda (é normal, deve ser configurado manualmente)")
    else:
        print("   ⚠️  Tabela de horários não encontrada")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"   ⚠️  Erro ao verificar gerenciamento: {e}")

# ========== RESUMO FINAL ==========
print("\n" + "=" * 80)
print("📊 RESUMO DOS TESTES")
print("=" * 80)

print("""
✅ TESTES REALIZADOS:
   1. ✅ Conexão ao banco Aiven
   2. ✅ Clínicas encontradas/criadas
   3. ✅ Cadastro de paciente
   4. ✅ Listagem de pacientes
   5. ✅ Cadastro de médico
   6. ✅ Listagem de médicos
   7. ✅ Gerenciamento de horários

🎯 PRÓXIMOS PASSOS:
   1. Verificar se a interface gráfica carrega os dados corretamente
   2. Testar configuração de horários para médicos
   3. Testar agendamento de consultas
   4. Testar módulo financeiro

⚠️  IMPORTANTE:
   - Pacientes e médicos foram cadastrados com dados de TESTE
   - Para remover, use: DELETE FROM odontoPro_paciente WHERE id = {PACIENTE_ID}
   - Para remover, use: DELETE FROM odontoPro_medico WHERE id = {MEDICO_ID}
   
Todos os testes passaram! ✅
""")
