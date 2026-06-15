#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Adicionar path
sys.path.insert(0, r'c:\Users\58143406\Documents\Desktop_2\OdontoPro\SistemaDesktop')

from config.database import get_connection
from config.settings import DB_CONFIG
from models.auth import autenticar_usuario

print('='*60)
print('🔍 TESTE DE DIAGNÓSTICO - BANCO DE DADOS')
print('='*60)

# 1. Testar conexão
print('\n1️⃣ Testando conexão com banco de dados...')
print(f'   Host: {DB_CONFIG["host"]}')
print(f'   User: {DB_CONFIG["user"]}')
print(f'   Database: {DB_CONFIG["database"]}')
print(f'   Port: {DB_CONFIG["port"]}')

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT COUNT(*) as count FROM odontoPro_clinica')
    result = cursor.fetchone()
    print(f'   ✅ Conexão bem-sucedida!')
    print(f'   📊 Total de clínicas: {result["count"]}')
    
    # 2. Listar clínicas disponíveis
    print('\n2️⃣ Clínicas cadastradas:')
    cursor.execute('SELECT id, nome, email FROM odontoPro_clinica')
    clinicas = cursor.fetchall()
    for cli in clinicas:
        print(f'   - {cli["nome"]} ({cli["email"]})')
    
    # 3. Testar autenticação
    print('\n3️⃣ Testando autenticação...')
    if clinicas:
        email_teste = clinicas[0]['email']
        print(f'   Email: {email_teste}')
        
        # Tentar com algumas senhas comuns
        senhas_teste = ['admin@123', '123456', 'admin', 'password']
        
        for senha in senhas_teste:
            print(f'   Testando senha: {senha}...')
            resultado = autenticar_usuario(email_teste, senha)
            if resultado:
                print(f'   ✅ LOGIN BEM-SUCEDIDO com senha: {senha}')
                break
        else:
            print(f'   ❌ Nenhuma senha funcionou. Verifique o banco de dados.')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'   ❌ Erro na conexão: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*60)
