from config.database import get_connection


class EspecialidadeService:
    @staticmethod
    def _normalize(nome):
        if nome is None:
            return None
        return nome.strip()

    @staticmethod
    def get_by_name(nome, conn=None):
        """Retorna tupla (id, nome) para o nome fornecido (case-insensitive, trimmed) ou None."""
        internal = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal = True
            cursor = conn.cursor(dictionary=True)
            nome_norm = EspecialidadeService._normalize(nome)
            if not nome_norm:
                return None
            cursor.execute("SELECT id, nome FROM odontoPro_especialidade WHERE LOWER(TRIM(nome)) = %s", (nome_norm.lower(),))
            return cursor.fetchone()
        except Exception:
            return None
        finally:
            if cursor:
                cursor.close()
            if internal and conn:
                conn.close()

    @staticmethod
    def create(nome, conn=None):
        """Cria nova especialidade e retorna seu ID."""
        internal = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal = True
            cursor = conn.cursor()
            nome_norm = EspecialidadeService._normalize(nome)
            if not nome_norm:
                return None
            cursor.execute("INSERT INTO odontoPro_especialidade (nome) VALUES (%s)", (nome_norm,))
            if internal:
                conn.commit()
            return cursor.lastrowid
        except Exception:
            if internal and conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if internal and conn:
                conn.close()

    @staticmethod
    def get_or_create(nome, conn=None):
        """Retorna o ID de uma especialidade existente (busca por nome ignorando case/espaces) ou cria uma nova.

        Se uma conexão for fornecida, usa-a (não fecha a conexão); útil para transações.
        """
        if nome is None:
            return None
        nome_norm = EspecialidadeService._normalize(nome)
        if not nome_norm:
            return None

        internal = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal = True
            cursor = conn.cursor(dictionary=True)

            # Buscar existente (case-insensitive, trimmed)
            cursor.execute("SELECT id, nome FROM odontoPro_especialidade WHERE LOWER(TRIM(nome)) = %s", (nome_norm.lower(),))
            row = cursor.fetchone()
            if row:
                return row['id']

            # Não existe: inserir
            # Use cursor sem dictionary para lastrowid
            cursor.close()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO odontoPro_especialidade (nome) VALUES (%s)", (nome_norm,))
            new_id = cursor.lastrowid
            if internal:
                conn.commit()
            return new_id
        except Exception:
            if internal and conn:
                conn.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if internal and conn:
                conn.close()
