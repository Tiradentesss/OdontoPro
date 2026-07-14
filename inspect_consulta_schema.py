"""
Inspecionar o schema da tabela odontoPro_consulta
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from config.database import get_connection

conn = get_connection()
cursor = conn.cursor()

# Obter informações sobre as colunas da tabela
cursor.execute("""
    SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'odontoPro_consulta'
    ORDER BY ORDINAL_POSITION
""")

print("=" * 80)
print("SCHEMA DA TABELA: odontoPro_consulta")
print("=" * 80)

columns = cursor.fetchall()
for col in columns:
    col_name, col_type, is_nullable, col_default, col_key, extra = col
    print(f"\nColuna: {col_name}")
    print(f"  Tipo: {col_type}")
    print(f"  Nullable: {is_nullable}")
    print(f"  Default: {col_default}")
    print(f"  Key: {col_key}")
    print(f"  Extra: {extra}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
