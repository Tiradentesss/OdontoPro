import sys
sys.path.insert(0, 'SistemaDesktop')
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor(dictionary=True)

print('=== SCHEMA - odontoPro_paciente ===')
cursor.execute('DESCRIBE odontoPro_paciente')
paciente_schema = cursor.fetchall()
for col in paciente_schema:
    print(f"{col['Field']}: {col['Type']} | NULL: {col['Null']} | Default: {col['Default']}")

print('\n=== SCHEMA - odontoPro_medico ===')
cursor.execute('DESCRIBE odontoPro_medico')
medico_schema = cursor.fetchall()
for col in medico_schema:
    print(f"{col['Field']}: {col['Type']} | NULL: {col['Null']} | Default: {col['Default']}")

cursor.close()
conn.close()
