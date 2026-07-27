from config.database import get_connection
import hashlib
import bcrypt
import base64
import hmac


def hash_senha(senha: str) -> str:
    """
    Gera um hash bcrypt (rounds=10) para novas senhas.
    """
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("utf-8")


def verificar_senha(senha_digitada: str, senha_salva: str) -> bool:
    """
    Verifica senha compatível com hashes antigos (sha256 hex) ou novos (bcrypt).
    Retorna True se a senha confere.
    """
    if not senha_salva:
        return False

    # bcrypt hashes iniciam com $2a$ ou $2b$ (ou $2y$ em alguns fornecedores)
    if senha_salva.startswith("$2"):
        try:
            return bcrypt.checkpw(senha_digitada.encode("utf-8"), senha_salva.encode("utf-8"))
        except Exception:
            return False

    # Django PBKDF2-SHA256 format: pbkdf2_sha256$iterations$salt$hash
    if senha_salva.startswith("pbkdf2_sha256$"):
        try:
            parts = senha_salva.split("$")
            # parts: [algorithm, iterations, salt, hash]
            if len(parts) != 4:
                return False
            iterations = int(parts[1])
            salt = parts[2]
            hash_b64 = parts[3]

            dk = hashlib.pbkdf2_hmac("sha256", senha_digitada.encode("utf-8"), salt.encode("utf-8"), iterations)
            computed_b64 = base64.b64encode(dk).decode().strip()
            return hmac.compare_digest(computed_b64, hash_b64)
        except Exception:
            return False

    # Unsupported hash format
    return False


def autenticar_usuario(email, senha):
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        print(f"[DEBUG] Email: {email}")
        print(f"[DEBUG] Senha digitada: {senha}")

        # ================= CLÍNICA =================
        cursor.execute("""
            SELECT id, nome, senha
            FROM odontoPro_clinica
            WHERE email = %s
        """, (email,))

        clinica = cursor.fetchone()

        if clinica:
            print(f"[DEBUG] Clínica encontrada. Senha no BD: {clinica['senha']}")
            if verificar_senha(senha, clinica['senha']):
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
            if verificar_senha(senha, gerenciamento['senha']):
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
