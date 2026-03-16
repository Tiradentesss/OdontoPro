from config.database import get_connection
from models.auth import autenticar_usuario
import hashlib


def autenticar_usuario(email, senha):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    # ================= CLÍNICA =================
    cursor.execute("""
        SELECT id, nome
        FROM odontoPro_clinica
        WHERE email = %s
          AND (senha = %s OR senha = %s)
    """, (email, senha, senha_hash))

    clinica = cursor.fetchone()

    if clinica:
        conn.close()
        return {
            "tipo": "clinica",
            "id": clinica["id"],
            "nome": clinica["nome"]
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

    conn.close()

    if gerenciamento:
        return {
            "tipo": "gerenciamento",
            "id": gerenciamento["id"],
            "nome": gerenciamento["nome"],
            "clinica_id": gerenciamento["clinica_id"]
        }

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



