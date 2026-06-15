#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# Adicionar o SistemaDesktop ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from config.database import get_connection

print("=" * 70)
print("🔗 TESTANDO CONEXÃO COM BANCO AIVEN")
print("=" * 70)

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n✅ Conexão estabelecida com sucesso!")
    print(f"   Host: odontoplace-odontopro2-87cf.f.aivencloud.com")
    print(f"   Database: defaultdb")
    print(f"   Port: 23912")
    
    # Teste 1: Verificar versão do MySQL
    print("\n1️⃣  Verificando versão do MySQL...")
    cursor.execute("SELECT VERSION();")
    version = cursor.fetchone()
    print(f"   ✅ Versão: {version[0]}")
    
    # Teste 2: Listar databases disponíveis
    print("\n2️⃣  Listando databases...")
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    print(f"   ✅ Databases encontrados:")
    for db in databases:
        print(f"      - {db[0]}")
    
    # Teste 3: Verificar tabelas
    print("\n3️⃣  Verificando tabelas do banco...")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    if tables:
        print(f"   ✅ Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")
    else:
        print("   ℹ️  Nenhuma tabela encontrada (banco vazio)")
    
    print("\n" + "=" * 70)
    print("✅ TUDO FUNCIONANDO PERFEITAMENTE!")
    print("=" * 70)
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERRO NA CONEXÃO:")
    print(f"   {type(e).__name__}: {e}")
    print("\n💡 Possíveis soluções:")
    print("   1. Verificar se a senha está correta")
    print("   2. Verificar se o host está acessível")
    print("   3. Verificar se o arquivo ca.pem existe")
    print("   4. Verificar permissões de firewall")
    sys.exit(1)
