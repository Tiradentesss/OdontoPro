import sys
import mysql.connector
sys.path.insert(0, 'SistemaDesktop')
from config.settings import DB_CONFIG

print('DB_CONFIG=', DB_CONFIG)
cn = mysql.connector.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG.get('password', ''),
    database=DB_CONFIG['database'],
    port=DB_CONFIG.get('port', 3306)
)
cur = cn.cursor()
queries = [
    'SHOW CREATE TABLE odontoPro_especialidade',
    'SHOW CREATE TABLE odontoPro_medico_especialidades',
    'SHOW CREATE TABLE odontoPro_medico',
    "SELECT id,nome,clinica_id FROM odontoPro_especialidade WHERE nome LIKE '%Odontoped%';",
    'SELECT id, medico_id, especialidade_id FROM odontoPro_medico_especialidades WHERE medico_id=18;',
    'SELECT id, nome, clinica_id, ativo FROM odontoPro_medico WHERE id=18;',
    'SELECT id, nome, clinica_id FROM odontoPro_especialidade ORDER BY clinica_id IS NULL DESC, clinica_id, nome LIMIT 200',
    'SELECT DISTINCT clinica_id FROM odontoPro_especialidade ORDER BY clinica_id',
    'SELECT e.id,e.nome,e.clinica_id, COUNT(me.medico_id) as num_medicos FROM odontoPro_especialidade e LEFT JOIN odontoPro_medico_especialidades me ON me.especialidade_id=e.id GROUP BY e.id,e.nome,e.clinica_id ORDER BY num_medicos DESC, e.clinica_id, e.nome LIMIT 200',
    'SELECT e.id,e.nome,e.clinica_id FROM odontoPro_especialidade e WHERE e.clinica_id=7 ORDER BY nome',
    'SELECT DISTINCT e.id,e.nome,e.clinica_id FROM odontoPro_especialidade e JOIN odontoPro_medico_especialidades me ON me.especialidade_id=e.id JOIN odontoPro_medico m ON m.id=me.medico_id WHERE m.clinica_id=7 ORDER BY e.id'
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
