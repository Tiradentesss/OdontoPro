#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar os cadastros de Pacientes e Médicos
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from config.database import get_connection

def test_conexao_banco():
    """Testa conexão com banco de dados"""
    print("\n" + "="*60)
    print("TESTE 1: CONEXÃO COM BANCO DE DADOS")
    print("="*60)
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT 1")
        result = cursor.fetchall()
        print("✅ Conexão com banco de dados: OK")
        
        # Listar clínicas disponíveis
        cursor.execute("SELECT id, nome FROM odontoPro_clinica LIMIT 5")
        clinicas = cursor.fetchall()
        print(f"✅ Clínicas encontradas: {len(clinicas)}")
        if clinicas:
            for clinica in clinicas:
                print(f"   - ID: {clinica['id']}, Nome: {clinica['nome']}")
        
        cursor.close()
        conn.close()
        return True, clinicas[0]['id'] if clinicas else None
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False, None

def test_criar_paciente(clinica_id):
    """Testa criação de paciente"""
    print("\n" + "="*60)
    print("TESTE 2: CRIAR PACIENTE")
    print("="*60)
    
    # Dados de teste
    dados_paciente = {
        "nome": "João Silva Teste",
        "cpf": "12345678901",
        "sexo": "M",
        "email": f"joao_teste_{os.urandom(4).hex()}@example.com",
        "data_nascimento": "1990-01-15",
        "telefone": "11987654321",
        "clinica_id": clinica_id,
        "senha": "senha123"
    }
    
    print(f"Criando paciente: {dados_paciente['nome']}")
    resultado = PacienteController.criar_paciente(**dados_paciente)
    
    if resultado["sucesso"]:
        print(f"✅ {resultado['mensagem']}")
        print(f"   ID do paciente: {resultado['id']}")
        return True, resultado['id']
    else:
        print(f"❌ {resultado['mensagem']}")
        return False, None

def test_listar_pacientes(clinica_id):
    """Testa listagem de pacientes"""
    print("\n" + "="*60)
    print("TESTE 3: LISTAR PACIENTES")
    print("="*60)
    
    try:
        pacientes = PacienteController.listar_pacientes(clinica_id)
        print(f"✅ Total de pacientes: {len(pacientes)}")
        if pacientes:
            print("   Últimos 3 pacientes:")
            for paciente in pacientes[-3:]:
                print(f"   - {paciente.get('nome', 'N/A')} ({paciente.get('email', 'N/A')})")
        return True
    except Exception as e:
        print(f"❌ Erro ao listar pacientes: {str(e)}")
        return False

def test_criar_medico(clinica_id):
    """Testa criação de médico"""
    print("\n" + "="*60)
    print("TESTE 4: CRIAR MÉDICO")
    print("="*60)
    
    # Dados de teste
    dados_medico = {
        "nome": "Dra. Maria Oliveira Teste",
        "cpf": "98765432101",
        "sexo": "F",
        "email": f"maria_teste_{os.urandom(4).hex()}@example.com",
        "data_nascimento": "1985-06-20",
        "telefone": "11912345678",
        "cro": "123456",
        "clinica_id": clinica_id,
        "senha": "senha123",
        "especialidades": [1]  # Odontologia Geral (ID 1)
    }
    
    print(f"Criando médico: {dados_medico['nome']}")
    resultado = MedicoController.criar_medico(**dados_medico)
    
    if resultado["sucesso"]:
        print(f"✅ {resultado['mensagem']}")
        print(f"   ID do médico: {resultado['id']}")
        return True, resultado['id']
    else:
        print(f"❌ {resultado['mensagem']}")
        return False, None

def test_listar_medicos(clinica_id):
    """Testa listagem de médicos"""
    print("\n" + "="*60)
    print("TESTE 5: LISTAR MÉDICOS")
    print("="*60)
    
    try:
        medicos = MedicoController.listar_medicos(clinica_id)
        print(f"✅ Total de médicos: {len(medicos)}")
        if medicos:
            print("   Últimos 3 médicos:")
            for medico in medicos[-3:]:
                print(f"   - {medico.get('nome', 'N/A')} ({medico.get('email', 'N/A')})")
        return True
    except Exception as e:
        print(f"❌ Erro ao listar médicos: {str(e)}")
        return False

def test_verificar_tabelas():
    """Verifica se as tabelas existem"""
    print("\n" + "="*60)
    print("TESTE 0: VERIFICAR TABELAS")
    print("="*60)
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        tabelas = ['odontoPro_paciente', 'odontoPro_medico', 'odontoPro_medico_especialidades']
        
        for tabela in tabelas:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
                count = cursor.fetchone()[0]
                print(f"✅ Tabela '{tabela}': OK ({count} registros)")
            except Exception as e:
                print(f"❌ Tabela '{tabela}': {str(e)}")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {str(e)}")
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "🔍 "*30)
    print("TESTE COMPLETO DE CADASTROS - OdontoPro")
    print("🔍 "*30)
    
    # Teste 0: Verificar tabelas
    test_verificar_tabelas()
    
    # Teste 1: Conexão
    sucesso_conexao, clinica_id = test_conexao_banco()
    if not sucesso_conexao or not clinica_id:
        print("\n❌ Não foi possível conectar ao banco de dados. Encerrando...")
        return
    
    # Teste 2: Criar Paciente
    sucesso_pac_criar, paciente_id = test_criar_paciente(clinica_id)
    
    # Teste 3: Listar Pacientes
    test_listar_pacientes(clinica_id)
    
    # Teste 4: Criar Médico
    sucesso_med_criar, medico_id = test_criar_medico(clinica_id)
    
    # Teste 5: Listar Médicos
    test_listar_medicos(clinica_id)
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"✅ Conexão com banco: {'OK' if sucesso_conexao else 'FALHOU'}")
    print(f"✅ Criar paciente: {'OK' if sucesso_pac_criar else 'FALHOU'}")
    print(f"✅ Criar médico: {'OK' if sucesso_med_criar else 'FALHOU'}")
    print("\n" + "="*60)
    
    if all([sucesso_conexao, sucesso_pac_criar, sucesso_med_criar]):
        print("✅ TODOS OS CADASTROS ESTÃO FUNCIONANDO!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM - VERIFIQUE OS ERROS ACIMA")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
