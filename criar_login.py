import sys
import os
import hashlib

sys.path.insert(0, 'SistemaDesktop')
from config.database import get_connection
from datetime import datetime

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

print("=" * 70)
print("🔐 CRIANDO LOGIN NO ODONTOPRO")
print("=" * 70)

# Credenciais do novo usuário
EMAIL = "admin@odontopro.com"
SENHA = "admin123"
NOME = "Administrador OdontoPro"
CLINICA_ID = 1  # Usar a primeira clínica

try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar se o gerente já existe
    cursor.execute("SELECT id FROM odontoPro_gerenciamento WHERE email = %s", (EMAIL,))
    gerente_existente = cursor.fetchone()
    
    if gerente_existente:
        print(f"\n⚠️  Gerente com email {EMAIL} já existe!")
        print(f"   ID: {gerente_existente['id']}")
    else:
        # Criar novo gerente ATIVO
        senha_hash = hash_senha(SENHA)
        
        cursor.execute("""
            INSERT INTO odontoPro_gerenciamento 
            (nome, email, senha, clinica_id, ativo, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (NOME, EMAIL, senha_hash, CLINICA_ID, 1, datetime.now()))
        
        conn.commit()
        gerente_id = cursor.lastrowid
        
        print(f"\n✅ Gerente criado com sucesso!")
        print(f"   ID: {gerente_id}")
        print(f"   Nome: {NOME}")
        print(f"   Email: {EMAIL}")
        print(f"   Status: ATIVO")
        print(f"   Clínica ID: {CLINICA_ID}")
    
    # Listar todos os gerentes ativos
    print(f"\n📋 Gerentes ativos no sistema:")
    cursor.execute("""
        SELECT id, nome, email, clinica_id, ativo, criado_em
        FROM odontoPro_gerenciamento
        WHERE ativo = 1
        ORDER BY criado_em DESC
        LIMIT 10
    """)
    
    gerentes = cursor.fetchall()
    if gerentes:
        for g in gerentes:
            print(f"   - ID: {g['id']}, Nome: {g['nome']}, Email: {g['email']}, Ativo: {'✅' if g['ativo'] else '❌'}")
    
    # Também verificar login de clínica
    print(f"\n📋 Clínicas cadastradas (podem fazer login):")
    cursor.execute("""
        SELECT id, nome, email
        FROM odontoPro_clinica
        LIMIT 5
    """)
    
    clinicas = cursor.fetchall()
    for c in clinicas:
        print(f"   - ID: {c['id']}, Nome: {c['nome']}, Email: {c['email']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("🔑 CREDENCIAIS PARA LOGIN:")
    print("=" * 70)
    print(f"\n📧 Email: {EMAIL}")
    print(f"🔐 Senha: {SENHA}")
    print(f"\n✅ Tipo de usuário: GERENCIADOR")
    print(f"✅ Acesso: Clínica ID {CLINICA_ID}")
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
