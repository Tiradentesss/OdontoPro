"""
Service para operações com Consultas.
Validações, verificação de conflitos e transações.
"""

from config.database import get_connection
from datetime import datetime, date, timedelta
import mysql.connector
from services.query_logger import timed_sql
from services.especialidade_service import EspecialidadeService


class ConsultaService:
    """Serviço centralizado para operações com consultas"""

    @staticmethod
    def validar_data(data_str):
        """
        Valida se uma data está no formato correto e não é passada.
        
        Parâmetros:
            data_str: Data em formato DD/MM/YYYY
        
        Retorna:
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
        
        Parâmetros:
            hora_str: Hora em formato HH:MM
        
        Retorna:
            Tupla (válido: bool, mensagem: str, hora_obj: time ou None)
        """
        try:
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
            return True, "Hora válida", hora_obj
        
        except ValueError:
            return False, "Formato de hora inválido. Use HH:MM", None

    @staticmethod
    def verificar_horario_disponivel(medico_id, data_consulta, hora_consulta, conn=None):
        """
        Verifica se um horário está disponível para um médico em uma data específica.
        
        Parâmetros:
            medico_id: ID do médico
            data_consulta: datetime.date object
            hora_consulta: datetime.time object
            conn: conexão reutilizável opcional
        
        Retorna:
            Tupla (disponível: bool, mensagem: str)
        """
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()

            query = """
                SELECT COUNT(*) as total
                FROM odontoPro_consulta
                WHERE 
                    medico_id = %s
                    AND DATE(data_hora) = %s
                    AND TIME_FORMAT(data_hora, '%H:%i') = %s
                    AND status != 'cancelada'
                    AND clinica_id = (
                        SELECT clinica_id FROM odontoPro_medico WHERE id = %s
                    )
            """

            def _exec():
                hora_str = hora_consulta.strftime('%H:%M') if hasattr(hora_consulta, 'strftime') else str(hora_consulta)[:5]
                cursor.execute(query, (medico_id, data_consulta, hora_str, medico_id))
                return cursor.fetchone()

            resultado = timed_sql("verificar_horario_disponivel", _exec, sql=query)
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
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def listar_horarios_ocupados_no_dia(medico_id, data_consulta, conn=None, excluir_consulta_id=None):
        """
        Lista todos os horários ocupados de um médico em um dia específico.
        
        Parâmetros:
            medico_id: ID do médico
            data_consulta: datetime.date object
            conn: conexão reutilizável opcional
        
        Retorna:
            Lista de horários (HH:MM) ocupados
        """
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()

            query = """
                SELECT TIME_FORMAT(data_hora, '%H:%i') as hora
                FROM odontoPro_consulta
                WHERE 
                    medico_id = %s
                    AND DATE(data_hora) = %s
                    AND status != 'cancelada'
                    AND clinica_id = (
                        SELECT clinica_id FROM odontoPro_medico WHERE id = %s
                    )
                ORDER BY hora ASC
            """

            if excluir_consulta_id is not None:
                query = query.replace("                ORDER BY hora ASC", "                AND id != %s\n                ORDER BY hora ASC")

            def _exec():
                params = (medico_id, data_consulta, medico_id)
                if excluir_consulta_id is not None:
                    params += (excluir_consulta_id,)
                cursor.execute(query, params)
                return cursor.fetchall()

            resultados = timed_sql("listar_horarios_ocupados_no_dia", _exec, sql=query) or []
            
            horarios = [r[0] for r in resultados] if resultados else []
            return horarios

        except Exception as e:
            print(f"[ConsultaService] Erro em listar_horarios_ocupados_no_dia: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
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
    def _listar_horarios_abertos_do_medico(medico_id, conn=None):
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()
            def _exec():
                cursor.execute("""
                    SELECT dia, TIME_FORMAT(hora_inicio, '%H:%i'), TIME_FORMAT(hora_fim, '%H:%i')
                    FROM odontoPro_medicohorario
                    WHERE medico_id = %s
                """, (medico_id,))
                return cursor.fetchall()

            resultados = timed_sql("_listar_horarios_abertos_do_medico", _exec, sql="SELECT dia, hora_inicio, hora_fim FROM odontoPro_medicohorario WHERE medico_id = %s") or []
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
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def _listar_horarios_abertos_por_clinica(clinica_id, conn=None):
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()
            def _exec():
                cursor.execute("""
                    SELECT d.dia, TIME_FORMAT(h.hora_inicio, '%H:%i'), TIME_FORMAT(h.hora_fim, '%H:%i')
                    FROM odontoPro_horarioaberto h
                    JOIN odontoPro_diasemanadisponivel d ON d.id = h.dia_id
                    WHERE d.clinica_id = %s
                """, (clinica_id,))
                return cursor.fetchall()

            resultados = timed_sql("_listar_horarios_abertos_por_clinica", _exec, sql="SELECT d.dia, h.hora_inicio, h.hora_fim FROM odontoPro_horarioaberto JOIN odontoPro_diasemanadisponivel WHERE clinica_id = %s") or []
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
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def carregar_disponibilidade_medico(medico_id, clinica_id=None, conn=None):
        """Retorna os horários cadastrados do médico agrupados por dia da semana."""
        if not medico_id:
            return {}

        horarios_por_dia = ConsultaService._listar_horarios_abertos_do_medico(
            medico_id,
            conn=conn
        )
        disponibilidade = {}
        for weekday, intervalos in horarios_por_dia.items():
            horarios = []
            for inicio, fim in intervalos:
                inicio_obj = ConsultaService._parse_hora(inicio)
                fim_obj = ConsultaService._parse_hora(fim)
                horarios.extend(
                    ConsultaService._gerar_horarios_por_intervalo(inicio_obj, fim_obj)
                )
            disponibilidade[weekday] = sorted(set(horarios))
        return disponibilidade

    @staticmethod
    def carregar_disponibilidade_medico_por_data(medico_id, conn=None):
        """Retorna os horários cadastrados do médico agrupados por data específica."""
        if not medico_id:
            return {}

        disponibilidade = {}
        for data_disponivel, intervalos in ConsultaService._listar_disponibilidade_por_data_do_medico(medico_id, conn=conn).items():
            horarios = []
            for inicio, fim in intervalos:
                inicio_obj = ConsultaService._parse_hora(inicio)
                fim_obj = ConsultaService._parse_hora(fim)
                horarios.extend(ConsultaService._gerar_horarios_por_intervalo(inicio_obj, fim_obj))
            if horarios:
                disponibilidade[data_disponivel] = sorted(set(horarios))

        return disponibilidade

    @staticmethod
    def _listar_disponibilidade_por_data_do_medico(medico_id, conn=None):
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()
            cursor.execute("""
                SELECT data, TIME_FORMAT(hora_inicio, '%H:%i'), TIME_FORMAT(hora_fim, '%H:%i')
                FROM odontoPro_medicohorario_data
                WHERE medico_id = %s
                ORDER BY data ASC, hora_inicio ASC
            """, (medico_id,))

            disponibilidade = {}
            for data_disponivel, inicio, fim in cursor.fetchall() or []:
                if isinstance(data_disponivel, datetime):
                    data_disponivel = data_disponivel.date()
                if isinstance(data_disponivel, date) and inicio and fim:
                    disponibilidade.setdefault(data_disponivel, []).append((inicio, fim))
            return disponibilidade
        except Exception as e:
            print(f"[ConsultaService] Erro ao carregar disponibilidade por data: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def _converter_weekday_para_dia(weekday):
        mapping = {
            0: 'Segunda',
            1: 'Terça',
            2: 'Quarta',
            3: 'Quinta',
            4: 'Sexta',
            5: 'Sábado',
            6: 'Domingo'
        }
        return mapping.get(weekday)

    @staticmethod
    def _agrupar_horarios_em_intervalos(horarios):
        if not horarios:
            return []

        def to_minutes(hora_str):
            parts = hora_str.split(':')
            return int(parts[0]) * 60 + int(parts[1])

        horas_ordenadas = sorted(set(horarios), key=to_minutes)
        intervalos = []
        inicio_atual = horas_ordenadas[0]
        fim_atual = horas_ordenadas[0]

        for horario in horas_ordenadas[1:]:
            prev_minutos = to_minutes(fim_atual)
            atual_minutos = to_minutes(horario)
            if atual_minutos == prev_minutos + 30:
                fim_atual = horario
            else:
                fim_str = (datetime.strptime(fim_atual, '%H:%M') + timedelta(minutes=30)).strftime('%H:%M')
                intervalos.append((inicio_atual, fim_str))
                inicio_atual = horario
                fim_atual = horario

        fim_str = (datetime.strptime(fim_atual, '%H:%M') + timedelta(minutes=30)).strftime('%H:%M')
        intervalos.append((inicio_atual, fim_str))
        return intervalos

    @staticmethod
    def salvar_disponibilidade_medico(medico_id, disponibilidade_por_dia, clinica_id=None):
        if not medico_id:
            return {'sucesso': False, 'mensagem': 'Médico não informado.'}

        if not disponibilidade_por_dia:
            return {'sucesso': False, 'mensagem': 'Nenhuma disponibilidade selecionada.'}

        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if clinica_id is not None:
                cursor.execute(
                    "SELECT id FROM odontoPro_medico WHERE id = %s AND clinica_id = %s",
                    (medico_id, clinica_id)
                )
            else:
                cursor.execute(
                    "SELECT id FROM odontoPro_medico WHERE id = %s",
                    (medico_id,)
                )

            if not cursor.fetchone():
                return {
                    'sucesso': False,
                    'mensagem': 'Médico não encontrado ou não pertence a esta clínica.'
                }

            for data_disponivel, horarios in disponibilidade_por_dia.items():
                if horarios is None:
                    continue

                if isinstance(data_disponivel, datetime):
                    data_disponivel = data_disponivel.date()
                if not isinstance(data_disponivel, date):
                    continue

                intervalos = ConsultaService._agrupar_horarios_em_intervalos(horarios)
                if not intervalos:
                    continue

                cursor.execute(
                    "DELETE FROM odontoPro_medicohorario_data WHERE medico_id = %s AND data = %s",
                    (medico_id, data_disponivel)
                )

                for inicio, fim in intervalos:
                    cursor.execute(
                        "INSERT INTO odontoPro_medicohorario_data (medico_id, data, hora_inicio, hora_fim) VALUES (%s, %s, %s, %s)",
                        (medico_id, data_disponivel, inicio, fim)
                    )

            conn.commit()
            return {
                'sucesso': True,
                'mensagem': 'Disponibilidade salva com sucesso.'
            }

        except Exception as e:
            print(f"[ConsultaService] Erro ao salvar disponibilidade do médico: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return {
                'sucesso': False,
                'mensagem': f'Erro ao salvar disponibilidade: {str(e)}'
            }

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def _obter_clinica_do_medico(medico_id, conn=None):
        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True
            cursor = conn.cursor()
            def _exec():
                cursor.execute("SELECT clinica_id FROM odontoPro_medico WHERE id = %s", (medico_id,))
                return cursor.fetchone()

            resultado = timed_sql("_obter_clinica_do_medico", _exec, sql="SELECT clinica_id FROM odontoPro_medico WHERE id = %s")
            return resultado[0] if resultado else None
        except Exception as e:
            print(f"[ConsultaService] Erro em _obter_clinica_do_medico: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def carregar_horarios_disponiveis(medico_id, data_consulta, clinica_id=None, conn=None, excluir_consulta_id=None):
        if not medico_id or not data_consulta:
            return []

        if isinstance(data_consulta, datetime):
            data_consulta = data_consulta.date()

        if not isinstance(data_consulta, date):
            return []

        horarios_por_dia = ConsultaService._listar_horarios_abertos_do_medico(medico_id, conn=conn)
        if not horarios_por_dia:
            if clinica_id is None:
                clinica_id = ConsultaService._obter_clinica_do_medico(medico_id, conn=conn)
            if clinica_id is None:
                return []
            horarios_por_dia = ConsultaService._listar_horarios_abertos_por_clinica(clinica_id, conn=conn)

        intervalos = horarios_por_dia.get(data_consulta.weekday(), [])
        if not intervalos:
            return []

        horarios = []
        for inicio, fim in intervalos:
            inicio_obj = ConsultaService._parse_hora(inicio)
            fim_obj = ConsultaService._parse_hora(fim)
            horarios.extend(ConsultaService._gerar_horarios_por_intervalo(inicio_obj, fim_obj))

        horarios = sorted(set(horarios))
        horarios_ocupados = ConsultaService.listar_horarios_ocupados_no_dia(
            medico_id,
            data_consulta,
            conn=conn,
            excluir_consulta_id=excluir_consulta_id,
        )

        if data_consulta == date.today():
            agora = datetime.now().time()
            horarios = [h for h in horarios if datetime.strptime(h, "%H:%M").time() > agora]

        return [h for h in horarios if h not in horarios_ocupados]

    @staticmethod
    def carregar_datas_disponiveis(medico_id, clinica_id=None, dias_ahead=30, conn=None):
        if not medico_id:
            return []

        horarios_por_dia = ConsultaService._listar_horarios_abertos_do_medico(medico_id, conn=conn)
        if not horarios_por_dia:
            if clinica_id is None:
                clinica_id = ConsultaService._obter_clinica_do_medico(medico_id, conn=conn)
            if clinica_id is None:
                return []
            horarios_por_dia = ConsultaService._listar_horarios_abertos_por_clinica(clinica_id, conn=conn)

        if not horarios_por_dia:
            return []

        hoje = date.today()
        datas_disponiveis = []
        for offset in range(dias_ahead + 1):
            data_candidata = hoje + timedelta(days=offset)
            if data_candidata.weekday() not in horarios_por_dia:
                continue

            horarios = ConsultaService.carregar_horarios_disponiveis(medico_id, data_candidata, clinica_id, conn=conn)
            if horarios:
                datas_disponiveis.append(data_candidata.strftime("%d/%m/%Y"))

        return datas_disponiveis

    @staticmethod
    def carregar_agenda_disponivel(medico_id, clinica_id=None, dias_ahead=60, conn=None, excluir_consulta_id=None, somente_disponibilidade_medico=False):
        """
        Carrega a agenda disponível do médico pelos próximos dias sem consultar a cada troca de data.
        Retorna todas as datas e horários disponíveis em memória.
        """
        if not medico_id:
            return {'datas': [], 'horarios_por_data': {}}

        internal_conn = False
        cursor = None
        try:
            if conn is None:
                conn = get_connection()
                internal_conn = True

            disponibilidade_por_data = {}
            if somente_disponibilidade_medico:
                disponibilidade_por_data = ConsultaService._listar_disponibilidade_por_data_do_medico(medico_id, conn=conn)
                if not disponibilidade_por_data:
                    return {'datas': [], 'horarios_por_data': {}}
                horarios_por_dia = None
            else:
                horarios_por_dia = ConsultaService._listar_horarios_abertos_do_medico(medico_id, conn=conn)
            if not horarios_por_dia and not somente_disponibilidade_medico:
                if clinica_id is None:
                    clinica_id = ConsultaService._obter_clinica_do_medico(medico_id, conn=conn)
                if clinica_id is None:
                    return {'datas': [], 'horarios_por_data': {}}
                horarios_por_dia = ConsultaService._listar_horarios_abertos_por_clinica(clinica_id, conn=conn)

            if not horarios_por_dia and not somente_disponibilidade_medico:
                return {'datas': [], 'horarios_por_data': {}}

            cursor = conn.cursor()
            def _exec():
                # aplicar filtro de clínica quando disponível no escopo (clinica_id)
                if clinica_id is not None:
                    query = '''
                        SELECT DATE(data_hora), TIME(data_hora)
                        FROM odontoPro_consulta
                        WHERE medico_id = %s
                          AND clinica_id = %s
                          AND status != 'cancelada'
                          AND DATE(data_hora) BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                    '''
                    params = (medico_id, clinica_id, dias_ahead)
                else:
                    query = '''
                        SELECT DATE(data_hora), TIME(data_hora)
                        FROM odontoPro_consulta
                        WHERE medico_id = %s
                          AND status != 'cancelada'
                          AND DATE(data_hora) BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
                    '''
                    params = (medico_id, dias_ahead)
                if excluir_consulta_id is not None:
                    query += ' AND id != %s'
                    params += (excluir_consulta_id,)
                cursor.execute(query, params)
                return cursor.fetchall()

            ocupados_rows = timed_sql("carregar_agenda_disponivel - buscar ocupados", _exec, sql="SELECT DATE(data_hora), TIME(data_hora) FROM odontoPro_consulta WHERE medico_id = %s AND DATE(data_hora) BETWEEN ...") or []

            ocupados_por_data = {}
            for data_hora, hora in ocupados_rows or []:
                if not data_hora or not hora:
                    continue
                if hasattr(data_hora, 'strftime'):
                    data_str = data_hora.strftime('%d/%m/%Y')
                else:
                    data_str = str(data_hora)
                if hasattr(hora, 'strftime'):
                    hora_str = hora.strftime('%H:%M')
                else:
                    hora_str = str(hora)[:5]
                ocupados_por_data.setdefault(data_str, set()).add(hora_str)

            hoje = date.today()
            datas = []
            horarios_por_data = {}
            if somente_disponibilidade_medico:
                datas_candidatas = sorted(disponibilidade_por_data)
            else:
                datas_candidatas = [hoje + timedelta(days=offset) for offset in range(dias_ahead + 1)]

            for data_candidata in datas_candidatas:
                if data_candidata < hoje or data_candidata > hoje + timedelta(days=dias_ahead):
                    continue

                if somente_disponibilidade_medico:
                    intervalos = disponibilidade_por_data[data_candidata]
                else:
                    weekday = data_candidata.weekday()
                    if weekday not in horarios_por_dia:
                        continue
                    intervalos = horarios_por_dia[weekday]
                horarios_disponiveis_dia = []
                for inicio, fim in intervalos:
                    inicio_obj = ConsultaService._parse_hora(inicio)
                    fim_obj = ConsultaService._parse_hora(fim)
                    horarios_disponiveis_dia.extend(ConsultaService._gerar_horarios_por_intervalo(inicio_obj, fim_obj))

                horarios_disponiveis_dia = sorted(set(horarios_disponiveis_dia))
                if data_candidata == hoje:
                    agora = datetime.now().time()
                    horarios_disponiveis_dia = [h for h in horarios_disponiveis_dia if datetime.strptime(h, '%H:%M').time() > agora]

                ocupado = ocupados_por_data.get(data_candidata.strftime('%d/%m/%Y'), set())
                horarios_disponiveis_dia = [h for h in horarios_disponiveis_dia if h not in ocupado]

                if horarios_disponiveis_dia:
                    data_str = data_candidata.strftime('%d/%m/%Y')
                    datas.append(data_str)
                    horarios_por_data[data_str] = horarios_disponiveis_dia

            return {'datas': datas, 'horarios_por_data': horarios_por_data}

        except Exception as e:
            print(f"[ConsultaService] Erro em carregar_agenda_disponivel: {e}")
            return {'datas': [], 'horarios_por_data': {}}
        finally:
            if cursor:
                cursor.close()
            if internal_conn and conn:
                conn.close()

    @staticmethod
    def marcar_consultas_pendentes_como_falta(clinica_id):
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE odontoPro_consulta
                SET status = 'falta'
                WHERE clinica_id = %s
                  AND DATE_ADD(data_hora, INTERVAL 1 HOUR) < NOW()
                  AND LOWER(TRIM(status)) IN ('agendada', 'confirmada', 'reagendada')
            """, (clinica_id,))
            atualizadas = cursor.rowcount
            conn.commit()
            return atualizadas
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"[ConsultaService] Erro ao atualizar faltas: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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
            # Se nenhum ID for fornecido, mas houver um nome, garante que o registro da especialidade exista e obtém o ID
            if especialidade_id is None and especialidade:
                try:
                    especialidade_id = EspecialidadeService.get_or_create(especialidade, conn=conn)
                except Exception as e:
                    print(f"[ConsultaService] Erro ao garantir especialidade: {e}")

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
                params = (
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
                )
            else:
                query = """
                    INSERT INTO odontoPro_consulta 
                    (clinica_id, paciente_id, medico_id, data_hora, status, observacoes, 
                     nome, email, telefone, criado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
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
                )

            print("[ConsultaService] Executando INSERT:", query.strip().replace('\n', ' '))
            print("[ConsultaService] Parâmetros:", params)
            cursor.execute(query, params)
            consulta_id = cursor.lastrowid
            rowcount = cursor.rowcount
            print(f"[ConsultaService] cursor.lastrowid={consulta_id}, cursor.rowcount={rowcount}")
            conn.commit()
            print("[ConsultaService] commit executado")

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
            if conn:
                try:
                    conn.rollback()
                    print("[ConsultaService] rollback executado após erro MySQL")
                except Exception as rollback_error:
                    print(f"[ConsultaService] Erro ao dar rollback: {rollback_error}")
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
            if conn:
                try:
                    conn.rollback()
                    print("[ConsultaService] rollback executado após erro inesperado")
                except Exception as rollback_error:
                    print(f"[ConsultaService] Erro ao dar rollback: {rollback_error}")
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
    def buscar_por_id(consulta_id, clinica_id=None):
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

            if clinica_id is not None:
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
                      AND c.clinica_id = %s
                """
                cursor.execute(query, (consulta_id, clinica_id))
            else:
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
