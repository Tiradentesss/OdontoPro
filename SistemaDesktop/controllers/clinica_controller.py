# controllers/clinica_controller.py

from config.database import get_connection
from models.data import LIMITE_CONSULTAS


class ClinicaController:

    @staticmethod
    def listar_consultas(clinica_id, pagina=0):
        """
        Lista consultas paginadas da clínica
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            inicio = pagina * LIMITE_CONSULTAS
            
            cursor.execute("""
                SELECT 
                    c.id,
                    p.nome,
                    c.data_hora,
                    c.status,
                    p.telefone,
                    p.email,
                    m.nome AS medico_nome,
                    c.especialidade
                FROM odontoPro_consulta c
                LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
                LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
                WHERE c.clinica_id = %s
                ORDER BY c.data_hora DESC
                LIMIT %s OFFSET %s
            """, (clinica_id, LIMITE_CONSULTAS, inicio))
            
            return cursor.fetchall()
        
        except Exception as e:
            print(f"Erro ao listar consultas: {e}")
            return []
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def contar_consultas(clinica_id):
        """
        Conta total de consultas da clínica
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) as total FROM odontoPro_consulta 
                WHERE clinica_id = %s
            """, (clinica_id,))
            
            return cursor.fetchone()[0]
        
        except Exception as e:
            print(f"Erro ao contar consultas: {e}")
            return 0
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def obter_info_clinica(clinica_id):
        """
        Obtém informações gerais da clínica
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM odontoPro_clinica WHERE id = %s
            """, (clinica_id,))
            
            return cursor.fetchone()
        
        except Exception as e:
            print(f"Erro ao obter clínica: {e}")
            return None
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
