import hashlib
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path('SistemaDesktop').resolve()))
from config.database import get_connection
from controllers.gerenciamento_controller import GerenciamentoController

email = 'admin@odontopro.com'
senha = '12345678'

conn = None
cursor = None
try:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute('SELECT id, nome, clinica_id, ativo, senha FROM odontoPro_gerenciamento WHERE email = %s', (email,))
    gerente = cursor.fetchone()

    if gerente is None:
        cursor.execute('SELECT id FROM odontoPro_clinica ORDER BY id LIMIT 1')
        clinica = cursor.fetchone()
        clinica_id = clinica['id'] if clinica else 1
        cursor.execute('''
            INSERT INTO odontoPro_gerenciamento (nome, email, senha, clinica_id, ativo, criado_em)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', ('Admin', email, senha_hash, clinica_id, 1, datetime.now()))
        gerente_id = cursor.lastrowid
        print(f'CREATED:{gerente_id}')
    else:
        gerente_id = gerente['id']
        cursor.execute('''
            UPDATE odontoPro_gerenciamento
            SET senha = %s, ativo = 1, nome = %s
            WHERE id = %s
        ''', (senha_hash, 'Admin', gerente_id))
        print(f'UPDATED:{gerente_id}')

    resultado_perms = GerenciamentoController.inicializar_permissoes_padrao()
    print(f'INIT_PERMS:{resultado_perms.get("sucesso")}')

    cursor.execute('SELECT id, codigo FROM odontoPro_permissao ORDER BY id')
    permissoes = cursor.fetchall()
    if not permissoes:
        print('NO_PERMS')
    else:
        cursor.execute('DELETE FROM odontoPro_gerenciamento_permissoes WHERE gerenciamento_id = %s', (gerente_id,))
        for perm in permissoes:
            cursor.execute('''
                INSERT INTO odontoPro_gerenciamento_permissoes (gerenciamento_id, permissao_id)
                VALUES (%s, %s)
            ''', (gerente_id, perm['id']))
        print(f'ASSIGNED:{len(permissoes)}')

    conn.commit()

    cursor.execute('SELECT COUNT(*) AS total FROM odontoPro_gerenciamento_permissoes WHERE gerenciamento_id = %s', (gerente_id,))
    total = cursor.fetchone()['total']
    print(f'TOTAL:{total}')

except Exception as e:
    if conn:
        conn.rollback()
    print(f'ERROR:{e}')
    raise
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()
