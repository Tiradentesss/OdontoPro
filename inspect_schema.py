import sys
sys.path.append(r'c:\Users\58143406\Documents\Desktop_2\OdontoPro\SistemaDesktop')
from config.database import get_connection
conn = get_connection()
cur = conn.cursor()
tables = ['odontoPro_especialidade', 'odontoPro_medico', 'odontoPro_medico_especialidades']
for t in tables:
    try:
        cur.execute(f'SHOW COLUMNS FROM {t}')
        print('TABLE', t)
        for row in cur.fetchall():
            print(row)
        print()
    except Exception as e:
        print('ERR', t, e)
cur.close()
conn.close()
