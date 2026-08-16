"""
Script de teste para validar a integração das 3 fotos da galeria
com a tabela odontoPro_clinicaimagem
"""
import sys
sys.path.insert(0, 'SistemaDesktop')

from config.database import get_connection

def test_schema():
    """Verificar o schema da tabela"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("1. VERIFICAR SCHEMA DA TABELA odontoPro_clinicaimagem")
    print("="*70)
    
    cursor.execute("SHOW COLUMNS FROM odontoPro_clinicaimagem")
    columns = cursor.fetchall()
    
    for col in columns:
        print(f"  {col[0]:15} | {col[1]:30} | NULL: {col[2]:5} | KEY: {col[3]}")
    
    cursor.close()
    conn.close()

def test_load_clinic_photos(clinica_id=1):
    """Testar carregamento de fotos existentes"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print(f"2. CARREGAR FOTOS EXISTENTES (clinica_id={clinica_id})")
    print("="*70)
    
    cursor.execute("""
        SELECT id, clinica_id, ordem, SUBSTRING(imagem, 1, 80) as url_preview
        FROM odontoPro_clinicaimagem
        WHERE clinica_id = %s
        ORDER BY ordem ASC
    """, (clinica_id,))
    
    results = cursor.fetchall()
    if results:
        print(f"  Encontrados {len(results)} registros:")
        for row in results:
            print(f"  ID: {row[0]:3} | Clinica: {row[1]:3} | Ordem: {row[2]:2} | URL: {row[3]}...")
    else:
        print(f"  Nenhum registro encontrado para clinica_id={clinica_id}")
    
    cursor.close()
    conn.close()

def test_upsert_logic(clinica_id=1):
    """Testar a lógica de UPSERT"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("3. TESTAR LÓGICA DE UPSERT")
    print("="*70)
    
    # Simular URL de teste
    test_urls = [
        f"https://res.cloudinary.com/test/image/upload/v123456/odontopro/clinicas/{clinica_id}/galeria/teste1.jpg",
        f"https://res.cloudinary.com/test/image/upload/v123456/odontopro/clinicas/{clinica_id}/galeria/teste2.jpg"
    ]
    
    # Testar INSERT
    print(f"\n  Testando INSERT para clinica_id={clinica_id}...")
    for ordem in [1, 2]:
        cursor.execute("""
            SELECT id
            FROM odontoPro_clinicaimagem
            WHERE clinica_id = %s AND ordem = %s
        """, (clinica_id, ordem))
        
        existing = cursor.fetchone()
        
        if existing:
            print(f"    Ordem {ordem}: Registro já existe (ID: {existing[0]}), faria UPDATE")
        else:
            print(f"    Ordem {ordem}: Novo registro, faria INSERT")
    
    cursor.close()
    conn.close()

def test_column_capacity():
    """Verificar se a coluna imagem consegue armazenar URLs Cloudinary"""
    conn = get_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*70)
    print("4. VERIFICAR CAPACIDADE DA COLUNA 'imagem'")
    print("="*70)
    
    cursor.execute("""
        SELECT COLUMN_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = 'odontoPro_clinicaimagem'
        AND COLUMN_NAME = 'imagem'
    """)
    
    result = cursor.fetchone()
    if result:
        column_type = result[0]
        print(f"  Tipo da coluna: {column_type}")
        
        # Extrair tamanho se for VARCHAR
        if 'varchar' in column_type.lower():
            import re
            match = re.search(r'varchar\((\d+)\)', column_type.lower())
            if match:
                size = int(match.group(1))
                avg_cloudinary_url = 120
                print(f"  Tamanho máximo: {size} caracteres")
                print(f"  URL Cloudinary típica: ~{avg_cloudinary_url} caracteres")
                if size >= avg_cloudinary_url:
                    print(f"  ✓ CAPACIDADE SUFICIENTE")
                else:
                    print(f"  ✗ CAPACIDADE INSUFICIENTE")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    print("\n" + "█"*70)
    print("TESTE DE INTEGRAÇÃO - GALERIA DA CLÍNICA")
    print("█"*70)
    
    test_schema()
    test_column_capacity()
    test_upsert_logic()
    test_load_clinic_photos()
    
    print("\n" + "█"*70)
    print("TESTES CONCLUÍDOS")
    print("█"*70 + "\n")
