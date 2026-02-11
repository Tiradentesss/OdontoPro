# controllers/clinica_controller.py

from models.data import CONSULTAS_DATA, LIMITE_CONSULTAS

class ClinicaController:

    @staticmethod
    def listar_consultas(pagina):
        inicio = pagina * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        return CONSULTAS_DATA[inicio:fim]
