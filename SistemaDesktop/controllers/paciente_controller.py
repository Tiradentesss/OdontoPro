# controllers/paciente_controller.py

from config.database import get_connection
import hashlib


class PacienteController:
    
    @staticmethod
    def criar_paciente(nome, cpf, sexo, email, data_nascimento, telefone, clinica_id, senha=None):
        """
        Cria um novo paciente no banco de dados
        
        senha: senha fornecida pelo usuário (se None, usa "123456" como padrão)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Usar senha fornecida ou "123456" como padrão
            senha_para_hash = senha if senha else "123456"
            senha_hash = hashlib.sha256(senha_para_hash.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO odontoPro_paciente 
                (nome, cpf, sexo, email, data_nascimento, telefone, senha)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, sexo, email, data_nascimento, telefone, senha_hash))

            conn.commit()
            return {"sucesso": True, "id": cursor.lastrowid, "mensagem": "Paciente cadastrado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao cadastrar paciente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_pacientes(clinica_id=None):
        """
        Lista todos os pacientes ou filtra por clínica
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if clinica_id:
                cursor.execute("""
                    SELECT * FROM odontoPro_paciente WHERE clinica_id = %s
                """, (clinica_id,))
            else:
                cursor.execute("SELECT * FROM odontoPro_paciente")

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao listar pacientes: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def obter_paciente_por_id(paciente_id):
        """
        Obtém um paciente específico pelo ID
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM odontoPro_paciente WHERE id = %s
            """, (paciente_id,))

            return cursor.fetchone()

        except Exception as e:
            print(f"Erro ao obter paciente: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def atualizar_paciente(paciente_id, **campos):
        """
        Atualiza dados de um paciente
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Construir query dinamicamente
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            valores = list(campos.values()) + [paciente_id]

            cursor.execute(f"""
                UPDATE odontoPro_paciente SET {set_clause} WHERE id = %s
            """, valores)

            conn.commit()
            return {"sucesso": True, "mensagem": "Paciente atualizado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao atualizar paciente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def deletar_paciente(paciente_id):
        """
        Deleta um paciente do banco
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM odontoPro_paciente WHERE id = %s", (paciente_id,))
            conn.commit()
            return {"sucesso": True, "mensagem": "Paciente deletado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao deletar paciente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
