# controllers/financeiro_controller.py

from config.database import get_connection
from datetime import datetime, timedelta
from decimal import Decimal


class FinanceiroController:
    
    @staticmethod
    def criar_transacao(tipo, descricao, valor, clinica_id, data=None, categoria=None):
        """
        Cria uma nova transação (receita ou despesa)
        tipo: 'receita' ou 'despesa'
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            data = data or datetime.now()
            
            cursor.execute("""
                INSERT INTO odontopro_financeiro 
                (tipo, descricao, valor, clinica_id, data, categoria)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo.lower(), descricao, valor, clinica_id, data, categoria))
            
            conn.commit()
            return {"sucesso": True, "id": cursor.lastrowid, "mensagem": "Transação registrada"}
        
        except Exception as e:
            if conn:
                conn.rollback()
            return {"sucesso": False, "mensagem": f"Erro ao registrar transação: {str(e)}"}
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def listar_transacoes(clinica_id, data_inicio=None, data_fim=None):
        """
        Lista transações de uma clínica em um período
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            if not data_inicio:
                data_inicio = datetime.now().replace(day=1)
            if not data_fim:
                data_fim = datetime.now()
            
            cursor.execute("""
                SELECT * FROM odontoPro_financeiro
                WHERE clinica_id = %s AND data BETWEEN %s AND %s
                ORDER BY data DESC
            """, (clinica_id, data_inicio, data_fim))
            
            return cursor.fetchall()
        
        except Exception as e:
            print(f"Erro ao listar transações: {e}")
            return []
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def obter_resumo_financeiro(clinica_id, data_inicio=None, data_fim=None):
        """
        Retorna resumo financeiro: total receita, despesa e lucro
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            if not data_inicio:
                data_inicio = datetime.now().replace(day=1)
            if not data_fim:
                data_fim = datetime.now()
            
            # Receitas
            cursor.execute("""
                SELECT COALESCE(SUM(valor), 0) as total 
                FROM odontoPro_financeiro
                WHERE clinica_id = %s AND tipo = 'receita' 
                AND data BETWEEN %s AND %s
            """, (clinica_id, data_inicio, data_fim))
            
            receita = cursor.fetchone()['total']
            
            # Despesas
            cursor.execute("""
                SELECT COALESCE(SUM(valor), 0) as total 
                FROM odontoPro_financeiro
                WHERE clinica_id = %s AND tipo = 'despesa' 
                AND data BETWEEN %s AND %s
            """, (clinica_id, data_inicio, data_fim))
            
            despesa = cursor.fetchone()['total']
            
            # Consultas realizadas
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM odontoPro_consulta
                WHERE clinica_id = %s AND status = 'realizada'
                AND data_hora BETWEEN %s AND %s
            """, (clinica_id, data_inicio, data_fim))
            
            consultas_realizadas = cursor.fetchone()['total']
            
            # Total de consultas
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM odontoPro_consulta
                WHERE clinica_id = %s 
                AND data_hora BETWEEN %s AND %s
            """, (clinica_id, data_inicio, data_fim))
            
            total_consultas = cursor.fetchone()['total']
            
            return {
                'faturamento': float(receita),
                'despesas': float(despesa),
                'lucro': float(receita - despesa),
                'realizadas': consultas_realizadas,
                'total_consultas': total_consultas
            }
        
        except Exception as e:
            print(f"Erro ao obter resumo: {e}")
            return {
                'faturamento': 0,
                'despesas': 0,
                'lucro': 0,
                'realizadas': 0,
                'total_consultas': 0
            }
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    @staticmethod
    def obter_dados_por_periodo(clinica_id, periodo='7_dias'):
        """
        Retorna dados agrupados por período para gráficos
        período: '7_dias', '30_dias', 'ano'
        """
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            if periodo == '7_dias':
                data_inicio = datetime.now() - timedelta(days=7)
                grupo = "DATE(data)"
            elif periodo == '30_dias':
                data_inicio = datetime.now() - timedelta(days=30)
                grupo = "WEEK(data)"
            else:  # ano
                data_inicio = datetime.now().replace(month=1, day=1)
                grupo = "MONTH(data)"
            
            cursor.execute(f"""
                SELECT 
                    {grupo} as periodo,
                    tipo,
                    SUM(valor) as total
                FROM odontoPro_financeiro
                WHERE clinica_id = %s AND data >= %s
                GROUP BY {grupo}, tipo
                ORDER BY {grupo}
            """, (clinica_id, data_inicio))
            
            return cursor.fetchall()
        
        except Exception as e:
            print(f"Erro ao obter dados: {e}")
            return []
        
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
