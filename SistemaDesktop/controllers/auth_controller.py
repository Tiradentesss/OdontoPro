from models.auth import autenticar_usuario


class AuthController:

    @staticmethod
    def autenticar(email, senha):

        usuario = autenticar_usuario(email, senha)

        if not usuario:
            return None

        return {
            "usuario": usuario
        }
