from config.database import get_connection
import hashlib
from datetime import datetime


class GerenciamentoController:
    
    @staticmethod
    def criar_gerente(nome, email, clinica_id, senha=None, permissoes=None):
        """
        Cria um novo gerente/usuário de gerenciamento no banco de dados
        
        IMPORTANTE:
        - Gerente sempre começa DESATIVADO (ativo=0)
        - Nenhuma permissão é atribuída na criação (permissões ficam vazias)
        - Permissões serão adicionadas em uma página separada
        
        senha: senha fornecida pelo usuário (se None, usa "123456" como padrão)
        permissoes: lista de IDs de permissões (ignorado na criação, sempre vazio)
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
                INSERT INTO odontoPro_gerenciamento 
                (nome, email, senha, clinica_id, ativo, criado_em)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nome, email, senha_hash, clinica_id, 0, datetime.now()))


            gerente_id = cursor.lastrowid

            # Permissões NÃO são adicionadas na criação
            # Elas serão gerenciadas em uma página separada
            # (permissoes é sempre None/ignorado neste método)

            conn.commit()
            return {"sucesso": True, "id": gerente_id, "mensagem": "Gerente cadastrado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao cadastrar gerente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_gerentes(clinica_id):
        """
        Lista todos os gerentes de uma clínica
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM odontoPro_gerenciamento WHERE clinica_id = %s AND ativo = 1
            """, (clinica_id,))

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao listar gerentes: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def obter_gerente_por_id(gerente_id):
        """
        Obtém um gerente específico pelo ID
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT * FROM odontoPro_gerenciamento WHERE id = %s
            """, (gerente_id,))

            return cursor.fetchone()

        except Exception as e:
            print(f"Erro ao obter gerente: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def obter_permissoes_gerente(gerente_id):
        """
        Obtém as permissões de um gerente
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT p.* FROM odontoPro_permissao p
                INNER JOIN odontoPro_gerenciamento_permissoes gp ON p.id = gp.permissao_id
                WHERE gp.gerenciamento_id = %s
            """, (gerente_id,))

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao obter permissões: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_permissoes_disponiveis():
        """
        Lista todas as permissões disponíveis no sistema
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM odontoPro_permissao")

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao listar permissões: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def atualizar_gerente(gerente_id, **campos):
        """
        Atualiza dados de um gerente
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Construir query dinamicamente
            set_clause = ", ".join([f"{k} = %s" for k in campos.keys()])
            valores = list(campos.values()) + [gerente_id]

            cursor.execute(f"""
                UPDATE odontoPro_gerenciamento SET {set_clause} WHERE id = %s
            """, valores)

            conn.commit()
            return {"sucesso": True, "mensagem": "Gerente atualizado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao atualizar gerente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def desativar_gerente(gerente_id):
        """
        Desativa um gerente (soft delete)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE odontoPro_gerenciamento SET ativo = 0 WHERE id = %s
            """, (gerente_id,))

            conn.commit()
            return {"sucesso": True, "mensagem": "Gerente desativado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao desativar gerente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def adicionar_permissao_gerente(gerente_id, permissao_id):
        """
        Adiciona uma permissão a um gerente existente
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Verificar se a permissão já existe
            cursor.execute("""
                SELECT 1 FROM odontoPro_gerenciamento_permissoes
                WHERE gerenciamento_id = %s AND permissao_id = %s
            """, (gerente_id, permissao_id))

            if cursor.fetchone():
                return {"sucesso": True, "mensagem": "Permissão já atribuída"}

            cursor.execute("""
                INSERT INTO odontoPro_gerenciamento_permissoes (gerenciamento_id, permissao_id)
                VALUES (%s, %s)
            """, (gerente_id, permissao_id))

            conn.commit()
            return {"sucesso": True, "mensagem": "Permissão adicionada com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao adicionar permissão: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def remover_permissao_gerente(gerente_id, permissao_id):
        """
        Remove uma permissão de um gerente
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM odontoPro_gerenciamento_permissoes
                WHERE gerenciamento_id = %s AND permissao_id = %s
            """, (gerente_id, permissao_id))

            conn.commit()
            return {"sucesso": True, "mensagem": "Permissão removida com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao remover permissão: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def ativar_gerente(gerente_id):
        """
        Ativa um gerente (após configuração de permissões)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE odontoPro_gerenciamento SET ativo = 1 WHERE id = %s
            """, (gerente_id,))

            conn.commit()
            return {"sucesso": True, "mensagem": "Gerente ativado com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao ativar gerente: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_todos_gerentes_por_clinica(clinica_id):
        """
        Lista TODOS os gerentes de uma clínica (incluindo inativos)
        Usado na tela de permissões para configurar novos gerentes
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, nome, email, ativo FROM odontoPro_gerenciamento 
                WHERE clinica_id = %s
                ORDER BY criado_em DESC
            """, (clinica_id,))

            return cursor.fetchall()

        except Exception as e:
            print(f"Erro ao listar gerentes: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def remover_todas_permissoes_gerente(gerente_id):
        """
        Remove TODAS as permissões de um gerente
        Usado na tela de permissões antes de salvar novas permissões
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM odontoPro_gerenciamento_permissoes 
                WHERE gerenciamento_id = %s
            """, (gerente_id,))

            conn.commit()
            return {"sucesso": True, "mensagem": "Permissões removidas com sucesso"}

        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao remover permissões: {str(e)}"}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def inicializar_permissoes_padrao():
        """
        Inicializa as permissões padrão do sistema no banco de dados
        Verifica se as permissões já existem antes de inserir (evita duplicatas)
        """
        conn = None
        cursor = None
        permissoes_padrao = [
            "Painel",
            "Agenda",
            "Financeiro",
            "Configurações",
            "Cadastro",
            "Permissões"
        ]
        
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Verificar quais permissões já existem no BD
            try:
                cursor.execute("SELECT codigo FROM odontoPro_permissao")
                permissoes_existentes = {row[0] for row in cursor.fetchall()}
                print(f"[PERMISSÕES] Já existem no BD: {permissoes_existentes}")
            except Exception as query_error:
                print(f"[ERRO] Falha ao consultar tabela odontoPro_permissao: {query_error}")
                print(f"[ERRO] Verifique se a tabela existe no banco de dados!")
                return {"sucesso": False, "mensagem": f"Tabela não encontrada: {str(query_error)}"}

            # Inserir as permissões que não existem
            inseridas = []
            for perm in permissoes_padrao:
                if perm not in permissoes_existentes:
                    try:
                        cursor.execute(
                            "INSERT INTO odontoPro_permissao (codigo) VALUES (%s)",
                            (perm,)
                        )
                        inseridas.append(perm)
                        print(f"[PERMISSÕES] ✓ Permissão inserida: {perm}")
                    except Exception as insert_error:
                        print(f"[ERRO] Falha ao inserir permissão '{perm}': {insert_error}")
                        raise
                else:
                    print(f"[PERMISSÕES] → Permissão já existe: {perm}")

            conn.commit()
            mensagem = f"Permissões inicializadas com sucesso. Inseridas: {inseridas}"
            print(f"[PERMISSÕES] ✓ {mensagem}")
            return {"sucesso": True, "mensagem": mensagem, "inseridas": inseridas}

        except Exception as e:
            if conn:
                conn.rollback()
            erro_msg = f"Erro ao inicializar permissões: {str(e)}"
            print(f"[ERRO] {erro_msg}")
            return {"sucesso": False, "mensagem": erro_msg}

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
