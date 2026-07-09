"""
Service para operações com Consultas.
Validações, verificação de conflitos e transações.
"""

from config.database import get_connection
from datetime import datetime, timedelta
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
    def criar_consulta(clinica_id, paciente_id, medico_id, data_hora, especialidade, 
                       status='agendada', observacoes=''):
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
            cursor = conn.cursor()

            # Verificar se paciente existe
            cursor.execute("SELECT id FROM odontoPro_paciente WHERE id = %s", (paciente_id,))
            if not cursor.fetchone():
                conn.close()
                return {
                    'sucesso': False,
                    'mensagem': 'Paciente não encontrado.',
                    'consulta_id': None,
                    'erro': 'Paciente inválido'
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

            # Inserir consulta (com autocommit=True, é automático)
            query = """
                INSERT INTO odontoPro_consulta 
                (clinica_id, paciente_id, medico_id, data_hora, status, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, (
                clinica_id,
                paciente_id,
                medico_id,
                data_hora,
                status.lower(),
                observacoes
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
