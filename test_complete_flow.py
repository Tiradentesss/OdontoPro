"""
Script de teste completo que simula o fluxo de seleção, upload e UPSERT de fotos
"""
import sys
sys.path.insert(0, 'SistemaDesktop')

from config.database import get_connection
from services.cloudinary_service import upload_image_to_cloudinary
from PIL import Image
import os
import time

def create_test_images():
    """Criar imagens de teste simples"""
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    images_created = []
    
    for i in range(1, 4):
        img_path = os.path.join(test_dir, f"foto_teste_{i}.png")
        
        # Criar imagem simples 200x200 com cores diferentes
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # R, G, B
        img = Image.new('RGB', (200, 200), colors[i-1])
        img.save(img_path)
        
        print(f"  ✓ Criada: {img_path}")
        images_created.append(img_path)
    
    return images_created

def simulate_gallery_selection_and_save(clinica_id=1, test_images=None):
    """Simular a seleção de fotos e salvar"""
    print(f"\n{'='*70}")
    print(f"SIMULANDO: Seleção de 3 fotos e SALVAR ALTERAÇÕES (clinica_id={clinica_id})")
    print(f"{'='*70}")
    
    if not test_images:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Simular self.clinic_photos = [img1_path, img2_path, img3_path]
    clinic_photos = test_images[:]
    
    print(f"\nFotos selecionadas:")
    for idx, photo_path in enumerate(clinic_photos):
        ordem = idx + 1
        print(f"  Foto {ordem}: {photo_path}")
    
    # Simular _save_clinic_data() - parte de fotos
    failed_photos = []
    saved_records = []
    
    print(f"\nProcessando uploads e salvando no banco...")
    
    for index, photo_path in enumerate(clinic_photos):
        ordem = index + 1
        
        if not photo_path:
            print(f"  [FOTO {ordem}] Vazio, pulando")
            continue
        
        # Se já for URL remota, preservar
        if isinstance(photo_path, str) and photo_path.lower().startswith(("http://", "https://")):
            print(f"  [FOTO {ordem}] URL remota detectada, preservando")
            saved_url = photo_path
        # Se for arquivo local, fazer upload
        elif isinstance(photo_path, str) and os.path.exists(photo_path):
            try:
                timestamp = int(time.time())
                public_id = f"clinica_{clinica_id}_foto_{ordem}_{timestamp}"
                folder = f"odontopro/clinicas/{clinica_id}/galeria"
                print(f"  [FOTO {ordem}] Iniciando upload Cloudinary...")
                saved_url = upload_image_to_cloudinary(photo_path, public_id=public_id, folder=folder)
                print(f"    ✓ Upload concluído: {saved_url[:100]}...")
            except Exception as upload_error:
                print(f"  [FOTO {ordem}] ✗ ERRO no upload: {upload_error}")
                failed_photos.append(ordem)
                continue
        else:
            print(f"  [FOTO {ordem}] ✗ Caminho inválido: {photo_path}")
            continue
        
        # UPSERT
        if saved_url and isinstance(saved_url, str) and saved_url.lower().startswith("https://"):
            try:
                cursor.execute("""
                    SELECT id
                    FROM odontoPro_clinicaimagem
                    WHERE clinica_id = %s AND ordem = %s
                """, (clinica_id, ordem))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    cursor.execute("""
                        UPDATE odontoPro_clinicaimagem
                        SET imagem = %s
                        WHERE clinica_id = %s AND ordem = %s
                    """, (saved_url, clinica_id, ordem))
                    print(f"    ✓ Record atualizado (ID: {existing_record[0]})")
                    saved_records.append((ordem, "UPDATE", existing_record[0]))
                else:
                    cursor.execute("""
                        INSERT INTO odontoPro_clinicaimagem
                        (clinica_id, imagem, ordem)
                        VALUES (%s, %s, %s)
                    """, (clinica_id, saved_url, ordem))
                    new_id = cursor.lastrowid
                    print(f"    ✓ Novo registro inserido (ID: {new_id})")
                    saved_records.append((ordem, "INSERT", new_id))
            except Exception as db_error:
                print(f"  [FOTO {ordem}] ✗ ERRO ao salvar: {db_error}")
                failed_photos.append(ordem)
                continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return {
        "saved": len(saved_records),
        "failed": failed_photos,
        "records": saved_records
    }

def verify_database_state(clinica_id=1):
    """Verificar estado do banco de dados"""
    print(f"\n{'='*70}")
    print(f"VERIFICAR ESTADO DO BANCO (clinica_id={clinica_id})")
    print(f"{'='*70}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, clinica_id, ordem, LENGTH(imagem) as url_len, SUBSTRING(imagem, 1, 100) as url_preview
        FROM odontoPro_clinicaimagem
        WHERE clinica_id = %s
        ORDER BY ordem ASC
    """, (clinica_id,))
    
    results = cursor.fetchall()
    
    print(f"\nTotal de registros: {len(results)}")
    
    if results:
        print(f"\n{'ID':5} {'Ordem':7} {'URL Length':15} {'Preview':50}")
        print("-" * 70)
        for row in results:
            print(f"{row[0]:5} {row[2]:7} {row[3]:15} {row[4]:50}...")
    else:
        print("  Nenhum registro encontrado")
    
    cursor.close()
    conn.close()
    
    return len(results)

def test_upsert_update(clinica_id=1, test_images=None):
    """Testar UPDATE (trocar Foto 2)"""
    print(f"\n{'='*70}")
    print(f"TESTE DE UPSERT UPDATE: Trocar apenas Foto 2 (clinica_id={clinica_id})")
    print(f"{'='*70}")
    
    if not test_images or len(test_images) < 2:
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Simular: trocar foto 2, mantendo 1 e 3
    clinic_photos = [None, test_images[0], None]  # Foto 2 recebe uma imagem
    
    print(f"\nFoto 2 será atualizada com nova imagem...")
    
    for index, photo_path in enumerate(clinic_photos):
        ordem = index + 1
        
        if not photo_path:
            print(f"  [FOTO {ordem}] Vazio, pulando")
            continue
        
        if isinstance(photo_path, str) and os.path.exists(photo_path):
            try:
                timestamp = int(time.time())
                public_id = f"clinica_{clinica_id}_foto_{ordem}_updated_{timestamp}"
                folder = f"odontopro/clinicas/{clinica_id}/galeria"
                print(f"  [FOTO {ordem}] Upload da nova imagem...")
                saved_url = upload_image_to_cloudinary(photo_path, public_id=public_id, folder=folder)
                print(f"    ✓ Upload concluído")
                
                # UPSERT
                cursor.execute("""
                    SELECT id
                    FROM odontoPro_clinicaimagem
                    WHERE clinica_id = %s AND ordem = %s
                """, (clinica_id, ordem))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    cursor.execute("""
                        UPDATE odontoPro_clinicaimagem
                        SET imagem = %s
                        WHERE clinica_id = %s AND ordem = %s
                    """, (saved_url, clinica_id, ordem))
                    print(f"    ✓ Record atualizado (ID: {existing_record[0]})")
                else:
                    print(f"    ! Nenhum registro existente para ordem {ordem}")
                    
            except Exception as e:
                print(f"  [FOTO {ordem}] ✗ ERRO: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()

def test_no_duplicates(clinica_id=1):
    """Verificar que não há duplicatas"""
    print(f"\n{'='*70}")
    print(f"VERIFICAR DUPLICATAS (clinica_id={clinica_id})")
    print(f"{'='*70}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ordem, COUNT(*) as count
        FROM odontoPro_clinicaimagem
        WHERE clinica_id = %s
        GROUP BY ordem
        HAVING count > 1
    """, (clinica_id,))
    
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"\n✗ DUPLICATAS ENCONTRADAS:")
        for row in duplicates:
            print(f"  Ordem {row[0]}: {row[1]} registros")
    else:
        print(f"\n✓ Nenhuma duplicata encontrada")
    
    # Mostrar resumo
    cursor.execute("""
        SELECT COUNT(DISTINCT ordem) as ordens_unicas
        FROM odontoPro_clinicaimagem
        WHERE clinica_id = %s
    """, (clinica_id,))
    
    result = cursor.fetchone()
    print(f"  Total de ordens únicas: {result[0]}")
    
    cursor.close()
    conn.close()

def main():
    print("\n" + "█"*70)
    print("TESTE COMPLETO - INTEGRAÇÃO GALERIA DA CLÍNICA")
    print("█"*70)
    
    clinica_id = 1
    
    # Passo 1: Criar imagens de teste
    print(f"\n1. CRIAR IMAGENS DE TESTE")
    print("="*70)
    test_images = create_test_images()
    
    # Passo 2: Limpar dados anteriores (opcional)
    print(f"\n2. LIMPAR DADOS ANTERIORES (opcional)")
    print("="*70)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM odontoPro_clinicaimagem WHERE clinica_id = %s", (clinica_id,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"  Dados anteriores removidos para clinica_id={clinica_id}")
    
    # Passo 3: Simular seleção e salvar
    print(f"\n3. PRIMEIRA SALVA - INSERT de 3 fotos")
    result = simulate_gallery_selection_and_save(clinica_id, test_images)
    print(f"\nResultado: {result['saved']} salvos, {len(result['failed'])} falharam")
    
    # Passo 4: Verificar banco
    count1 = verify_database_state(clinica_id)
    print(f"\n✓ Esperado: 3 registros | Encontrado: {count1}")
    
    # Passo 5: Verificar duplicatas
    test_no_duplicates(clinica_id)
    
    # Passo 6: Trocar Foto 2
    print(f"\n4. SEGUNDA SALVA - UPDATE da Foto 2")
    test_upsert_update(clinica_id, test_images)
    
    # Passo 7: Verificar banco novamente
    count2 = verify_database_state(clinica_id)
    print(f"\n✓ Esperado: 3 registros (sem duplicatas) | Encontrado: {count2}")
    
    # Passo 8: Verificar duplicatas novamente
    test_no_duplicates(clinica_id)
    
    print("\n" + "█"*70)
    print("TESTE CONCLUÍDO")
    print("█"*70 + "\n")

if __name__ == "__main__":
    main()
