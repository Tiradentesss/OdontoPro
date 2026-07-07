import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'SistemaDesktop'))
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)
print('=== DESCRIBE odontoPro_paciente ===')
cursor.execute('DESCRIBE odontoPro_paciente')
for row in cursor.fetchall():
    print(row)
print('\n=== CREATE TABLE odontoPro_paciente ===')
cursor.execute('SHOW CREATE TABLE odontoPro_paciente')
print(cursor.fetchone()['Create Table'])
print('\n=== COUNT ===')
cursor.execute('SELECT COUNT(*) AS c FROM odontoPro_paciente')
print(cursor.fetchone())
conn.close()
