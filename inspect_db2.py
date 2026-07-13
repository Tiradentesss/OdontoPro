import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'SistemaDesktop'))
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()
for table in ['odontoPro_diasemanadisponivel', 'odontoPro_horarioaberto', 'odontoPro_medicohorario', 'odontoPro_consulta']:
    print('\nTABLE', table)
    cursor.execute('SELECT * FROM %s LIMIT 5' % table)
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = %s", (table,))
    cols = [r[0] for r in cursor.fetchall()]
    print('COLUMNS:', cols)

cursor.close()
conn.close()
