"""
Service para operações com Consultas.
Validações, verificação de conflitos e transações.
"""

from config.database import get_connection
from datetime import datetime, date, timedelta
import mysql.connector


class ConsultaService:
    """Serviço centralizado para operações com consultas"""

    @staticmethod
    def validar_data(data_str):
        """
        Valida se uma data está no formato correto e não é passada.
        
        Args:
            data_str: Data em formato DD/MM/YYYY
        
        Returns:
            Tupla (válido: bool, mensagem: str, data_obj: datetime ou None)
        """
        try:
            data_obj = datetime.strptime(data_str, "%d/%m/%Y")
            
            # Verificar se a data é hoje ou futura
            hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if data_obj.date() < hoje.date():
                return False, "A data da consulta não pode ser no passado.", None
            
            return True, "Data válida", data_obj
        
        except ValueError:
            return False, "Formato de data inválido. Use DD/MM/YYYY", None

    @staticmethod
    def validar_hora(hora_str):
        """
        Valida se uma hora está no formato correto.
        
        Args:
            hora_str: Hora em formato HH:MM
        
        Returns:
            Tupla (válido: bool, mensagem: str, hora_obj: time ou None)
        """
        try:
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
            return True, "Hora válida", hora_obj
        
        except ValueError:
            return False, "Formato de hora inválido. Use HH:MM", None

    @staticmethod
    def verificar_horario_disponivel(medico_id, data_consulta, hora_consulta):
        """
        Verifica se um horário está disponível para um médico em uma data específica.
        
        Args:
            medico_id: ID do médico
            data_consulta: datetime.date object
            hora_consulta: datetime.time object
        
        Returns:
            Tupla (disponível: bool, mensagem: str)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Procurar por conflitos de horário (mesma hora no mesmo dia)
            query = """
                SELECT COUNT(*) as total
                FROM odontoPro_consulta
                WHERE 
                    medico_id = %s
                    AND DATE(data_hora) = %s
                    AND TIME(data_hora) = %s
                    AND status != 'cancelada'
            """

            cursor.execute(query, (medico_id, data_consulta, hora_consulta))
            resultado = cursor.fetchone()
            total_conflitos = resultado[0] if resultado else 0

            if total_conflitos > 0:
                return False, "Este horário já está reservado para este médico."

            return True, "Horário disponível"

        except Exception as e:
            print(f"[ConsultaService] Erro em verificar_horario_disponivel: {e}")
            return False, f"Erro ao verificar horário: {str(e)}"

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def listar_horarios_ocupados_no_dia(medico_id, data_consulta):
        """
        Lista todos os horários ocupados de um médico em um dia específico.
        
        Args:
            medico_id: ID do médico
            data_consulta: datetime.date object
        
        Returns:
            Lista de horários (HH:MM) ocupados
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT TIME_FORMAT(data_hora, '%H:%i') as hora
                FROM odontoPro_consulta
                WHERE 
                    medico_id = %s
                    AND DATE(data_hora) = %s
                    AND status != 'cancelada'
                ORDER BY hora ASC
            """

            cursor.execute(query, (medico_id, data_consulta))
            resultados = cursor.fetchall()
            
            horarios = [r[0] for r in resultados] if resultados else []
            return horarios

        except Exception as e:
            print(f"[ConsultaService] Erro em listar_horarios_ocupados_no_dia: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _converter_dia_para_weekday(dia):
        if dia is None:
            return None

        if isinstance(dia, int):
            if 0 <= dia <= 6:
                return dia
            if 1 <= dia <= 7:
                return dia - 1
            return None

        if isinstance(dia, str):
            valor = dia.strip().lower()
            mapping = {
                'segunda': 0,
                'terca': 1,
                'terça': 1,
                'quarta': 2,
                'quinta': 3,
                'sexta': 4,
                'sabado': 5,
                'sábado': 5,
                'domingo': 6,
            }

            if valor in mapping:
                return mapping[valor]

            if valor.isdigit():
                numero = int(valor)
                if 0 <= numero <= 6:
                    return numero
                if 1 <= numero <= 7:
                    return numero - 1

        return None

    @staticmethod
    def _parse_hora(hora_valor):
        if hora_valor is None:
            return None

        if isinstance(hora_valor, str):
            try:
                return datetime.strptime(hora_valor, "%H:%M").time()
            except ValueError:
                return None

        if isinstance(hora_valor, timedelta):
            total_seconds = int(hora_valor.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").time()

        return None

    @staticmethod
    def _gerar_horarios_por_intervalo(inicio, fim, intervalo_minutos=30):
        if not inicio or not fim:
            return []

        horarios = []
        atual = inicio
        while datetime.combine(date.today(), atual) + timedelta(minutes=intervalo_minutos) <= datetime.combine(date.today(), fim):
            horarios.append(atual.strftime("%H:%M"))
            atual = (datetime.combine(date.today(), atual) + timedelta(minutes=intervalo_minutos)).time()
        return horarios

    @staticmethod
    def _listar_horarios_abertos_do_medico(medico_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dia, TIME_FORMAT(hora_inicio, '%H:%i'), TIME_FORMAT(hora_fim, '%H:%i')
                FROM odontoPro_medicohorario
                WHERE medico_id = %s
            """, (medico_id,))

            resultados = cursor.fetchall() or []
            horarios = {}
            for dia, inicio, fim in resultados:
                weekday = ConsultaService._converter_dia_para_weekday(dia)
                if weekday is None or not inicio or not fim:
                    continue
                horarios.setdefault(weekday, []).append((inicio, fim))
            return horarios
        except Exception as e:
            print(f"[ConsultaService] Erro em _listar_horarios_abertos_do_medico: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _listar_horarios_abertos_por_clinica(clinica_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT d.dia, TIME_FORMAT(h.hora_inicio, '%H:%i'), TIME_FORMAT(h.hora_fim, '%H:%i')
                FROM odontoPro_horarioaberto h
                JOIN odontoPro_diasemanadisponivel d ON d.id = h.dia_id
                WHERE d.clinica_id = %s
            """, (clinica_id,))

            resultados = cursor.fetchall() or []
            horarios = {}
            for dia, inicio, fim in resultados:
                weekday = ConsultaService._converter_dia_para_weekday(dia)
                if weekday is None or not inicio or not fim:
                    continue
                horarios.setdefault(weekday, []).append((inicio, fim))
            return horarios
        except Exception as e:
            print(f"[ConsultaService] Erro em _listar_horarios_abertos_por_clinica: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _obter_clinica_do_medico(medico_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT clinica_id FROM odontoPro_medico WHERE id = %s", (medico_id,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"[ConsultaService] Erro em _obter_clinica_do_medico: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def carregar_horarios_disponiveis(medico_id, data_consulta, clinica_id=None):
        if not medico_id or not data_consulta:
            return []

        if isinstance(data_consulta, datetime):
            data_consulta = data_consulta.date()

        if not isinstance(data_consulta, date):
            return []

        horarios_por_dia = ConsultaService._listar_horarios_abertos_do_medico(medico_id)
        if not horarios_por_dia:
            if clinica_id is None:
                clinica_id = ConsultaService._obter_clinica_do_medico(medico_id)
            if clinica_id is None:
                return []
            horarios_por_dia = ConsultaService._listar_horarios_abertos_por_clinica(clinica_id)

        intervalos = horarios_por_dia.get(data_consulta.weekday(), [])
        if not intervalos:
            return []

        horarios = []
        for inicio, fim in intervalos:
            inicio_obj = ConsultaService._parse_hora(inicio)
            fim_obj = ConsultaService._parse_hora(fim)
            horarios.extend(ConsultaService._gerar_horarios_por_intervalo(inicio_obj, fim_obj))

        horarios = sorted(set(horarios))
        horarios_ocupados = ConsultaService.listar_horarios_ocupados_no_dia(medico_id, data_consulta)

        if data_consulta == date.today():
            agora = datetime.now().time()
            horarios = [h for h in horarios if datetime.strptime(h, "%H:%M").time() > agora]

        return [h for h in horarios if h not in horarios_ocupados]

    @staticmethod
    def carregar_datas_disponiveis(medico_id, clinica_id=None, dias_ahead=30):
        if not medico_id:
            return []

        horarios_por_dia = ConsultaService._listar_horarios_abertos_do_medico(medico_id)
        if not horarios_por_dia:
            if clinica_id is None:
                clinica_id = ConsultaService._obter_clinica_do_medico(medico_id)
            if clinica_id is None:
                return []
            horarios_por_dia = ConsultaService._listar_horarios_abertos_por_clinica(clinica_id)

        if not horarios_por_dia:
            return []

        hoje = date.today()
        datas_disponiveis = []
        for offset in range(dias_ahead + 1):
            data_candidata = hoje + timedelta(days=offset)
            if data_candidata.weekday() not in horarios_por_dia:
                continue

            horarios = ConsultaService.carregar_horarios_disponiveis(medico_id, data_candidata, clinica_id)
            if horarios:
                datas_disponiveis.append(data_candidata.strftime("%d/%m/%Y"))

        return datas_disponiveis

    @staticmethod
    def criar_consulta(clinica_id, paciente_id, medico_id, data_hora, especialidade, 
                       status='agendada', observacoes='', especialidade_id=None):
        """
        Cria uma nova consulta no banco com transação.
        
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
        conn = None
        cursor = None
        
        try:
            # Validações básicas
            if not all([clinica_id, paciente_id, medico_id, data_hora]):
                return {
                    'sucesso': False,
                    'mensagem': 'Campos obrigatórios não preenchidos.',
                    'consulta_id': None,
                    'erro': 'Campos vazios'
                }

            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Verificar se paciente existe E OBTER SEUS DADOS (nome, email, telefone)
            cursor.execute("SELECT id, nome, email, telefone FROM odontoPro_paciente WHERE id = %s", (paciente_id,))
            paciente_data = cursor.fetchone()
            if not paciente_data:
                conn.close()
                return {
                    'sucesso': False,
                    'mensagem': 'Paciente não encontrado.',
                    'consulta_id': None,
                    'erro': 'Paciente inválido'
                }
            
            # Extrair dados do paciente
            nome_paciente = paciente_data['nome'] or ''
            email_paciente = paciente_data['email'] or ''
            telefone_paciente = paciente_data['telefone'] or ''
            
            # ✓ VALIDAÇÃO: Garantir que os dados do paciente não estão vazios
            if not nome_paciente:
                return {
                    'sucesso': False,
                    'mensagem': 'Dados do paciente incompletos (nome ausente).',
                    'consulta_id': None,
                    'erro': 'Paciente sem nome'
                }
            
            if not email_paciente:
                return {
                    'sucesso': False,
                    'mensagem': 'Dados do paciente incompletos (email ausente).',
                    'consulta_id': None,
                    'erro': 'Paciente sem email'
                }
            
            if not telefone_paciente:
                return {
                    'sucesso': False,
                    'mensagem': 'Dados do paciente incompletos (telefone ausente).',
                    'consulta_id': None,
                    'erro': 'Paciente sem telefone'
                }

            # Verificar se médico existe e pertence à clínica
            cursor.execute(
                "SELECT id FROM odontoPro_medico WHERE id = %s AND clinica_id = %s",
                (medico_id, clinica_id)
            )
            if not cursor.fetchone():
                conn.close()
                return {
                    'sucesso': False,
                    'mensagem': 'Médico não encontrado ou não pertence a esta clínica.',
                    'consulta_id': None,
                    'erro': 'Médico inválido'
                }

            especialidade_nome = especialidade
            if especialidade_id is not None:
                cursor.execute(
                    "SELECT id, nome FROM odontoPro_especialidade WHERE id = %s",
                    (especialidade_id,)
                )
                especialidade_db = cursor.fetchone()
                if not especialidade_db:
                    return {
                        'sucesso': False,
                        'mensagem': 'Especialidade não encontrada.',
                        'consulta_id': None,
                        'erro': 'Especialidade inválida'
                    }
                especialidade_nome = especialidade_db['nome']

            # Verificar conflito de horário
            disponivel, msg_horario = ConsultaService.verificar_horario_disponivel(
                medico_id, 
                data_hora.date(), 
                data_hora.time()
            )

            if not disponivel:
                conn.close()
                return {
                    'sucesso': False,
                    'mensagem': msg_horario,
                    'consulta_id': None,
                    'erro': 'Horário ocupado'
                }

            # Inserir consulta com todos os campos obrigatórios
            from datetime import datetime
            criado_em = datetime.now()
            
            # Criar um novo cursor sem dictionary para verificar colunas (índices numéricos)
            cursor_cols = conn.cursor()
            cursor_cols.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'odontoPro_consulta'")
            colunas_consulta = [row[0].lower() for row in cursor_cols.fetchall()]
            cursor_cols.close()

            if 'especialidade_id' in colunas_consulta:
                query = """
                    INSERT INTO odontoPro_consulta 
                    (clinica_id, paciente_id, medico_id, especialidade_id, data_hora, status, observacoes, 
                     nome, email, telefone, criado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    clinica_id,
                    paciente_id,
                    medico_id,
                    especialidade_id,
                    data_hora,
                    status.lower(),
                    observacoes,
                    nome_paciente,
                    email_paciente,
                    telefone_paciente,
                    criado_em
                ))
            else:
                query = """
                    INSERT INTO odontoPro_consulta 
                    (clinica_id, paciente_id, medico_id, data_hora, status, observacoes, 
                     nome, email, telefone, criado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    clinica_id,
                    paciente_id,
                    medico_id,
                    data_hora,
                    status.lower(),
                    observacoes,
                    nome_paciente,
                    email_paciente,
                    telefone_paciente,
                    criado_em
                ))

            consulta_id = cursor.lastrowid

            if consulta_id:
                print(f"[ConsultaService] ✓ Consulta criada com sucesso. ID: {consulta_id}")
                return {
                    'sucesso': True,
                    'mensagem': 'Consulta marcada com sucesso!',
                    'consulta_id': consulta_id,
                    'erro': None
                }
            else:
                return {
                    'sucesso': False,
                    'mensagem': 'Erro ao salvar consulta no banco.',
                    'consulta_id': None,
                    'erro': 'Erro de insert'
                }

        except mysql.connector.Error as e:
            print(f"[ConsultaService] Erro MySQL em criar_consulta: {e}")
            return {
                'sucesso': False,
                'mensagem': f'Erro ao salvar no banco: {str(e)}',
                'consulta_id': None,
                'erro': str(e)
            }

        except Exception as e:
            print(f"[ConsultaService] Erro geral em criar_consulta: {e}")
            import traceback
            traceback.print_exc()
            return {
                'sucesso': False,
                'mensagem': f'Erro inesperado: {str(e)}',
                'consulta_id': None,
                'erro': str(e)
            }

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def buscar_por_id(consulta_id):
        """
        Busca uma consulta específica pelo ID.
        
        Args:
            consulta_id: ID da consulta
        
        Returns:
            Tupla completa ou None
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT 
                    c.id, p.nome, c.data_hora, c.status, p.telefone, p.email,
                    p.sexo, p.data_nascimento, p.cpf, p.foto, c.observacoes,
                    m.nome AS medico_nome, 
                    COALESCE((
                        SELECT GROUP_CONCAT(e.nome SEPARATOR ', ')
                        FROM odontoPro_medico_especialidades me
                        JOIN odontoPro_especialidade e ON me.especialidade_id = e.id
                        WHERE me.medico_id = m.id
                    ), '') AS especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                WHERE c.id = %s
            """

            cursor.execute(query, (consulta_id,))
            consulta = cursor.fetchone()
            return consulta

        except Exception as e:
            print(f"[ConsultaService] Erro em buscar_por_id: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
