#!/usr/bin/env python3
"""
Script de teste para validar a funcionalidade de descrição de serviços.
"""

import sys
import os

# Adicionar o diretório SistemaDesktop ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from config.database import get_connection
from decimal import Decimal

def test_descricao_functionality():
    """Testa a funcionalidade de descrição de serviços."""
    
    conn = None
    cursor = None
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 70)
        print("TESTE DE FUNCIONALIDADE DE DESCRIÇÃO DE SERVIÇOS")
        print("=" * 70)
        
        # 1. Verificar coluna
        print("\n[1] Verificando se a coluna 'descricao' existe...")
        cursor.execute("""
            SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'odontoPro_especialidade' 
            AND COLUMN_NAME = 'descricao'
        """)
        col_info = cursor.fetchone()
        if col_info:
            print(f"   ✅ Coluna encontrada:")
            print(f"      - Tipo: {col_info['COLUMN_TYPE']}")
            print(f"      - Aceita NULL: {col_info['IS_NULLABLE']}")
        else:
            print("   ❌ Coluna NÃO encontrada!")
            return False
        
        # 2. Buscar um serviço existente
        print("\n[2] Buscando um serviço existente para teste...")
        cursor.execute("""
            SELECT id, nome, preco, clinica_id, descricao
            FROM odontoPro_especialidade
            LIMIT 1
        """)
        servico = cursor.fetchone()
        
        if not servico:
            print("   ❌ Nenhum serviço encontrado no banco!")
            return False
        
        serv_id = servico['id']
        serv_nome = servico['nome']
        serv_clinica_id = servico['clinica_id']
        
        print(f"   ✅ Serviço encontrado:")
        print(f"      - ID: {serv_id}")
        print(f"      - Nome: {serv_nome}")
        print(f"      - Clínica ID: {serv_clinica_id}")
        print(f"      - Descrição atual: {servico['descricao'] or '(vazio)'}")
        
        # 3. Testar UPDATE (salvar descrição)
        print("\n[3] Testando UPDATE (salvar descrição)...")
        descricao_teste = "Atendimento voltado à prevenção, diagnóstico e restauração da saúde bucal."
        
        cursor.execute("""
            UPDATE odontoPro_especialidade
            SET descricao = %s
            WHERE id = %s
            AND clinica_id = %s
        """, (descricao_teste, serv_id, serv_clinica_id))
        
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"   ✅ Descrição salva com sucesso!")
            print(f"      Linhas afetadas: {cursor.rowcount}")
        else:
            print(f"   ❌ Nenhuma linha foi atualizada!")
            return False
        
        # 4. Testar SELECT (recuperar descrição)
        print("\n[4] Testando SELECT (recuperar descrição)...")
        cursor.execute("""
            SELECT nome, descricao
            FROM odontoPro_especialidade
            WHERE id = %s
            AND clinica_id = %s
        """, (serv_id, serv_clinica_id))
        
        resultado = cursor.fetchone()
        
        if resultado:
            nome_recuperado = resultado['nome']
            desc_recuperada = resultado['descricao']
            
            print(f"   ✅ Dados recuperados:")
            print(f"      - Nome: {nome_recuperado}")
            print(f"      - Descrição: {desc_recuperada[:60]}..." if len(desc_recuperada or "") > 60 else f"      - Descrição: {desc_recuperada}")
            
            if desc_recuperada == descricao_teste:
                print(f"   ✅ Descrição salva e recuperada corretamente!")
            else:
                print(f"   ❌ Descrição não corresponde!")
                return False
        else:
            print("   ❌ Dados não encontrados!")
            return False
        
        # 5. Testar atualização com NULL
        print("\n[5] Testando atualização com NULL...")
        cursor.execute("""
            UPDATE odontoPro_especialidade
            SET descricao = NULL
            WHERE id = %s
            AND clinica_id = %s
        """, (serv_id, serv_clinica_id))
        
        conn.commit()
        
        cursor.execute("""
            SELECT descricao
            FROM odontoPro_especialidade
            WHERE id = %s
            AND clinica_id = %s
        """, (serv_id, serv_clinica_id))
        
        resultado = cursor.fetchone()
        if resultado['descricao'] is None:
            print(f"   ✅ Campo descricao atualizado para NULL com sucesso!")
        else:
            print(f"   ❌ Campo descricao não foi limpo!")
            return False
        
        # 6. Listar todos os serviços de uma clínica
        print("\n[6] Listando todos os serviços da clínica...")
        cursor.execute("""
            SELECT id, nome, preco, descricao
            FROM odontoPro_especialidade
            WHERE clinica_id = %s
            ORDER BY nome ASC
        """, (serv_clinica_id,))
        
        servicos = cursor.fetchall()
        
        if servicos:
            print(f"   ✅ {len(servicos)} serviço(s) encontrado(s):")
            for svc in servicos[:5]:  # Mostrar apenas os 5 primeiros
                desc = f"{svc['descricao'][:40]}..." if svc['descricao'] and len(svc['descricao']) > 40 else (svc['descricao'] or "(vazio)")
                print(f"      - {svc['nome']:<20} | R$ {svc['preco'] or '0.00':<8} | {desc}")
        else:
            print(f"   ❌ Nenhum serviço encontrado para a clínica!")
            return False
        
        print("\n" + "=" * 70)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    success = test_descricao_functionality()
    sys.exit(0 if success else 1)
