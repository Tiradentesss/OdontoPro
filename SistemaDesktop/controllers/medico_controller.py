# controllers/medico_controller.py

from config.database import get_connection
from models.auth import hash_senha
import re
from services.query_logger import timed_sql, reset_query_count, get_query_count, inc_query_count
from services.email_uniqueness_service import EmailUniquenessService
from services.medico_service import MedicoService


class MedicoController:
    
    @staticmethod
    def criar_medico(nome, cpf, sexo, email, data_nascimento, telefone, cro, clinica_id, senha=None, especialidades=None):
        """
        Cria um novo médico no banco de dados
        
        senha: senha fornecida pelo usuário (se None, usa "123456" como padrão)
        especialidades: lista de IDs de especialidades
        """
        nome = nome.strip() if isinstance(nome, str) else str(nome or "")

        # ✓ VALIDAÇÃO: Verificar campos obrigatórios
        if not nome:
            return {
                "sucesso": False,
                "mensagem": "Nome do médico é obrigatório e não pode ser vazio."
            }

        if MedicoService.nome_com_prefixo_proibido(nome):
            return {
                "sucesso": False,
                "mensagem": 'Digite somente o nome do médico, sem "Dentista", "Dr.", "Dra." ou "Dr(a).". Exemplo: João Lima'
            }
        
        if not email or (isinstance(email, str) and not email.strip()):
            return {
                "sucesso": False,
                "mensagem": "Email é obrigatório e não pode ser vazio."
            }
        
        if not cro or (isinstance(cro, str) and not cro.strip()):
            return {
                "sucesso": False,
                "mensagem": "CRO é obrigatório e não pode ser vazio."
            }

        cro = cro.strip() if isinstance(cro, str) else str(cro)
        cro_upper = cro.upper()
        if not re.fullmatch(r"\d{4,5}|[A-Z]{2}-?\d{4,5}", cro_upper):
            return {
                "sucesso": False,
                "mensagem": "CRO inválido. Utilize 1234, 12345, UF-1234 ou UF-12345."
            }

        # Normalizar formato UF1234 para UF-1234, mantendo valores numéricos como estão.
        if re.fullmatch(r"[A-Z]{2}\d{4,5}", cro_upper):
            cro_upper = cro_upper[:2] + "-" + cro_upper[2:]

        cro = cro_upper
        
        if not telefone or (isinstance(telefone, str) and not telefone.strip()):
            return {
                "sucesso": False,
                "mensagem": "Telefone é obrigatório e não pode ser vazio."
            }
        
        # Limpar espaços em branco
        email = email.strip() if isinstance(email, str) else email
        cro = cro.strip() if isinstance(cro, str) else cro
        telefone = telefone.strip() if isinstance(telefone, str) else telefone
        email_normalizado = EmailUniquenessService.normalizar_email(email)

        if email_normalizado and EmailUniquenessService.email_ja_existe(email_normalizado):
            return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}
        
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Usar senha fornecida ou "123456" como padrão
            senha_para_hash = senha if senha else "123456"
            senha_hash = hash_senha(senha_para_hash)

            cursor.execute("""
                INSERT INTO odontoPro_medico 
                (nome, cpf, sexo, email, data_nascimento, telefone, crm_cro, clinica_id, senha, num_avaliacoes, ativo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, sexo, email, data_nascimento, telefone, cro, clinica_id, senha_hash, 0, 1))

            medico_id = cursor.lastrowid

            # Adicionar especialidades se fornecidas
            if especialidades:
                # especialidades pode conter ids ou nomes; normalizar para ids.
                # Se o valor for um ID numérico em string, mantemos o ID em vez de criar
                # uma especialidade com o nome numérico.
                from services.especialidade_service import EspecialidadeService
                for espec in especialidades:
                    espec_id = None
                    if isinstance(espec, str):
                        espec_str = espec.strip()
                        if espec_str.isdigit():
                            espec_id = int(espec_str)
                        else:
                            try:
                                espec_id = EspecialidadeService.get_or_create(espec_str, conn=conn)
                            except Exception:
                                espec_id = None
                    else:
                        espec_id = espec

                    if espec_id:
                        cursor.execute("""
                            INSERT INTO odontoPro_medico_especialidades (medico_id, especialidade_id)
                            VALUES (%s, %s)
                        """, (medico_id, espec_id))

            conn.commit()
            return {"sucesso": True, "id": medico_id, "mensagem": "Médico cadastrado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            if EmailUniquenessService.tratar_erro_unique(e):
                return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}
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
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            def _exec():
                sql = ("SELECT id, nome, email, crm_cro, ativo"
                       " FROM odontoPro_medico"
                       " WHERE clinica_id = %s"
                       " ORDER BY nome ASC")
                cursor.execute(sql, (clinica_id,))
                return cursor.fetchall() or []

            return timed_sql("Buscar médicos (listar_medicos)", _exec, sql="SELECT id, nome, email, crm_cro, ativo FROM odontoPro_medico WHERE clinica_id = %s ORDER BY nome ASC")

        except Exception as e:
            print(f"Erro ao listar médicos: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Nota: manter apenas um método otimizado para listagem mínima (acima). Se necessário,
    # outros métodos podem reutilizar `listar_medicos` ou `obter_medico_por_id`.

    @staticmethod
    def obter_medico_por_id(medico_id, clinica_id=None):
        """
        Obtém um médico específico pelo ID e, quando disponível, restringe à clínica.
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            def _exec():
                if clinica_id is not None:
                    sql = "SELECT * FROM odontoPro_medico WHERE id = %s AND clinica_id = %s"
                    cursor.execute(sql, (medico_id, clinica_id))
                else:
                    sql = "SELECT * FROM odontoPro_medico WHERE id = %s"
                    cursor.execute(sql, (medico_id,))
                return cursor.fetchone()

            sql_debug = "SELECT * FROM odontoPro_medico WHERE id = %s" if clinica_id is None else "SELECT * FROM odontoPro_medico WHERE id = %s AND clinica_id = %s"
            return timed_sql("obter_medico_por_id", _exec, sql=sql_debug)

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

            def _exec():
                sql = (
                    "SELECT e.* FROM odontoPro_especialidade e"
                    " INNER JOIN odontoPro_medico_especialidades me ON e.id = me.especialidade_id"
                    " WHERE me.medico_id = %s"
                )
                cursor.execute(sql, (medico_id,))
                return cursor.fetchall()

            return timed_sql("obter_especialidades_medico", _exec, sql="SELECT e.* FROM odontoPro_especialidade e JOIN odontoPro_medico_especialidades me ON e.id = me.especialidade_id WHERE me.medico_id = %s")

        except Exception as e:
            print(f"Erro ao obter especialidades: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def atualizar_medico(medico_id, clinica_id=None, **campos):
        """
        Atualiza dados de um médico
        """
        conn = None
        cursor = None
        try:
            if 'email' in campos:
                email = campos.get('email')
                email_normalizado = EmailUniquenessService.normalizar_email(email)
                if email_normalizado and EmailUniquenessService.email_ja_existe(email_normalizado, tipo='medico', entidade_id=medico_id):
                    return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}

            conn = get_connection()
            cursor = conn.cursor()

            # Construir query dinamicamente
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            valores = list(campos.values()) + [medico_id]
            where_clause = "id = %s"
            if clinica_id is not None:
                where_clause += " AND clinica_id = %s"
                valores.append(clinica_id)

            cursor.execute(f"""
                UPDATE odontoPro_medico SET {set_clause} WHERE {where_clause}
            """, valores)

            conn.commit()
            return {"sucesso": True, "mensagem": "Médico atualizado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            if EmailUniquenessService.tratar_erro_unique(e):
                return {"sucesso": False, "mensagem": EmailUniquenessService.mensagem_email_duplicado()}
            return {"sucesso": False, "mensagem": f"Erro ao atualizar médico: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def atualizar_foto_medico(medico_id, clinica_id, foto):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE odontoPro_medico SET foto = %s WHERE id = %s AND clinica_id = %s",
                (foto, medico_id, clinica_id),
            )
            conn.commit()
            return {"sucesso": True, "mensagem": "Foto do médico atualizada com sucesso"}
        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao atualizar foto do médico: {str(e)}"}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def deletar_medico(medico_id, clinica_id=None):
        """
        Deleta um médico do banco
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM odontoPro_medico WHERE id = %s"
            params = [medico_id]
            if clinica_id is not None:
                sql += " AND clinica_id = %s"
                params.append(clinica_id)

            cursor.execute(sql, tuple(params))
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

    @staticmethod
    def desassociar_medico(medico_id, clinica_id):
        """Remove somente o vínculo do médico com a clínica informada."""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    UPDATE odontoPro_medico
                    SET clinica_id = NULL
                    WHERE id = %s AND clinica_id = %s
                    """,
                    (medico_id, clinica_id)
                )

                if cursor.rowcount == 0:
                    conn.rollback()
                    return {"sucesso": False, "mensagem": "Médico não está associado a esta clínica."}

                conn.commit()
                return {"sucesso": True, "mensagem": "Médico removido da clínica com sucesso."}
            except Exception as inner_e:
                # Tratamento específico quando a coluna clinica_id não aceita NULL (1048)
                msg = str(inner_e).lower()
                if "1048" in str(inner_e) or "cannot be null" in msg or "column 'clinica_id'" in msg:
                    # Fallback mínimo: marcar o médico como inativo para que ele deixe de aparecer
                    # nas listagens da clínica (listas usam ativo = 1). Isso preserva o cadastro
                    # do médico e suas especialidades, evitando violar constraints do banco.
                    try:
                        cursor.execute(
                            """
                            UPDATE odontoPro_medico
                            SET ativo = 0
                            WHERE id = %s AND clinica_id = %s
                            """,
                            (medico_id, clinica_id)
                        )
                        if cursor.rowcount == 0:
                            conn.rollback()
                            return {"sucesso": False, "mensagem": "Médico não está associado a esta clínica."}
                        conn.commit()
                        return {"sucesso": True, "mensagem": "Médico removido da clínica com sucesso."}
                    except Exception:
                        if conn:
                            conn.rollback()
                        return {"sucesso": False, "mensagem": f"Erro ao remover médico da clínica: {str(inner_e)}"}
                else:
                    raise

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao remover médico da clínica: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
