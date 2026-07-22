import sys
sys.path.append('SistemaDesktop')
from config.database import get_connection

conn = get_connection()
cur = conn.cursor(dictionary=True)
print('DB connected')
cur.execute("SHOW TABLES LIKE 'odontoPro_consulta'")
print('consulta table exists:', bool(cur.fetchone()))
cur.execute("SELECT COUNT(*) AS total FROM odontoPro_consulta")
print('total consultas:', cur.fetchone()['total'])
cur.execute("SELECT clinica_id, COUNT(*) AS total FROM odontoPro_consulta GROUP BY clinica_id ORDER BY clinica_id LIMIT 10")
print('por clinica:')
for row in cur.fetchall():
    print(row)
cur.execute("SELECT status, COUNT(*) AS total FROM odontoPro_consulta GROUP BY status ORDER BY status")
print('por status:')
for row in cur.fetchall():
    print(row)
conn.close()
