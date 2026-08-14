import sys
import os

# Ensure SistemaDesktop is on sys.path so imports like 'config.database' work
ROOT = os.path.abspath(os.path.dirname(__file__))
SISTEMA_PATH = os.path.join(ROOT, "SistemaDesktop")
if SISTEMA_PATH not in sys.path:
    sys.path.insert(0, SISTEMA_PATH)

from config.database import get_connection
try:
    conn = get_connection()
    cursor = conn.cursor()
    # Buscar por nome contendo 'Sorriso Norte' (acerto de acentos/separadores)
    cursor.execute("""
        SELECT id, nome, logo
        FROM odontoPro_clinica
        WHERE nome LIKE %s
        LIMIT 5
    """, ("%Sorriso%Norte%",))
    rows = cursor.fetchall()
    if not rows:
        # tentar sem wildcard entre palavras
        cursor.execute("""
            SELECT id, nome, logo
            FROM odontoPro_clinica
            WHERE nome LIKE %s
            LIMIT 5
        """, ("%Sorriso Norte%",))
        rows = cursor.fetchall()

    # se ainda vazio, tentar buscar por 'Sorriso'
    if not rows:
        cursor.execute("""
            SELECT id, nome, logo
            FROM odontoPro_clinica
            WHERE nome LIKE %s
            LIMIT 5
        """, ("%Sorriso%",))
        rows = cursor.fetchall()

    # imprimir resultados solicitados
    if not rows:
        print("[RESULT] nenhuma clínica encontrada com nome contendo 'Sorriso' ou 'Sorriso Norte'.")
    else:
        for r in rows:
            clin_id = r[0]
            nome = r[1]
            logo = r[2]
            print("[RESULT]")
            print(f"clinica_id: {clin_id}")
            print(f"nome: {nome}")
            # mostrar tipo e começo do valor do logo sem expor segredos
            if logo is None:
                print("valor_bruto_no_banco: NULL")
            elif isinstance(logo, str) and logo.strip()=="":
                print("valor_bruto_no_banco: EMPTY STRING")
            else:
                # mostrar prefixo (first 200 chars) safely
                s = str(logo)
                preview = s[:200]
                print(f"valor_bruto_no_banco (preview, max200): {preview}")
                # classify format
                if s.startswith('http://') or s.startswith('https://'):
                    print("formato_detectado: absolute_url")
                elif s.startswith('/'):
                    print("formato_detectado: absolute_path_on_server")
                elif '\\' in s or ':' in s[:3]:
                    print("formato_detectado: local_windows_path_or_other")
                else:
                    print("formato_detectado: filename_or_relative_path")

except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)
finally:
    try:
        cursor.close()
    except:
        pass
    try:
        conn.close()
    except:
        pass
