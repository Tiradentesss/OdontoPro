#!/usr/bin/env python3
"""Script de teste para verificar carregamento de dados da clínica"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from config.database import get_connection

def test_clinic_data():
    """Testa carregamento de dados da clínica"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Teste 1: Verificar se a tabela existe e quais colunas tem
        print("[TESTE 1] Verificando colunas da tabela...")
        cursor.execute("DESCRIBE odontoPro_clinica")
        columns = cursor.fetchall()
        print(f"Colunas encontradas: {[col[0] for col in columns]}")
        
        # Teste 2: Tentar carregar dados da clínica ID 1
        print("\n[TESTE 2] Carregando dados da clínica ID 1...")
        cursor.execute("""
            SELECT nome, cnpj, email, telefone, logo
            FROM odontoPro_clinica
            WHERE id = %s
        """, (1,))
        
        result = cursor.fetchone()
        if result:
            data = {
                "nome": result[0] or "",
                "cnpj": result[1] or "",
                "email": result[2] or "",
                "telefone": result[3] or "",
                "logo": result[4] or "",
            }
            print(f"✓ Dados carregados com sucesso:")
            for key, value in data.items():
                print(f"  - {key}: {value}")
        else:
            print("✗ Nenhum resultado encontrado para clinica_id 1")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clinic_data()
