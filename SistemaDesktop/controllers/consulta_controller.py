from config.database import get_connection
class ConsultaController:

    @staticmethod
    def listar_por_clinica(clinica_id):
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
                c.observacoes,
                m.nome as medico_nome
            FROM odontopro_consulta c
            LEFT JOIN odontopro_paciente p ON c.paciente_id = p.id
            LEFT JOIN odontopro_medico m ON c.medico_id = m.id
            WHERE c.clinica_id = %s
            ORDER BY c.data_hora DESC
        """, (clinica_id,))

        dados = cursor.fetchall()
        conn.close()
        return dados

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
                m.nome
            FROM odontopro_consulta c
            LEFT JOIN odontopro_paciente p ON c.paciente_id = p.id
            LEFT JOIN odontopro_medico m ON c.medico_id = m.id
            WHERE c.id = %s
        """, (consulta_id,))

        dado = cursor.fetchone()
        conn.close()
        return dado