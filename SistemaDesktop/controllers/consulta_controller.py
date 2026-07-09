from config.database import get_connection
from models.data import LIMITE_CONSULTAS
from services.paciente_service import PacienteService
from services.medico_service import MedicoService
from services.consulta_service import ConsultaService

class ConsultaController:

    @staticmethod
    def _build_filters(clinica_id, data=None, status=None, medico=None, especialidade=None):
        where = ["c.clinica_id = %s"]
        params = [clinica_id]

        if data and data not in ['Todos', 'Data']:
            where.append("DATE(c.data_hora) = %s")
            params.append(data)

        if status and status not in ['Todos', 'Status']:
            where.append("LOWER(c.status) = %s")
            params.append(status.lower())

        if medico and medico not in ['Todos', 'Médico']:
            where.append("m.nome = %s")
            params.append(medico)

        if especialidade and especialidade not in ['Todos', 'Especialidade']:
            where.append("EXISTS ("
                         "SELECT 1 FROM odontoPro_medico_especialidades me "
                         "JOIN odontoPro_especialidade e ON me.especialidade_id = e.id "
                         "WHERE me.medico_id = c.medico_id AND LOWER(e.nome) = %s)")
            params.append(especialidade.lower())

        return " AND ".join(where), params

    @staticmethod
    def listar_por_clinica(clinica_id, pagina=0, limite=LIMITE_CONSULTAS, data=None, status=None, medico=None, especialidade=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            where_clause, params = ConsultaController._build_filters(clinica_id, data, status, medico, especialidade)

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
                WHERE {where_clause}
                ORDER BY c.data_hora DESC
                LIMIT %s OFFSET %s
            """

            params.extend([limite, pagina * limite])
            cursor.execute(query, tuple(params))
            dados = cursor.fetchall()
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
    def contar_por_clinica(clinica_id, data=None, status=None, medico=None, especialidade=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            where_clause, params = ConsultaController._build_filters(clinica_id, data, status, medico, especialidade)

            cursor.execute(f"""
                SELECT COUNT(*)
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
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
                SELECT DISTINCT DATE(c.data_hora), m.nome, e.nome AS especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                LEFT JOIN odontoPro_medico_especialidades me ON me.medico_id = m.id
                LEFT JOIN odontoPro_especialidade e ON me.especialidade_id = e.id
                WHERE c.clinica_id = %s
                ORDER BY DATE(c.data_hora) DESC, m.nome ASC, e.nome ASC
            """, (clinica_id,))

            resultados = cursor.fetchall() or []

            datas = sorted({r[0] for r in resultados if r[0]}, reverse=True)
            medicos = sorted({r[1] for r in resultados if r[1]})
            especialidades = sorted({r[2] for r in resultados if r[2]})

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
    def buscar_por_id(consulta_id):
        conn = get_connection()
        cursor = conn.cursor()

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
    def snapshot_por_clinica(clinica_id, data=None, status=None, medico=None, especialidade=None):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            where_clause, params = ConsultaController._build_filters(clinica_id, data, status, medico, especialidade)

            cursor.execute(f"""
                SELECT CONCAT(COUNT(*), '-', IFNULL(MAX(c.id), 0), '-', IFNULL(MIN(c.id), 0), '-', COALESCE(MAX(UNIX_TIMESTAMP(c.data_hora)), 0))
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
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
    def listar_especialidades():
        """Lista todas as especialidades odontológicas"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome
            FROM odontoPro_especialidade
            ORDER BY nome ASC
        """)
        
        especialidades = cursor.fetchall()
        conn.close()
        return especialidades

    @staticmethod
    def criar_consulta(clinica_id, paciente_id, medico_id, data_hora, status='agendada', especialidade='', observacoes=''):
        """Cria uma nova consulta"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO odontoPro_consulta 
                (clinica_id, paciente_id, medico_id, data_hora, status, especialidade, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (clinica_id, paciente_id, medico_id, data_hora, status, especialidade, observacoes))
            
            conn.commit()
            consulta_id = cursor.lastrowid
            conn.close()
            
            return {"sucesso": True, "consulta_id": consulta_id}
        except Exception as e:
            return {"sucesso": False, "erro": str(e)}

    # ==================== NOVOS MÉTODOS COM SERVICES ====================

    @staticmethod
    def buscar_pacientes_dinamico(termo_busca, limite=10, offset=0):
        """
        Busca pacientes de forma dinâmica por CPF ou Nome.
        
        Args:
            termo_busca: CPF ou Nome (parcial)
            limite: Número máximo de resultados
            offset: Deslocamento para paginação
        
        Returns:
            Lista de pacientes formatados
        """
        return PacienteService.buscar_por_cpf_ou_nome(
            clinica_id=None,
            termo_busca=termo_busca,
            limite=limite,
            offset=offset
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
    def verificar_disponibilidade_horario(medico_id, data_consulta, hora_consulta):
        """
        Verifica se um horário está disponível.
        
        Args:
            medico_id: ID do médico
            data_consulta: datetime.date object
            hora_consulta: datetime.time object
        
        Returns:
            Tupla (disponível: bool, mensagem: str)
        """
        return ConsultaService.verificar_horario_disponivel(
            medico_id, 
            data_consulta, 
            hora_consulta
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
                             especialidade, status='agendada', observacoes=''):
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
            observacoes
        )