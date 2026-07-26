from config.database import get_connection
from mysql.connector import Error


class EmailUniquenessService:
    EMAIL_DUPLICADO_MENSAGEM = (
        "E-mail já cadastrado\n"
        "Este endereço de e-mail já está sendo utilizado por outro cadastro.\n"
        "Informe um e-mail diferente."
    )

    @staticmethod
    def normalizar_email(email):
        if email is None:
            return None

        if not isinstance(email, str):
            email = str(email)

        email_normalizado = email.strip().lower()
        return email_normalizado or None

    @staticmethod
    def mensagem_email_duplicado():
        return EmailUniquenessService.EMAIL_DUPLICADO_MENSAGEM

    @staticmethod
    def email_ja_existe(email, tipo=None, entidade_id=None):
        email_normalizado = EmailUniquenessService.normalizar_email(email)
        if not email_normalizado:
            return False

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            try:
                if entidade_id is None:
                    cursor.execute(
                        "SELECT 1 FROM odontoPro_email_global WHERE email_normalizado = %s LIMIT 1",
                        (email_normalizado,)
                    )
                else:
                    cursor.execute(
                        """
                        SELECT 1
                        FROM odontoPro_email_global
                        WHERE email_normalizado = %s
                          AND NOT (tipo = %s AND entidade_id = %s)
                        LIMIT 1
                        """,
                        (email_normalizado, tipo, entidade_id)
                    )

                if cursor.fetchone() is not None:
                    return True
            except Exception:
                pass

            if entidade_id is None:
                cursor.execute(
                    """
                    SELECT 1 FROM odontoPro_paciente WHERE LOWER(TRIM(email)) = %s LIMIT 1
                    """,
                    (email_normalizado,)
                )
                if cursor.fetchone() is not None:
                    return True

                cursor.execute(
                    """
                    SELECT 1 FROM odontoPro_medico WHERE LOWER(TRIM(email)) = %s LIMIT 1
                    """,
                    (email_normalizado,)
                )
                if cursor.fetchone() is not None:
                    return True

                cursor.execute(
                    """
                    SELECT 1 FROM odontoPro_gerenciamento WHERE LOWER(TRIM(email)) = %s LIMIT 1
                    """,
                    (email_normalizado,)
                )
                return cursor.fetchone() is not None

            tabela = {
                'paciente': 'odontoPro_paciente',
                'medico': 'odontoPro_medico',
                'gerente': 'odontoPro_gerenciamento'
            }.get(tipo)

            if tabela:
                cursor.execute(
                    f"SELECT 1 FROM {tabela} WHERE LOWER(TRIM(email)) = %s AND id != %s LIMIT 1",
                    (email_normalizado, entidade_id)
                )
                return cursor.fetchone() is not None

            return False
        except Exception as e:
            print(f"Erro ao verificar e-mail único: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def tratar_erro_unique(e):
        if isinstance(e, Error):
            error_text = str(e).lower()
            if getattr(e, 'errno', None) == 1062 or 'duplicate entry' in error_text or 'unique' in error_text:
                return True
        elif isinstance(e, Exception):
            error_text = str(e).lower()
            if 'duplicate entry' in error_text or 'unique' in error_text or '1062' in error_text:
                return True
        return False
