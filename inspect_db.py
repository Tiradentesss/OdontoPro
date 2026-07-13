from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
tables = [row[0] for row in cursor.fetchall()]
print('TABLES:', tables)

keys = ['agenda', 'horario', 'bloqueio', 'schedule', 'turno', 'consulta']
for t in tables:
    if any(k in t.lower() for k in keys):
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = %s", (t,))
        cols = [r[0] for r in cursor.fetchall()]
        print('\nTABLE', t, 'COLUMNS:', cols)

cursor.close()
conn.close()
