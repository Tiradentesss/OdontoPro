import sys
sys.path.insert(0, 'SistemaDesktop')
from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Check existing records
cursor.execute("SELECT COUNT(*) as count FROM odontoPro_clinicaimagem")
result = cursor.fetchone()
print(f"Total de registros: {result[0]}")

# If there are records, show them
if result[0] > 0:
    print("\n=== Registros existentes ===")
    cursor.execute("SELECT id, clinica_id, ordem, LENGTH(imagem) as url_length, SUBSTRING(imagem, 1, 80) as url_preview FROM odontoPro_clinicaimagem LIMIT 5")
    for row in cursor.fetchall():
        print(f"ID: {row[0]:3} | Clinica: {row[1]:3} | Ordem: {row[2]:2} | Len: {row[3]:3} | URL: {row[4]}")

# Verify the column can handle typical Cloudinary URLs
cursor.execute("SELECT MAX(LENGTH(imagem)) as max_length FROM odontoPro_clinicaimagem")
result = cursor.fetchone()
if result[0]:
    print(f"\nComprimento máximo de URL atual no banco: {result[0]} caracteres")

cursor.close()
conn.close()
