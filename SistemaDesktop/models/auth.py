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
        
        print(f"[DEBUG] Email: {email}")
        print(f"[DEBUG] Senha digitada: {senha}")
        print(f"[DEBUG] Senha hash gerada: {senha_hash}")

        # ================= CLÍNICA =================
        cursor.execute("""
            SELECT id, nome, senha
            FROM odontoPro_clinica
            WHERE email = %s
        """, (email,))

        clinica = cursor.fetchone()
        
        if clinica:
            print(f"[DEBUG] Clínica encontrada. Senha no BD: {clinica['senha']}")
            if clinica['senha'] == senha_hash:
                print("[DEBUG] Senha da clínica corresponde!")
                return {
                    "tipo": "clinica",
                    "id": clinica["id"],
                    "nome": clinica["nome"],
                    "clinica_id": clinica["id"]
                }
            else:
                print("[DEBUG] Senha da clínica NÃO corresponde")

        # ================= GERENCIAMENTO =================
        cursor.execute("""
            SELECT id, nome, clinica_id, senha
            FROM odontoPro_gerenciamento
            WHERE email = %s AND ativo = 1
        """, (email,))

        gerenciamento = cursor.fetchone()
        
        if gerenciamento:
            print(f"[DEBUG] Gerenciamento encontrado. Senha no BD: {gerenciamento['senha']}")
            if gerenciamento['senha'] == senha_hash:
                print("[DEBUG] Senha do gerenciamento corresponde!")
                return {
                    "tipo": "gerenciamento",
                    "id": gerenciamento["id"],
                    "nome": gerenciamento["nome"],
                    "clinica_id": gerenciamento["clinica_id"]
                }
            else:
                print("[DEBUG] Senha do gerenciamento NÃO corresponde")

        print("[DEBUG] Nenhum usuário encontrado ou senha inválida")
        return None

    except Exception as e:
        print(f"Erro de autenticação/DB: {e}")
        return None

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
