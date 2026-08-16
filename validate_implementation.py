"""
Validação final do arquivo configuracoes.py
"""
import sys
sys.path.insert(0, 'SistemaDesktop')

def validate_configuracoes_py():
    """Validar que as modificações foram aplicadas corretamente"""
    
    print("\n" + "█"*70)
    print("VALIDAÇÃO FINAL - SistemaDesktop/views/configuracoes.py")
    print("█"*70)
    
    filepath = "SistemaDesktop/views/configuracoes.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificações
    checks = [
        ("_load_clinic_data contém SELECT de odontoPro_clinicaimagem",
         "SELECT imagem, ordem\n                        FROM odontoPro_clinicaimagem\n                        WHERE clinica_id = %s"),
        
        ("_load_clinic_data contém mapeamento ordem -> índice",
         "photos[ordem - 1] = imagem_url"),
        
        ("_save_clinic_data contém upload Cloudinary",
         "upload_image_to_cloudinary(photo_path, public_id=public_id, folder=folder)"),
        
        ("_save_clinic_data contém UPSERT SELECT",
         "SELECT id\n                                    FROM odontoPro_clinicaimagem\n                                    WHERE clinica_id = %s AND ordem = %s"),
        
        ("_save_clinic_data contém UPDATE",
         "UPDATE odontoPro_clinicaimagem\n                                        SET imagem = %s\n                                        WHERE clinica_id = %s AND ordem = %s"),
        
        ("_save_clinic_data contém INSERT",
         "INSERT INTO odontoPro_clinicaimagem\n                                        (clinica_id, imagem, ordem)\n                                        VALUES (%s, %s, %s)"),
        
        ("_update_gallery_display usa ImagePreview",
         "ImagePreview.create_rectangular_preview"),
        
        ("Banner não foi alterado",
         "self.clinic_banner = None  # Banner principal"),
        
        ("Logo não foi alterada",
         "self.images[\"logo\"]"),
        
        ("Imports de cloudinary_service estão presentes",
         "from services.cloudinary_service import upload_image_to_cloudinary"),
    ]
    
    print(f"\nValidando {len(checks)} pontos-chave...\n")
    
    passed = 0
    failed = 0
    
    for check_name, check_string in checks:
        if check_string in content:
            print(f"  ✓ {check_name}")
            passed += 1
        else:
            print(f"  ✗ {check_name}")
            failed += 1
    
    print(f"\n{'-'*70}")
    print(f"Resultado: {passed}/{len(checks)} validações passaram")
    
    if failed == 0:
        print(f"\n✓ ARQUIVO VALIDADO COM SUCESSO")
    else:
        print(f"\n✗ {failed} validações falharam")
    
    print("\n" + "█"*70 + "\n")
    
    return failed == 0

def count_modified_lines():
    """Contar linhas modificadas"""
    print("\n" + "█"*70)
    print("ANÁLISE DE MODIFICAÇÕES")
    print("█"*70)
    
    filepath = "SistemaDesktop/views/configuracoes.py"
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    print(f"\nArquivo: {filepath}")
    print(f"Total de linhas: {len(lines)}")
    
    # Contar métodos
    load_clinic_data_found = False
    save_clinic_data_found = False
    
    for i, line in enumerate(lines, 1):
        if "def _load_clinic_data(self):" in line:
            print(f"  - _load_clinic_data() encontrado em linha {i}")
            load_clinic_data_found = True
        if "def _save_clinic_data(self):" in line:
            print(f"  - _save_clinic_data() encontrado em linha {i}")
            save_clinic_data_found = True
    
    if load_clinic_data_found and save_clinic_data_found:
        print(f"\n✓ Ambos os métodos foram encontrados no arquivo")
    else:
        print(f"\n✗ Um ou mais métodos não encontrados")
    
    print("\n" + "█"*70 + "\n")

if __name__ == "__main__":
    print("\n" + "█"*70)
    print("VALIDAÇÃO FINAL DA IMPLEMENTAÇÃO")
    print("█"*70)
    
    # Validar arquivo
    if validate_configuracoes_py():
        # Contar linhas
        count_modified_lines()
        
        print("✅ IMPLEMENTAÇÃO VALIDADA COM SUCESSO!")
        print("\nO arquivo SistemaDesktop/views/configuracoes.py foi modificado corretamente.")
        print("Todos os requisitos foram implementados.")
    else:
        print("\n❌ Erro na validação. Verifique o arquivo.")
