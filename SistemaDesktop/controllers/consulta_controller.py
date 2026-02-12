from config.database import get_connection


class ConsultaController:

    @staticmethod
    def listar_por_clinica(clinica_id):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                c.id,
                COALESCE(p.nome, c.nome) as nome_paciente,
                c.data_hora,
                c.status,
                p.telefone,
                p.email,
                p.sexo,
                p.data_nascimento,
                p.cpf,
                c.observacoes
            FROM odontopro_consulta c
            LEFT JOIN odontopro_paciente p ON c.paciente_id = p.id
            WHERE c.clinica_id = %s
            ORDER BY c.data_hora DESC
        """

        cursor.execute(query, (clinica_id,))
        resultados = cursor.fetchall()

        cursor.close()
        conn.close()

        return resultados

