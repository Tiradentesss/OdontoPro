# controllers/medico_controller.py

from config.database import get_connection
import hashlib


class MedicoController:
    
    @staticmethod
    def criar_medico(nome, cpf, sexo, email, data_nascimento, telefone, cro, clinica_id, senha=None, especialidades=None):
        """
        Cria um novo médico no banco de dados
        
        senha: senha fornecida pelo usuário (se None, usa "123456" como padrão)
        especialidades: lista de IDs de especialidades
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
                INSERT INTO odontoPro_medico 
                (nome, cpf, sexo, email, data_nascimento, telefone, crm_cro, clinica_id, senha)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, sexo, email, data_nascimento, telefone, cro, clinica_id, senha_hash))

            medico_id = cursor.lastrowid

            # Adicionar especialidades se fornecidas
            if especialidades:
                for espec_id in especialidades:
                    cursor.execute("""
                        INSERT INTO odontoPro_medico_especialidades (medico_id, especialidade_id)
                        VALUES (%s, %s)
                    """, (medico_id, espec_id))

            conn.commit()
            return {"sucesso": True, "id": medico_id, "mensagem": "Médico cadastrado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao cadastrar médico: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_medicos(clinica_id):
        """
        Lista todos os médicos de uma clínica
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM odontoPro_medico WHERE clinica_id = %s
            """, (clinica_id,))

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao listar médicos: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def obter_medico_por_id(medico_id):
        """
        Obtém um médico específico pelo ID
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM odontoPro_medico WHERE id = %s
            """, (medico_id,))

            return cursor.fetchone()

        except Exception as e:
            print(f"Erro ao obter médico: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def obter_especialidades_medico(medico_id):
        """
        Obtém as especialidades de um médico
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT e.* FROM odontoPro_especialidade e
                INNER JOIN odontoPro_medico_especialidades me ON e.id = me.especialidade_id
                WHERE me.medico_id = %s
            """, (medico_id,))

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao obter especialidades: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def atualizar_medico(medico_id, **campos):
        """
        Atualiza dados de um médico
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Construir query dinamicamente
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            valores = list(campos.values()) + [medico_id]

            cursor.execute(f"""
                UPDATE odontoPro_medico SET {set_clause} WHERE id = %s
            """, valores)

            conn.commit()
            return {"sucesso": True, "mensagem": "Médico atualizado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao atualizar médico: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def deletar_medico(medico_id):
        """
        Deleta um médico do banco
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM odontoPro_medico WHERE id = %s", (medico_id,))
            conn.commit()
            return {"sucesso": True, "mensagem": "Médico deletado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao deletar médico: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
