from config.database import get_connection
from models.data import LIMITE_CONSULTAS

class ConsultaController:

    @staticmethod
    def _build_filters(clinica_id, data=None, status=None, medico=None):
        where = ["c.clinica_id = %s"]
        params = [clinica_id]

        if data:
            # Espera data no formato YYYY-MM-DD
            where.append("DATE(c.data_hora) = %s")
            params.append(data)

        if status:
            where.append("LOWER(c.status) = %s")
            params.append(status.lower())

        if medico:
            where.append("m.nome = %s")
            params.append(medico)

        return " AND ".join(where), params

    @staticmethod
    def listar_por_clinica(clinica_id, pagina=0, limite=LIMITE_CONSULTAS, data=None, status=None, medico=None):
        conn = get_connection()
        cursor = conn.cursor()

        where_clause, params = ConsultaController._build_filters(clinica_id, data, status, medico)

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
                m.nome as medico_nome
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
        conn.close()
        return dados

    @staticmethod
    def contar_por_clinica(clinica_id, data=None, status=None, medico=None):
        conn = get_connection()
        cursor = conn.cursor()

        where_clause, params = ConsultaController._build_filters(clinica_id, data, status, medico)

        cursor.execute(f"""
            SELECT COUNT(*)
            FROM odontoPro_consulta c
            LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
            WHERE {where_clause}
        """, tuple(params))

        total = cursor.fetchone()[0]
        conn.close()
        return total

    @staticmethod
    def listar_opcoes_filtro(clinica_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT DATE(c.data_hora), m.nome
            FROM odontoPro_consulta c
            LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
            WHERE c.clinica_id = %s
            ORDER BY DATE(c.data_hora) DESC, m.nome ASC
        """, (clinica_id,))

        resultados = cursor.fetchall()
        conn.close()

        datas = sorted({r[0] for r in resultados if r[0]}, reverse=True)
        medicos = sorted({r[1] for r in resultados if r[1]})

        return datas, medicos

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
            FROM odontoPro_consulta c
            LEFT JOIN odontoPro_paciente p ON c.paciente_id = p.id
            LEFT JOIN odontoPro_medico m ON c.medico_id = m.id
            WHERE c.id = %s
        """, (consulta_id,))

        dado = cursor.fetchone()
        conn.close()
        return dado