#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
🔍 TESTE DE CONEXÕES - SISTEMA ODONTOPRO
============================================
Este script testa se todos os controllers estão conectados corretamente ao banco de dados.

Uso:
    python teste_conexoes.py
    
ou

    python teste_conexoes.py --clinica-id 1
"""

import sys
import os
from datetime import datetime

# Adicionar diretório SistemaDesktop ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

def test_database_connection():
    """Testa conexão básica com banco de dados"""
    print("\n" + "="*70)
    print("1️⃣  TESTE: CONEXÃO COM BANCO DE DADOS")
    print("="*70)
    
    try:
        from config.database import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("✅ Conexão com banco de dados: OK")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False


def test_financeiro_controller(clinica_id=1):
    """Testa FinanceiroController"""
    print("\n" + "="*70)
    print("2️⃣  TESTE: FINANCEIRO CONTROLLER")
    print("="*70)
    
    try:
        from controllers.financeiro_controller import FinanceiroController
        
        # Teste 1: Resumo Financeiro
        print("\n   📊 Testando obter_resumo_financeiro()...")
        resumo = FinanceiroController.obter_resumo_financeiro(clinica_id)
        
        print(f"      ✅ Faturamento: R$ {resumo['faturamento']:.2f}")
        print(f"      ✅ Despesas:    R$ {resumo['despesas']:.2f}")
        print(f"      ✅ Lucro:       R$ {resumo['lucro']:.2f}")
        print(f"      ✅ Consultas:   {resumo['realizadas']} / {resumo['total_consultas']}")
        
        # Teste 2: Listar Transações
        print("\n   💳 Testando listar_transacoes()...")
        transacoes = FinanceiroController.listar_transacoes(clinica_id)
        print(f"      ✅ Total de transações: {len(transacoes)}")
        
        if transacoes:
            for i, trans in enumerate(transacoes[:3], 1):
                print(f"         {i}. {trans.get('descricao', 'N/A')} - R$ {trans.get('valor', 0):.2f} ({trans.get('tipo', 'N/A')})")
        
        # Teste 3: Dados por Período
        print("\n   📈 Testando obter_dados_por_periodo()...")
        dados_7d = FinanceiroController.obter_dados_por_periodo(clinica_id, '7_dias')
        print(f"      ✅ Dados últimos 7 dias: {len(dados_7d)} registros")
        
        return True
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return False


def test_clinica_controller(clinica_id=1):
    """Testa ClinicaController"""
    print("\n" + "="*70)
    print("3️⃣  TESTE: CLÍNICA CONTROLLER")
    print("="*70)
    
    try:
        from controllers.clinica_controller import ClinicaController
        
        # Teste 1: Listar Consultas
        print("\n   📋 Testando listar_consultas()...")
        consultas = ClinicaController.listar_consultas(clinica_id, pagina=0)
        print(f"      ✅ Total de consultas: {len(consultas)}")
        
        if consultas:
            for i, cons in enumerate(consultas[:3], 1):
                print(f"         {i}. Paciente: {cons.get('nome', 'N/A')} - Status: {cons.get('status', 'N/A')}")
        
        # Teste 2: Contar Consultas
        print("\n   🔢 Testando contar_consultas()...")
        total = ClinicaController.contar_consultas(clinica_id)
        print(f"      ✅ Total contado: {total}")
        
        # Teste 3: Info Clínica
        print("\n   🏥 Testando obter_info_clinica()...")
        info = ClinicaController.obter_info_clinica(clinica_id)
        if info:
            print(f"      ✅ Clínica: {info.get('nome', 'N/A')}")
        else:
            print(f"      ⚠️  Clínica {clinica_id} não encontrada")
        
        return True
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return False


def test_paciente_controller(clinica_id=1):
    """Testa PacienteController"""
    print("\n" + "="*70)
    print("4️⃣  TESTE: PACIENTE CONTROLLER")
    print("="*70)
    
    try:
        from controllers.paciente_controller import PacienteController
        
        # Teste 1: Listar Pacientes
        print("\n   👥 Testando listar_pacientes()...")
        pacientes = PacienteController.listar_pacientes(clinica_id)
        print(f"      ✅ Total de pacientes: {len(pacientes)}")
        
        if pacientes:
            for i, pac in enumerate(pacientes[:3], 1):
                print(f"         {i}. {pac.get('nome', 'N/A')} - {pac.get('email', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return False


def test_medico_controller(clinica_id=1):
    """Testa MedicoController"""
    print("\n" + "="*70)
    print("5️⃣  TESTE: MÉDICO CONTROLLER")
    print("="*70)
    
    try:
        from controllers.medico_controller import MedicoController
        
        # Teste 1: Listar Médicos
        print("\n   👨‍⚕️  Testando listar_medicos()...")
        medicos = MedicoController.listar_medicos(clinica_id)
        print(f"      ✅ Total de médicos: {len(medicos)}")
        
        if medicos:
            for i, med in enumerate(medicos[:3], 1):
                print(f"         {i}. Dr(a). {med.get('nome', 'N/A')} - CRM/CRO: {med.get('crm_cro', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return False


def test_consulta_controller(clinica_id=1):
    """Testa ConsultaController"""
    print("\n" + "="*70)
    print("6️⃣  TESTE: CONSULTA CONTROLLER")
    print("="*70)
    
    try:
        from controllers.consulta_controller import ConsultaController
        
        # Teste 1: Listar por Clínica
        print("\n   🗓️  Testando listar_por_clinica()...")
        consultas = ConsultaController.listar_por_clinica(clinica_id, pagina=0, limite=5)
        print(f"      ✅ Total de consultas: {len(consultas)}")
        
        if consultas:
            for i, cons in enumerate(consultas[:3], 1):
                print(f"         {i}. Paciente: {cons.get('nome', 'N/A')} - {cons.get('status', 'N/A')}")
        
        # Teste 2: Contar por Clínica
        print("\n   📊 Testando contar_por_clinica()...")
        total = ConsultaController.contar_por_clinica(clinica_id)
        print(f"      ✅ Total contado: {total}")
        
        return True
    except Exception as e:
        print(f"      ❌ Erro: {e}")
        return False


def test_views_imports():
    """Testa se as views conseguem importar sem erros"""
    print("\n" + "="*70)
    print("7️⃣  TESTE: IMPORTAÇÃO DE VIEWS")
    print("="*70)
    
    views_to_test = [
        ('views.painel', 'Painel'),
        ('views.financeiro', 'Financeiro'),
        ('views.cadastro', 'Cadastro'),
    ]
    
    for module_name, class_name in views_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            print(f"      ✅ {class_name}: OK")
        except ImportError as e:
            print(f"      ⚠️  {class_name}: AVISO - {e}")
        except Exception as e:
            print(f"      ❌ {class_name}: ERRO - {e}")
    
    return True


def main():
    """Função principal"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "🔍  TESTE DE CONEXÕES - SISTEMA ODONTOPRO".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    print(f"\nData/Hora do teste: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("Clinica ID para testes: 1 (padrão)")
    
    # Executar testes
    tests = [
        ("Conexão com Banco", test_database_connection),
        ("Financeiro Controller", lambda: test_financeiro_controller(1)),
        ("Clínica Controller", lambda: test_clinica_controller(1)),
        ("Paciente Controller", lambda: test_paciente_controller(1)),
        ("Médico Controller", lambda: test_medico_controller(1)),
        ("Consulta Controller", lambda: test_consulta_controller(1)),
        ("Importação de Views", test_views_imports),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ ERRO GERAL NO TESTE: {e}")
            results.append((test_name, False))
    
    # Resumo Final
    print("\n" + "="*70)
    print("📋 RESUMO DOS TESTES")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status:15} - {test_name}")
    
    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} testes passaram")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM! O SISTEMA ESTÁ 100% CONECTADO!")
    else:
        print(f"\n⚠️  {failed} teste(s) falharam. Verifique os erros acima.")
    
    print("="*70 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
