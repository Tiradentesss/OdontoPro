import sys
import mysql.connector
sys.path.insert(0, 'SistemaDesktop')
from config.settings import DB_CONFIG

cn = mysql.connector.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG.get('password', ''),
    database=DB_CONFIG['database'],
    port=DB_CONFIG.get('port', 3306)
)
cur = cn.cursor()
queries = [
    "SELECT m.id,m.nome,m.clinica_id, me.especialidade_id, e.nome, e.clinica_id FROM odontoPro_medico m JOIN odontoPro_medico_especialidades me ON me.medico_id=m.id JOIN odontoPro_especialidade e ON e.id=me.especialidade_id WHERE m.clinica_id=7 ORDER BY m.id",
    "SELECT m.clinica_id, COUNT(*) FROM odontoPro_medico m GROUP BY m.clinica_id ORDER BY m.clinica_id",
    "SELECT e.clinica_id, COUNT(*) FROM odontoPro_especialidade e GROUP BY e.clinica_id ORDER BY e.clinica_id",
    "SELECT m.clinica_id, e.clinica_id, COUNT(*) FROM odontoPro_medico m JOIN odontoPro_medico_especialidades me ON me.medico_id=m.id JOIN odontoPro_especialidade e ON e.id=me.especialidade_id GROUP BY m.clinica_id, e.clinica_id ORDER BY m.clinica_id, e.clinica_id"
]
for q in queries:
    print('\nQUERY:', q)
    try:
        cur.execute(q)
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print('ERR', e)
cn.close()
