from config.database import get_connection
from models.auth import autenticar_usuario
import hashlib


def autenticar_usuario(email, senha):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    
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
            conn.close()
            return {
                "tipo": "clinica",
                "id": clinica["id"],
                "nome": clinica["nome"]
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

    conn.close()

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

# ================== CONFIGURAÇÕES ==================

LIMITE_CONSULTAS = 20

STATUS_COLORS = {
    "realizada": {
        "bg": "#DCFCE7",
        "text": "#166534"
    },
    "agendada": {
        "bg": "#FEF9C3",
        "text": "#854D0E"
    },
    "cancelada": {
        "bg": "#FEE2E2",
        "text": "#991B1B"
    }
}



