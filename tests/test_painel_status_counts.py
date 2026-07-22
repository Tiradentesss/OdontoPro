import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "SistemaDesktop"))

from views.painel import Painel


def test_resumo_status_consultas_usa_registros_da_lista():
    consultas = [
        (1, "Ana", "2026-07-22 09:00:00", "agendada"),
        (2, "Bruno", "2026-07-22 10:00:00", "confirmada"),
        (3, "Carlos", "2026-07-22 11:00:00", "realizada"),
        (4, "Diana", "2026-07-22 12:00:00", "cancelada"),
        (5, "Edu", "2026-07-22 13:00:00", "AGENDADA"),
    ]

    resultado = Painel._resumir_status_consultas(consultas)

    assert resultado["agendada"] == 2
    assert resultado["confirmada"] == 1
    assert resultado["realizada"] == 1
    assert resultado["cancelada"] == 1
    assert resultado["total"] == 5
