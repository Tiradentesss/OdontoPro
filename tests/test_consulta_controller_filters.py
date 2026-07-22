import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "SistemaDesktop"))

from SistemaDesktop.controllers.consulta_controller import ConsultaController


class ConsultaControllerFiltersTest(unittest.TestCase):
    def test_listar_por_clinica_repassa_ids_de_filtro_para_build_filters(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        cursor.execute.return_value = None

        conn = Mock()
        conn.cursor.return_value = cursor

        with patch("SistemaDesktop.controllers.consulta_controller.get_connection", return_value=conn):
            with patch.object(
                ConsultaController,
                "_build_filters",
                return_value=("c.clinica_id = %s", [1]),
            ) as build_filters_mock:
                ConsultaController.listar_por_clinica(
                    1,
                    data="2024-01-01",
                    status="agendada",
                    medico_id=7,
                    especialidade_id=3,
                )

        self.assertEqual(build_filters_mock.call_args.args[0], 1)
        self.assertEqual(build_filters_mock.call_args.args[1], "2024-01-01")
        self.assertEqual(build_filters_mock.call_args.args[2], "agendada")
        self.assertEqual(build_filters_mock.call_args.args[5:], (7, 3))


if __name__ == "__main__":
    unittest.main()
