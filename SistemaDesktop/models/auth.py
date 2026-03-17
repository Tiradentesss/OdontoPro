import hashlib
from config.database import get_connection


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def autenticar_usuario(email, senha):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        senha_hash = hash_senha(senha)

        # ================= CLÍNICA =================
        cursor.execute("""
            SELECT id, nome
            FROM odontoPro_clinica
            WHERE email = %s
              AND (senha = %s OR senha = %s)
        """, (email, senha, senha_hash))

        clinica = cursor.fetchone()

        if clinica:
            return {
                "tipo": "clinica",
                "id": clinica["id"],
                "nome": clinica["nome"],
                "clinica_id": clinica["id"]
            }

        # ================= GERENCIAMENTO =================
        cursor.execute("""
            SELECT id, nome, clinica_id
            FROM odontoPro_gerenciamento
            WHERE email = %s
              AND (senha = %s OR senha = %s)
              AND ativo = 1
        """, (email, senha, senha_hash))

        gerenciamento = cursor.fetchone()

        if gerenciamento:
            return {
                "tipo": "gerenciamento",
                "id": gerenciamento["id"],
                "nome": gerenciamento["nome"],
                "clinica_id": gerenciamento["clinica_id"]
            }

        return None

    except Exception as e:
        print(f"Erro de autenticação/DB: {e}")
        return None

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
