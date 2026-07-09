"""
Service para operações com Pacientes.
Busca dinâmica, paginação e validações.
"""

from config.database import get_connection
from datetime import datetime


class PacienteService:
    """Serviço centralizado para operações com pacientes"""

    @staticmethod
    def buscar_por_cpf_ou_nome(clinica_id, termo_busca, limite=10, offset=0):
        """
        Busca pacientes por CPF ou Nome com paginação.
        
        Args:
            clinica_id: ID da clínica
            termo_busca: CPF ou Nome (parcial)
            limite: Número máximo de resultados
            offset: Deslocamento para paginação
        
        Returns:
            Lista de tuplas (id, nome, cpf, email, telefone)
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Limpar termo de busca
            termo = f"%{termo_busca.strip()}%"

            # Buscar pacientes que correspondem ao termo
            query = """
                SELECT 
                    id, 
                    nome, 
                    cpf, 
                    email, 
                    telefone,
                    data_nascimento
                FROM odontoPro_paciente
                WHERE (
                    LOWER(nome) LIKE LOWER(%s) OR 
                    cpf LIKE %s
                )
                ORDER BY nome ASC
                LIMIT %s OFFSET %s
            """

            cursor.execute(query, (termo, termo, limite, offset))
            pacientes = cursor.fetchall()
            return pacientes or []

        except Exception as e:
            print(f"[PacienteService] Erro em buscar_por_cpf_ou_nome: {e}")
            return []

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def contar_por_busca(termo_busca):
        """
        Conta total de pacientes que correspondem ao termo.
        
        Args:
            termo_busca: CPF ou Nome (parcial)
        
        Returns:
            Total de pacientes encontrados
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            termo = f"%{termo_busca.strip()}%"

            query = """
                SELECT COUNT(*)
                FROM odontoPro_paciente
                WHERE (
                    LOWER(nome) LIKE LOWER(%s) OR 
                    cpf LIKE %s
                )
            """

            cursor.execute(query, (termo, termo))
            total = cursor.fetchone()[0]
            return int(total or 0)

        except Exception as e:
            print(f"[PacienteService] Erro em contar_por_busca: {e}")
            return 0

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def buscar_por_id(paciente_id):
        """
        Busca um paciente específico pelo ID.
        
        Args:
            paciente_id: ID do paciente
        
        Returns:
            Tupla (id, nome, cpf, email, telefone, data_nascimento) ou None
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT 
                    id, 
                    nome, 
                    cpf, 
                    email, 
                    telefone,
                    data_nascimento
                FROM odontoPro_paciente
                WHERE id = %s
            """

            cursor.execute(query, (paciente_id,))
            paciente = cursor.fetchone()
            return paciente

        except Exception as e:
            print(f"[PacienteService] Erro em buscar_por_id: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @staticmethod
    def formatar_exibicao(paciente):
        """
        Formata um paciente para exibição (nome + CPF).
        
        Args:
            paciente: Tupla (id, nome, cpf, ...)
        
        Returns:
            String formatada "Nome (CPF)"
        """
        if not paciente:
            return ""
        
        id_pac, nome, cpf, email, telefone, data_nascimento = paciente[:6]
        
        if cpf:
            # Formatar CPF: XXX.XXX.XXX-XX
            cpf_str = cpf.replace(".", "").replace("-", "")
            if len(cpf_str) == 11:
                cpf_formatado = f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"
            else:
                cpf_formatado = cpf
            return f"{nome} ({cpf_formatado})"
        
        return nome

    @staticmethod
    def extrair_id_de_display(display_text, termo_original):
        """
        Extrai o ID do paciente a partir do texto de exibição.
        Realiza nova busca para confirmar.
        
        Args:
            display_text: Texto exibido "Nome (CPF)"
            termo_original: Termo original de busca
        
        Returns:
            ID do paciente ou None
        """
        pacientes = PacienteService.buscar_por_cpf_ou_nome(clinica_id=None, termo_busca=termo_original, limite=1)
        
        if pacientes:
            return pacientes[0][0]  # Retorna o ID (primeiro elemento)
        
        return None
