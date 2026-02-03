# controllers/gerente_controller.py

from models.model import USUARIOS

class GerenteController:

    @staticmethod
    def autenticar(usuario, senha):
        if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
            return USUARIOS[usuario]
        return None
