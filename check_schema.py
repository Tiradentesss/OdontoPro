import sys
sys.path.insert(0, 'SistemaDesktop')
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Check if table exists
cursor.execute("SHOW COLUMNS FROM odontoPro_clinicaimagem")
columns = cursor.fetchall()

print('=== Estrutura da tabela odontoPro_clinicaimagem ===')
for col in columns:
    print(f'Campo: {col[0]:20} | Tipo: {col[1]:30} | Null: {col[2]:5} | Key: {col[3]:5} | Default: {col[4]}')

cursor.close()
conn.close()
