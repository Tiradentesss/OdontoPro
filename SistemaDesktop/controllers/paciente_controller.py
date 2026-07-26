# controllers/paciente_controller.py

from config.database import get_connection
import hashlib
from services.email_uniqueness_service import EmailUniquenessService


class PacienteController:
    
    @staticmethod
    def _obter_paciente_por_cpf(cpf):
        if not cpf:
            return None

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM odontoPro_paciente WHERE cpf = %s",
                (cpf,)
            )
            return cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar paciente por CPF: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _vinculo_existe(paciente_id, clinica_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM paciente_clinica WHERE paciente_id = %s AND clinica_id = %s AND status = 'ativo'",
                (paciente_id, clinica_id)
            )
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Erro ao verificar vínculo paciente-clínica: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _criar_vinculo_clinica(paciente_id, clinica_id):
        if paciente_id is None or clinica_id is None:
            print(f"Erro ao criar vínculo paciente-clínica: paciente_id={paciente_id}, clinica_id={clinica_id}")
            return False

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO paciente_clinica (paciente_id, clinica_id, data_vinculo, status) VALUES (%s, %s, NOW(), 'ativo')"
                " ON DUPLICATE KEY UPDATE status = 'ativo', data_vinculo = NOW()",
                (paciente_id, clinica_id)
            )
            conn.commit()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao criar vínculo paciente-clínica: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def criar_paciente(nome, cpf, sexo, email, data_nascimento, telefone, clinica_id, senha=None):
        """
        Cria um paciente no banco de dados.

        Se um paciente com o mesmo CPF já existir, informa que ele já está cadastrado.
        """
        # ✓ VALIDAÇÃO: Verificar campos obrigatórios
        if not nome or (isinstance(nome, str) and not nome.strip()):
            return {
                "sucesso": False,
                "mensagem": "Nome do paciente é obrigatório e não pode ser vazio."
            }
        
        if not email or (isinstance(email, str) and not email.strip()):
            return {
                "sucesso": False,
                "mensagem": "Email é obrigatório e não pode ser vazio."
            }
        
        if not telefone or (isinstance(telefone, str) and not telefone.strip()):
            return {
                "sucesso": False,
                "mensagem": "Telefone é obrigatório e não pode ser vazio."
            }
        
        # Limpar espaços em branco
        nome = nome.strip() if isinstance(nome, str) else str(nome)
        email = email.strip() if isinstance(email, str) else email
        telefone = telefone.strip() if isinstance(telefone, str) else telefone
        email_normalizado = EmailUniquenessService.normalizar_email(email)
        
        if email_normalizado and EmailUniquenessService.email_ja_existe(email_normalizado):
            return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}
        
        conn = None
        cursor = None
        try:
            paciente_existente = PacienteController._obter_paciente_por_cpf(cpf)
            if paciente_existente:
                return {"sucesso": False, "mensagem": "Paciente já cadastrado."}

            conn = get_connection()
            cursor = conn.cursor()

            senha_para_hash = senha if senha else "123456"
            senha_hash = hashlib.sha256(senha_para_hash.encode()).hexdigest()

            cursor.execute("""
                INSERT INTO odontoPro_paciente 
                (nome, cpf, sexo, email, data_nascimento, telefone, senha, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, sexo, email, data_nascimento, telefone, senha_hash, 1))

            paciente_id = cursor.lastrowid
            conn.commit()

            return {"sucesso": True, "id": paciente_id, "mensagem": "Paciente cadastrado com sucesso."}

        except Exception as e:
            if conn:
                conn.rollback()
            if EmailUniquenessService.tratar_erro_unique(e):
                return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}
            return {"sucesso": False, "mensagem": f"Erro ao cadastrar paciente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_pacientes(clinica_id=None):
        """
        Lista todos os pacientes ou filtra por clínica.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            if clinica_id:
                cursor.execute("""
                    SELECT p.*
                    FROM odontoPro_paciente p
                    JOIN paciente_clinica pc ON pc.paciente_id = p.id
                    WHERE pc.clinica_id = %s
                      AND pc.status = 'ativo'
                    ORDER BY p.nome ASC
                """, (clinica_id,))
            else:
                cursor.execute("SELECT * FROM odontoPro_paciente ORDER BY nome ASC")

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
            if 'email' in campos:
                email = campos.get('email')
                email_normalizado = EmailUniquenessService.normalizar_email(email)
                if email_normalizado and EmailUniquenessService.email_ja_existe(email_normalizado, tipo='paciente', entidade_id=paciente_id):
                    return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}

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
            if EmailUniquenessService.tratar_erro_unique(e):
                return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}
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
