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
    ("Rafael Nunes", "13/02/2026", "16:00", "Cancelado"),
]
# ================== CONFIGURAÇÕES ==================

LIMITE_CONSULTAS = 6

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



