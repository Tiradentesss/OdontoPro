import os, json, sys, pathlib
# ensure project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
os.environ['DJANGO_SETTINGS_MODULE'] = 'setup.settings'
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='odontoPro_clinica' AND COLUMN_NAME='logo'")
    row = cursor.fetchone()
    output = {'column_type': row[0] if row else None, 'is_nullable': row[1] if row else None, 'column_default': row[2] if row else None}
    print(json.dumps(output))
