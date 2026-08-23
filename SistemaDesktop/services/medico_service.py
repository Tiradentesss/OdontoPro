"""
Service para operações com Médicos.
Busca por clínica, especialidades e validações.
"""

import re

from config.database import get_connection
from services.query_logger import timed_sql, inc_query_count


class MedicoService:
    """Serviço centralizado para operações com médicos"""

    _PREFIXO_NOME_RE = re.compile(r"^(?:Dentista|Dr\(a\)\.|Dra?\.)(?:\s+|$)", re.IGNORECASE)

    @staticmethod
    def normalizar_nome(nome):
        """Remove um prefixo profissional inicial do nome do médico."""
        nome_limpo = str(nome or "").strip()
        return MedicoService._PREFIXO_NOME_RE.sub("", nome_limpo, count=1).strip()

    @staticmethod
    def formatar_nome_visual(nome):
        """Apresenta o nome do médico com o prefixo visual padronizado."""
        nome_limpo = MedicoService.normalizar_nome(nome)
        return f"Dr(a). {nome_limpo}" if nome_limpo else "Dr(a)."

    @staticmethod
    def listar_por_clinica(clinica_id):
        """
        Lista todos os médicos de uma clínica com suas especialidades.
        
        Args:
            clinica_id: ID da clínica
        
        Returns:
            Lista de tuplas (id, nome, especialidades_str, especialidade_id)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Buscar médicos com suas especialidades (usado por listagens mais completas)
            def _exec():
                query = """
                    SELECT 
                        m.id,
                        m.nome,
                        m.email,
                        GROUP_CONCAT(e.nome SEPARATOR ', ') AS especialidades,
                        GROUP_CONCAT(e.id SEPARATOR ',') AS especialidade_ids
                    FROM odontoPro_medico m
                    LEFT JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id
                    LEFT JOIN odontoPro_especialidade e ON me.especialidade_id = e.id
                    WHERE m.clinica_id = %s AND m.ativo = 1
                    GROUP BY m.id, m.nome, m.email
                    ORDER BY m.nome ASC
                """

                print("MedicoService.listar_por_clinica() - consultando banco")
                cursor.execute(query, (clinica_id,))
                resultado = cursor.fetchall()
                print(f"MedicoService.listar_por_clinica() - retornou {len(resultado)} médicos")
                return resultado

            medicos = timed_sql("Buscar médicos (listar_por_clinica)", _exec) or []
            # marcar que possivelmente foram executadas consultas (a contagem já é feita em timed_sql)
            inc_query_count(0)
            return medicos

        except Exception as e:
            print(f"[MedicoService] Erro em listar_por_clinica: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def buscar_por_id(medico_id):
        """
        Busca um médico específico com suas especialidades.
        
        Args:
            medico_id: ID do médico
        
        Returns:
            Tupla (id, nome, especialidades_str, especialidade_ids) ou None
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT 
                    m.id,
                    m.nome,
                    GROUP_CONCAT(e.nome SEPARATOR ', ') AS especialidades,
                    GROUP_CONCAT(e.id SEPARATOR ',') AS especialidade_ids
                FROM odontoPro_medico m
                LEFT JOIN odontoPro_medico_especialidades me ON m.id = me.medico_id
                LEFT JOIN odontoPro_especialidade e ON me.especialidade_id = e.id
                WHERE m.id = %s
                GROUP BY m.id, m.nome
            """

            def _exec():
                cursor.execute(query, (medico_id,))
                return cursor.fetchone()

            medico = timed_sql("Buscar médico por id (MedicoService.buscar_por_id)", _exec, sql=query)
            return medico

        except Exception as e:
            print(f"[MedicoService] Erro em buscar_por_id: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def obter_especialidade_principal(medico_id):
        """
        Obtém a especialidade principal (primeira) de um médico.
        
        Args:
            medico_id: ID do médico
        
        Returns:
            Nome da especialidade ou string vazia
        """
        medico = MedicoService.buscar_por_id(medico_id)
        
        if medico:
            especialidades = medico[2]  # 3º elemento é especialidades_str
            if especialidades:
                # Retornar primeira especialidade
                return especialidades.split(', ')[0]
        
        return ""

    @staticmethod
    def obter_especialidades_lista(medico_id):
        """
        Obtém lista de especialidades de um médico.
        
        Args:
            medico_id: ID do médico
        
        Returns:
            Lista de especialidades ou lista vazia
        """
        medico = MedicoService.buscar_por_id(medico_id)
        
        if medico:
            especialidades = medico[2]  # 3º elemento é especialidades_str
            if especialidades:
                return [e.strip() for e in especialidades.split(', ')]
        
        return []

    @staticmethod
    def formatar_exibicao(medico):
        """
        Formata um médico para exibição (nome + especialidades).
        
        Args:
            medico: Tupla (id, nome, especialidades_str, ...)
        
        Returns:
            String formatada "Nome - Especialidade(s)"
        """
        if not medico:
            return ""
        
        id_med, nome, especialidades, _ = medico[:4]
        
        if especialidades:
            return f"{nome} - {especialidades}"
        
        return nome

    @staticmethod
    def extrair_id_de_display(display_text, clinica_id):
        """
        Extrai o ID do médico a partir do texto de exibição.
        
        Args:
            display_text: Texto exibido "Nome - Especialidade(s)"
            clinica_id: ID da clínica para validação
        
        Returns:
            ID do médico ou None
        """
        medicos = MedicoService.listar_por_clinica(clinica_id)
        
        for medico in medicos:
            if MedicoService.formatar_exibicao(medico) == display_text:
                return medico[0]
        
        return None
