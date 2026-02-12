from config.database import get_connection
from models.auth import autenticar_usuario
import hashlib


def autenticar_usuario(email, senha):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # ================= CLÍNICA =================
    cursor.execute("""
        SELECT id, nome
        FROM odontopro_clinica
        WHERE email = %s
          AND senha = %s
    """, (email, senha))

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
        SELECT id, nome
        FROM odontopro_gerenciamento
        WHERE email = %s
          AND senha = %s
          AND ativo = 1
    """, (email, senha))

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

USUARIOS = {
    "admin": {"senha": "123", "nome": "Lucas"},
}

CONSULTAS_DATA = [
    ("Maria Silva", "10/02/2026", "08:00", "Confirmado"),
    ("João Santos", "10/02/2026", "09:00", "Pendente"),
    ("Ana Costa", "10/02/2026", "10:00", "Cancelado"),
    ("Carlos Lima", "11/02/2026", "11:00", "Confirmado"),
    ("Fernanda Rocha", "11/02/2026", "13:00", "Confirmado"),
    ("Lucas Pereira", "12/02/2026", "14:00", "Pendente"),
    ("Juliana Alves", "12/02/2026", "15:00", "Confirmado"),
    ("Rafa nes", "14/02/2026", "15:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
    ("Rafael Nunes", "15/02/2026", "19:00", "Cancelado"),
    ("Lucas Pereira", "12/02/2026", "14:00", "Pendente"),
    ("Lucas Pereira", "12/02/2026", "14:00", "Pendente"),
    ("Lucas Tereira", "12/02/2026", "14:00", "Pendente"),
    ("Lucas Pereira", "12/02/2026", "14:00", "Pendente"),
    ("Lubas Pereira", "12/02/2026", "14:00", "Pendente"),
    ("Lucas Pereira", "12/02/2026", "14:00", "Pendente"),
    ("João Antos", "10/02/2026", "09:00", "Pendente"),
]
# ================== CONFIGURAÇÕES ==================

LIMITE_CONSULTAS = 20

STATUS_COLORS = {
    "Confirmado": {
        "bg": "#DCFCE7",
        "text": "#166534"
    },
    "Pendente": {
        "bg": "#FEF9C3",
        "text": "#854D0E"
    },
    "Cancelado": {
        "bg": "#FEE2E2",
        "text": "#991B1B"
    }
}



