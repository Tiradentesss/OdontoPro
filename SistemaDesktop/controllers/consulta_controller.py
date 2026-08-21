from datetime import datetime
from config.database import get_connection
from services.query_logger import timed_sql
from models.data import LIMITE_CONSULTAS
from services.paciente_service import PacienteService
from services.medico_service import MedicoService
from services.consulta_service import ConsultaService

class ConsultaController:

    @staticmethod
    def _build_filters(clinica_id, data=None, status=None, medico=None, especialidade=None, medico_id=None, especialidade_id=None):
        where = ["c.clinica_id = %s"]
        params = [clinica_id]

        if data and data not in ['Todos', 'Data', '']:
            where.append("DATE(c.data_hora) = DATE(%s)")
            params.append(data)

        if status and status not in ['Todos', 'Status', '']:
            where.append("LOWER(TRIM(c.status)) = %s")
            params.append(status.lower())

        if medico_id not in [None, '', 'Todos', 'Médico']:
            where.append("c.medico_id = %s")
            params.append(medico_id)
        elif medico and medico not in ['Todos', 'Médico', '']:
            where.append("m.nome = %s")
            params.append(medico)

        if especialidade_id not in [None, '', 'Todos', 'Especialidade']:
            where.append("c.especialidade_id = %s")
            params.append(especialidade_id)
        elif especialidade and especialidade not in ['Todos', 'Especialidade', '']:
            where.append("LOWER(TRIM(e.nome)) = %s")
            params.append(especialidade.lower())

        return " AND ".join(where), params

    @staticmethod
    def listar_por_clinica(clinica_id, pagina=0, limite=LIMITE_CONSULTAS, data=None, status=None, medico=None, especialidade=None, medico_id=None, especialidade_id=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            where_clause, params = ConsultaController._build_filters(
                clinica_id,
                data,
                status,
                medico,
                especialidade,
                medico_id,
                especialidade_id,
            )

            query = f"""
                SELECT
                    c.id,
                    p.nome,
                    c.data_hora,
                    c.status,
                    p.telefone,
                    p.email,
                    p.sexo,
                    p.data_nascimento,
                    p.cpf,
                    p.foto,
                    c.observacoes,
                    m.nome AS medico_nome,
                    COALESCE(e.nome, '') AS especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id
                WHERE {where_clause}
                ORDER BY c.data_hora ASC
                LIMIT %s OFFSET %s
            """

            params.extend([limite, pagina * limite])
            print('========== SQL E PARAMETROS ==========' )
            print(query)
            print('PARAMS =', params)
            print(f"[ConsultaController] Clínica: {clinica_id}")
            print(f"[ConsultaController] Filtro Data: {data}")
            print(f"[ConsultaController] Filtro Médico ID: {medico_id}")
            print(f"[ConsultaController] Filtro Especialidade ID: {especialidade_id}")
            print(f"[ConsultaController] Filtro Status: {status}")
            cursor.execute(query, tuple(params))
            dados = cursor.fetchall()
            print(f"[ConsultaController] Total de consultas encontradas: {len(dados) if dados else 0}")
            return dados or []
        except Exception as e:
            print(f"[ConsultaController] Erro em listar_por_clinica: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_proximas_por_clinica(clinica_id, limite=LIMITE_CONSULTAS, excluir_canceladas=True, apenas_confirmadas_futuras=False):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if apenas_confirmadas_futuras:
                where_clause = """
                    c.clinica_id = %s
                    AND c.data_hora >= %s
                    AND LOWER(TRIM(c.status)) = 'confirmada'
                """
                params = [clinica_id, datetime.now()]
                limite_consultas = 3
            else:
                where_clause = """
                    c.clinica_id = %s
                    AND DATE(c.data_hora) = CURDATE()
                    AND c.data_hora >= %s
                    AND LOWER(TRIM(c.status)) IN ('agendada', 'confirmada', 'reagendada')
                """
                params = [clinica_id, datetime.now()]
                limite_consultas = limite

            if excluir_canceladas and not apenas_confirmadas_futuras:
                where_clause += " AND LOWER(TRIM(c.status)) IN ('agendada', 'confirmada', 'reagendada')"

            query = f"""
                SELECT
                    c.id,
                    p.nome,
                    c.data_hora,
                    c.status,
                    p.telefone,
                    p.email,
                    p.sexo,
                    p.data_nascimento,
                    p.cpf,
                    p.foto,
                    c.observacoes,
                    m.nome AS medico_nome,
                    COALESCE(e.nome, '') AS especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id
                WHERE {where_clause}
                ORDER BY c.data_hora ASC
                LIMIT %s
            """

            params.append(limite_consultas)
            cursor.execute(query, tuple(params))
            dados = cursor.fetchall()
            print(f"[ConsultaController] Total de próximas consultas encontradas: {len(dados) if dados else 0}")
            return dados or []
        except Exception as e:
            print(f"[ConsultaController] Erro em listar_proximas_por_clinica: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def contar_por_clinica(clinica_id, data=None, status=None, medico=None, especialidade=None, medico_id=None, especialidade_id=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            where_clause, params = ConsultaController._build_filters(
                clinica_id,
                data,
                status,
                medico,
                especialidade,
                medico_id,
                especialidade_id,
            )

            cursor.execute(f"""
                SELECT COUNT(*)
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id
                WHERE {where_clause}
            """, tuple(params))

            total = cursor.fetchone()[0]
            return int(total or 0)
        except Exception as e:
            print(f"[ConsultaController] Erro em contar_por_clinica: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_opcoes_filtro(clinica_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT DATE(c.data_hora)
                FROM odontoPro_consulta c
                WHERE c.clinica_id = %s
                ORDER BY DATE(c.data_hora) DESC
            """, (clinica_id,))

            datas = [row[0] for row in cursor.fetchall() or []]

            medicos = ConsultaController.listar_medicos(clinica_id)
            # Use the shared prepared list for combos to avoid duplicates and ensure ordering
            especialidades = ConsultaController.listar_especialidades_para_combo(conn=conn)

            return datas, medicos, especialidades
        except Exception as e:
            print(f"[ConsultaController] Erro em listar_opcoes_filtro: {e}")
            import traceback
            traceback.print_exc()
            return [], [], []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def buscar_por_id(consulta_id, clinica_id=None):
        conn = get_connection()
        cursor = conn.cursor()

        if clinica_id is not None:
            cursor.execute("""
                SELECT
                    c.id,
                    p.nome,
                    c.data_hora,
                    c.status,
                    p.telefone,
                    p.email,
                    p.sexo,
                    p.data_nascimento,
                    p.cpf,
                    p.foto,
                    c.observacoes,
                    m.nome AS medico_nome,
                    COALESCE((
                        SELECT e.nome
                        FROM odontoPro_medico_especialidades me
                        JOIN odontoPro_especialidade e ON me.especialidade_id = e.id
                        WHERE me.medico_id = m.id
                        ORDER BY e.nome
                        LIMIT 1
                    ), '') AS especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                WHERE c.id = %s
                  AND c.clinica_id = %s
            """, (consulta_id, clinica_id,))
        else:
            cursor.execute("""
                SELECT
                    c.id,
                    p.nome,
                    c.data_hora,
                    c.status,
                    p.telefone,
                    p.email,
                    p.sexo,
                    p.data_nascimento,
                    p.cpf,
                    p.foto,
                    c.observacoes,
                    m.nome AS medico_nome,
                    COALESCE((
                        SELECT e.nome
                        FROM odontoPro_medico_especialidades me
                        JOIN odontoPro_especialidade e ON me.especialidade_id = e.id
                        WHERE me.medico_id = m.id
                        ORDER BY e.nome
                        LIMIT 1
                    ), '') AS especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                WHERE c.id = %s
            """, (consulta_id,))

        dado = cursor.fetchone()
        conn.close()
        return dado

    @staticmethod
    def obter_medico_consulta(consulta_id, clinica_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT medico_id
                FROM odontoPro_consulta
                WHERE id = %s AND clinica_id = %s
            """, (consulta_id, clinica_id))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"[ConsultaController] Erro ao obter médico da consulta: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def atualizar_status_atendimento(consulta_id, clinica_id, status_atual, novo_status):
        transicoes = {
            ('agendada', 'confirmada'),
            ('confirmada', 'realizada'),
        }
        status_atual = (status_atual or '').strip().lower()
        novo_status = (novo_status or '').strip().lower()

        if (status_atual, novo_status) not in transicoes:
            return False

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            date_condition = """
                AND DATE(data_hora) = CURDATE()
            """ if (status_atual, novo_status) == ('confirmada', 'realizada') else ""
            cursor.execute(f"""
                UPDATE odontoPro_consulta
                SET status = %s
                WHERE id = %s
                  AND clinica_id = %s
                  AND LOWER(TRIM(status)) = %s
                {date_condition}
            """, (novo_status, consulta_id, clinica_id, status_atual))
            conn.commit()
            return cursor.rowcount == 1
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ConsultaController] Erro ao atualizar status de atendimento: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def reagendar_consulta(consulta_id, clinica_id, data_hora):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT medico_id, status
                FROM odontoPro_consulta
                WHERE id = %s AND clinica_id = %s
            """, (consulta_id, clinica_id))
            consulta = cursor.fetchone()
            if not consulta or (consulta[1] or '').strip().lower() != 'agendada':
                return False

            if data_hora.date() < datetime.now().date():
                return False

            medico_id = consulta[0]
            horarios = ConsultaService.carregar_horarios_disponiveis(
                medico_id,
                data_hora.date(),
                clinica_id,
                conn=conn,
                excluir_consulta_id=consulta_id,
            )
            if data_hora.strftime('%H:%M') not in horarios:
                return False

            cursor.execute("""
                UPDATE odontoPro_consulta
                SET data_hora = %s
                WHERE id = %s
                  AND clinica_id = %s
                  AND medico_id = %s
                  AND LOWER(TRIM(status)) = 'agendada'
            """, (data_hora, consulta_id, clinica_id, medico_id))
            conn.commit()
            return cursor.rowcount == 1
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ConsultaController] Erro ao reagendar consulta: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def snapshot_por_clinica(clinica_id, data=None, status=None, medico=None, especialidade=None, medico_id=None, especialidade_id=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            where_clause, params = ConsultaController._build_filters(
                clinica_id,
                data,
                status,
                medico,
                especialidade,
                medico_id,
                especialidade_id,
            )

            cursor.execute(f"""
                SELECT CONCAT(COUNT(*), '-', IFNULL(MAX(c.id), 0), '-', IFNULL(MIN(c.id), 0), '-', COALESCE(MAX(UNIX_TIMESTAMP(c.data_hora)), 0))
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON e.id = c.especialidade_id
                WHERE {where_clause}
            """, tuple(params))

            snapshot = cursor.fetchone()[0]
            return snapshot or "0-0-0-0"
        except Exception as e:
            print(f"[ConsultaController] Erro em snapshot_por_clinica: {e}")
            import traceback
            traceback.print_exc()
            return "0-0-0-0"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_pacientes(clinica_id):
        """Lista todos os pacientes da clínica"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.id, p.nome
            FROM odontoPro_paciente p
            JOIN paciente_clinica pc ON pc.paciente_id = p.id
            WHERE pc.clinica_id = %s
              AND pc.status = 'ativo'
            ORDER BY p.nome ASC
        """, (clinica_id,))
        
        pacientes = cursor.fetchall()
        conn.close()
        return pacientes

    @staticmethod
    def listar_medicos(clinica_id):
        """Lista todos os médicos da clínica"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome
            FROM odontoPro_medico
            WHERE clinica_id = %s
            ORDER BY nome ASC
        """, (clinica_id,))
        
        medicos = cursor.fetchall()
        conn.close()
        return medicos

    @staticmethod
    def listar_especialidades(conn=None):
        """Lista todas as especialidades odontológicas, adaptando-se à estrutura real da tabela."""
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()
            # Tenta acessar tabela canônica de especialidades primeiro
            try:
                def _exec_main():
                    # Return canonical one-row-per-normalized-name: choose the MIN(id) for each normalized name
                    # Join back to retrieve the canonical name from that row. This guarantees deterministic
                    # selection of the ID (the smallest id for each normalized name) regardless of physical order.
                    sql = (
                        "SELECT t.id, t.nome "
                        "FROM odontoPro_especialidade t "
                        "JOIN (SELECT MIN(id) AS id FROM odontoPro_especialidade GROUP BY LOWER(TRIM(nome))) grp "
                        "ON t.id = grp.id "
                        "ORDER BY t.nome ASC"
                    )
                    cursor.execute(sql)
                    return cursor.fetchall()
                especialidades = timed_sql("listar_especialidades - tabela direta", _exec_main, sql="SELECT MIN(id) ... GROUP BY LOWER(TRIM(nome))")
                if especialidades:
                    return especialidades
            except Exception:
                pass

            # Se não existir, procurar tabelas que contenham 'especialidade' no nome
            def _exec_tables():
                sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() AND LOWER(table_name) LIKE '%especialidade%' ORDER BY table_name"
                cursor.execute(sql)
                return [row[0] for row in cursor.fetchall()]
            tabelas = timed_sql("listar_especialidades - descobrir tabelas", _exec_tables, sql="information_schema.tables LIKE '%especialidade%'") or []

            for tabela in tabelas:
                def _exec_cols():
                    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = %s", (tabela,))
                    return cursor.fetchall()
                cols = timed_sql(f"listar_especialidades - colunas {tabela}", _exec_cols, sql="information_schema.columns") or []
                colunas = [row[0].lower() for row in cols]

                coluna_id = next((col for col in ['id', 'codigo', 'especialidade_id'] if col in colunas), None)
                coluna_nome = next((col for col in ['nome', 'name', 'descricao', 'descricao_especialidade', 'especialidade'] if col in colunas), None)

                if coluna_id and coluna_nome:
                    def _exec_select():
                        cursor.execute(f"SELECT `{coluna_id}`, `{coluna_nome}` FROM `{tabela}` ORDER BY `{coluna_nome}` ASC")
                        return cursor.fetchall()
                    return timed_sql(f"listar_especialidades - tabela {tabela}", _exec_select, sql=f"SELECT {coluna_id}, {coluna_nome} FROM {tabela}") or []

            return []
        except Exception:
            return []
        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def listar_especialidades_por_clinica(clinica_id, conn=None):
        """Lista especialidades válidas para a clínica informada.

        Primeiro tenta usar as especialidades cadastradas para essa clínica.
        Se a clínica não tiver especialidades próprias, retorna as especialidades
        associadas aos médicos daquela clínica.
        """

        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()

            cursor.execute(
                """
                    SELECT id, nome
                    FROM odontoPro_especialidade
                    WHERE clinica_id = %s
                    ORDER BY nome ASC
                """,
                (clinica_id,)
            )
            especialidades = cursor.fetchall() or []
            if especialidades:
                return especialidades

            cursor.execute(
                """
                    SELECT DISTINCT e.id, e.nome
                    FROM odontoPro_especialidade e
                    JOIN odontoPro_medico_especialidades me ON e.id = me.especialidade_id
                    JOIN odontoPro_medico m ON m.id = me.medico_id
                    WHERE m.clinica_id = %s
                    ORDER BY e.nome ASC
                """,
                (clinica_id,)
            )
            return cursor.fetchall() or []
        except Exception as e:
            print(f"[ConsultaController] Erro em listar_especialidades_por_clinica: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def preparar_especialidades_para_combo(especialidades):
        """Normaliza e ordena especialidades para uso em combo."""
        if not especialidades:
            return []

        # The query that provides `especialidades` already deduplicates by normalized name and
        # returns the canonical id (MIN(id)) for each normalized name. Here we only need to
        # normalize spacing and return an alphabetically ordered list of tuples (id, nome).
        cleaned = []
        for especialidade_id, nome in especialidades:
            nome_limpo = (nome or "").strip()
            if especialidade_id is not None and nome_limpo:
                cleaned.append((especialidade_id, nome_limpo))

        return sorted(cleaned, key=lambda item: item[1].lower())

    @staticmethod
    def listar_especialidades_para_combo(clinica_id=None, conn=None):
        """Retorna a lista de especialidades pronta para uso em ComboBoxes:
        deduplicada, com nomes limpos e ordenada alfabeticamente.

        Este método reutiliza as funções existentes `listar_especialidades` e
        `preparar_especialidades_para_combo` para garantir uma única fonte de
        verdade para as especialidades usadas em diferentes telas.
        """
        if clinica_id is not None:
            especialidades_db = ConsultaController.listar_especialidades_por_clinica(clinica_id, conn=conn)
        else:
            especialidades_db = ConsultaController.listar_especialidades(conn=conn)
        return ConsultaController.preparar_especialidades_para_combo(especialidades_db)

    @staticmethod
    def criar_consulta(clinica_id, paciente_id, medico_id, data_hora, status='agendada', especialidade='', observacoes='', especialidade_id=None):
        """Cria uma nova consulta"""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'odontoPro_consulta'")
            colunas_consulta = [row[0].lower() for row in cursor.fetchall()]

            if 'especialidade_id' in colunas_consulta:
                cursor.execute("""
                    INSERT INTO odontoPro_consulta 
                    (clinica_id, paciente_id, medico_id, especialidade_id, data_hora, status, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (clinica_id, paciente_id, medico_id, especialidade_id, data_hora, status, observacoes))
            else:
                cursor.execute("""
                    INSERT INTO odontoPro_consulta 
                    (clinica_id, paciente_id, medico_id, data_hora, status, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (clinica_id, paciente_id, medico_id, data_hora, status, observacoes))
            
            conn.commit()
            consulta_id = cursor.lastrowid
            conn.close()
            
            return {"sucesso": True, "consulta_id": consulta_id}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==================== NOVOS MÉTODOS COM SERVICES ====================

    @staticmethod
    def buscar_pacientes_dinamico(termo_busca, limite=20, offset=0, conn=None):
        """
        Busca pacientes de forma dinâmica por CPF ou Nome.
        
        Args:
            termo_busca: CPF ou Nome (parcial)
            limite: Número máximo de resultados (padrão: 20)
            offset: Deslocamento para paginação
            conn: conexão reutilizável opcional
        
        Returns:
            Lista de pacientes formatados
        """
        return PacienteService.buscar_por_cpf_ou_nome(
            clinica_id=None,
            termo_busca=termo_busca,
            limite=limite,
            offset=offset,
            conn=conn
        )

    @staticmethod
    def contar_pacientes_busca(termo_busca):
        """
        Conta total de pacientes que correspondem ao termo de busca.
        
        Args:
            termo_busca: CPF ou Nome (parcial)
        
        Returns:
            Total de pacientes encontrados
        """
        return PacienteService.contar_por_busca(termo_busca)

    @staticmethod
    def obter_paciente_formatado(paciente_tupla):
        """
        Formata um paciente para exibição.
        
        Args:
            paciente_tupla: Tupla retornada do serviço
        
        Returns:
            String formatada "Nome (CPF)"
        """
        return PacienteService.formatar_exibicao(paciente_tupla)

    @staticmethod
    def extrair_id_paciente(display_text, termo_original):
        """
        Extrai ID do paciente a partir do texto de exibição.
        """
        return PacienteService.extrair_id_de_display(display_text, termo_original)

    @staticmethod
    def listar_medicos_por_clinica(clinica_id):
        """
        Lista todos os médicos de uma clínica com especialidades.
        
        Args:
            clinica_id: ID da clínica
        
        Returns:
            Lista de tuplas (id, nome, especialidades_str, especialidade_ids)
        """
        return MedicoService.listar_por_clinica(clinica_id)

    @staticmethod
    def carregar_medicos_por_especialidade(especialidade_id, clinica_id=None, conn=None):
        """
        Carrega os médicos vinculados à especialidade selecionada.

        Args:
            especialidade_id: ID da especialidade selecionada
            clinica_id: ID da clínica (opcional)
            conn: conexão reutilizável opcional

        Returns:
            Lista de tuplas (id_medico, nome_medico)
        """
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()

            if clinica_id is not None:
                cursor.execute("""
                    SELECT m.id, m.nome
                    FROM odontoPro_medico m
                    JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id
                    WHERE me.especialidade_id = %s
                      AND m.clinica_id = %s
                      AND m.ativo = 1
                    ORDER BY m.nome ASC
                """, (especialidade_id, clinica_id))
                return cursor.fetchall() or []

            cursor.execute("""
                SELECT m.id, m.nome
                FROM odontoPro_medico m
                JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id
                WHERE me.especialidade_id = %s
                  AND m.ativo = 1
                ORDER BY m.nome ASC
            """, (especialidade_id,))
            return cursor.fetchall() or []
        except Exception as e:
            print(f"[ConsultaController] Erro em carregar_medicos_por_especialidade: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def carregar_datas_disponiveis(medico_id, clinica_id=None, conn=None):
        return ConsultaService.carregar_datas_disponiveis(medico_id, clinica_id, conn=conn)

    @staticmethod
    def carregar_horarios_disponiveis(medico_id, data_consulta, clinica_id=None, conn=None, excluir_consulta_id=None):
        return ConsultaService.carregar_horarios_disponiveis(
            medico_id,
            data_consulta,
            clinica_id,
            conn=conn,
            excluir_consulta_id=excluir_consulta_id,
        )

    @staticmethod
    def carregar_disponibilidade_medico(medico_id, clinica_id=None, conn=None):
        return ConsultaService.carregar_disponibilidade_medico(medico_id, clinica_id, conn=conn)

    @staticmethod
    def carregar_disponibilidade_medico_por_data(medico_id, conn=None):
        return ConsultaService.carregar_disponibilidade_medico_por_data(medico_id, conn=conn)

    @staticmethod
    def carregar_agenda_disponivel(medico_id, clinica_id=None, dias_ahead=60, conn=None, excluir_consulta_id=None, somente_disponibilidade_medico=False):
        return ConsultaService.carregar_agenda_disponivel(
            medico_id,
            clinica_id=clinica_id,
            dias_ahead=dias_ahead,
            conn=conn,
            excluir_consulta_id=excluir_consulta_id,
            somente_disponibilidade_medico=somente_disponibilidade_medico,
        )

    @staticmethod
    def marcar_consultas_pendentes_como_falta(clinica_id):
        return ConsultaService.marcar_consultas_pendentes_como_falta(clinica_id)

    @staticmethod
    def obter_medico_formatado(medico_tupla):
        """
        Formata um médico para exibição.
        
        Args:
            medico_tupla: Tupla retornada do serviço
        
        Returns:
            String formatada "Nome - Especialidade(s)"
        """
        return MedicoService.formatar_exibicao(medico_tupla)

    @staticmethod
    def extrair_id_medico(display_text, clinica_id):
        """
        Extrai ID do médico a partir do texto de exibição.
        """
        return MedicoService.extrair_id_de_display(display_text, clinica_id)

    @staticmethod
    def obter_especialidade_medico(medico_id):
        """
        Obtém a especialidade principal de um médico.
        
        Args:
            medico_id: ID do médico
        
        Returns:
            Nome da especialidade principal ou string vazia
        """
        return MedicoService.obter_especialidade_principal(medico_id)

    @staticmethod
    def validar_data_consulta(data_str):
        """
        Valida data da consulta.
        
        Args:
            data_str: Data em formato DD/MM/YYYY
        
        Returns:
            Tupla (válido: bool, mensagem: str, data_obj: datetime ou None)
        """
        return ConsultaService.validar_data(data_str)

    @staticmethod
    def validar_hora_consulta(hora_str):
        """
        Valida hora da consulta.
        
        Args:
            hora_str: Hora em formato HH:MM
        
        Returns:
            Tupla (válido: bool, mensagem: str, hora_obj: time ou None)
        """
        return ConsultaService.validar_hora(hora_str)

    @staticmethod
    def verificar_disponibilidade_horario(medico_id, data_consulta, hora_consulta, conn=None):
        """
        Verifica se um horário está disponível.
        
        Args:
            medico_id: ID do médico
            data_consulta: datetime.date object
            hora_consulta: datetime.time object
            conn: conexão reutilizável opcional
        
        Returns:
            Tupla (disponível: bool, mensagem: str)
        """
        return ConsultaService.verificar_horario_disponivel(
            medico_id, 
            data_consulta, 
            hora_consulta,
            conn=conn
        )

    @staticmethod
    def salvar_disponibilidade_medico(medico_id, disponibilidade_por_dia, clinica_id=None):
        """
        Salva a disponibilidade de um médico.
        
        Args:
            medico_id: ID do médico
            disponibilidade_por_dia: dicionário {weekday_int: [horarios]}
            clinica_id: ID da clínica (opcional)

        Returns:
            Dicionário com resultado {'sucesso': bool, 'mensagem': str}
        """
        return ConsultaService.salvar_disponibilidade_medico(
            medico_id,
            disponibilidade_por_dia,
            clinica_id=clinica_id
        )

    @staticmethod
    def obter_horarios_ocupados(medico_id, data_consulta):
        """
        Lista horários ocupados de um médico em um dia.
        
        Args:
            medico_id: ID do médico
            data_consulta: datetime.date object
        
        Returns:
            Lista de horários (HH:MM) ocupados
        """
        return ConsultaService.listar_horarios_ocupados_no_dia(medico_id, data_consulta)

    @staticmethod
    def salvar_nova_consulta(clinica_id, paciente_id, medico_id, data_hora, 
                             especialidade, status='agendada', observacoes='', especialidade_id=None):
        """
        Salva uma nova consulta com transação e todas as validações.
        
        Args:
            clinica_id: ID da clínica
            paciente_id: ID do paciente
            medico_id: ID do médico
            data_hora: datetime object
            especialidade: Nome da especialidade
            status: Status da consulta (padrão: 'agendada')
            observacoes: Observações adicionais
        
        Returns:
            Dicionário com resultado {'sucesso': bool, 'mensagem': str, 'consulta_id': int ou None, 'erro': str ou None}
        """
        return ConsultaService.criar_consulta(
            clinica_id,
            paciente_id,
            medico_id,
            data_hora,
            especialidade,
            status,
            observacoes,
            especialidade_id=especialidade_id
        )