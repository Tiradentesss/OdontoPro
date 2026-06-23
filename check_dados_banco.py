#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'SistemaDesktop')
from config.database import get_connection

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    print("=" * 70)
    print("📊 DADOS SENDO SALVOS NO BANCO DE DADOS NA NUVEM")
    print("=" * 70)
    print()

    # Contar registros de cada tabela importante
    tabelas = {
        'odontoPro_paciente': 'Pacientes',
        'odontoPro_clinica': 'Clínicas',
        'odontoPro_medico': 'Médicos',
        'odontoPro_consulta': 'Consultas',
        'odontoPro_financeiro': 'Transações Financeiras',
        'odontoPro_gerenciamento': 'Gerenciadores'
    }

    print("📈 CONTAGEM DE REGISTROS POR TABELA:")
    print("-" * 70)
    for tabela, nome in tabelas.items():
        cursor.execute(f'SELECT COUNT(*) as count FROM {tabela}')
        count = cursor.fetchone()['count']
        print(f"   {nome}: {count} registros")

    # Mostrar últimas transações financeiras
    print()
    print("💰 ÚLTIMAS 5 TRANSAÇÕES FINANCEIRAS:")
    print("-" * 70)
    cursor.execute('''
        SELECT id, tipo, descricao, valor, data 
        FROM odontoPro_financeiro 
        ORDER BY data DESC 
        LIMIT 5
    ''')
    financeiras = cursor.fetchall()
    if financeiras:
        for tx in financeiras:
            tipo_emoji = "📥" if tx['tipo'] == 'receita' else "📤"
            print(f"   {tipo_emoji} ID: {tx['id']}")
            print(f"      Tipo: {tx['tipo']}")
            print(f"      Descrição: {tx['descricao']}")
            print(f"      Valor: R$ {tx['valor']}")
            print(f"      Data: {tx['data']}")
            print()
    else:
        print("   ℹ️  Nenhuma transação financeira registrada ainda")

    # Mostrar últimas consultas
    print("📅 ÚLTIMAS 5 CONSULTAS:")
    print("-" * 70)
    cursor.execute('''
        SELECT id, data_hora, status, paciente_id, medico_id
        FROM odontoPro_consulta 
        ORDER BY data_hora DESC 
        LIMIT 5
    ''')
    consultas = cursor.fetchall()
    if consultas:
        for cons in consultas:
            print(f"   ID: {cons['id']}")
            print(f"      Data: {cons['data_hora']}")
            print(f"      Status: {cons['status']}")
            print(f"      Paciente ID: {cons['paciente_id']}, Médico ID: {cons['medico_id']}")
            print()
    else:
        print("   ℹ️  Nenhuma consulta registrada ainda")

    print("=" * 70)
    print("✅ BANCO DE DADOS ESTÁ RECEBENDO DADOS COM SUCESSO!")
    print("=" * 70)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERRO: {e}")
    sys.exit(1)
