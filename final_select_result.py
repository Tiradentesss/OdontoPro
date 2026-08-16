"""
Script de verificação final - SELECT do banco de dados
"""
import sys
sys.path.insert(0, 'SistemaDesktop')

from config.database import get_connection

def final_database_check(clinica_id=1):
    """
    Executar SELECT final conforme solicitado no teste real
    """
    print("\n" + "█"*80)
    print("RESULTADO FINAL - SELECT DO BANCO DE DADOS")
    print("█"*80)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    print(f"\nExecutando:")
    print(f"SELECT id, clinica_id, imagem, ordem")
    print(f"FROM odontoPro_clinicaimagem")
    print(f"WHERE clinica_id = {clinica_id}")
    print(f"ORDER BY ordem;")
    
    print("\n" + "─"*80)
    
    cursor.execute("""
        SELECT id, clinica_id, imagem, ordem
        FROM odontoPro_clinicaimagem
        WHERE clinica_id = %s
        ORDER BY ordem
    """, (clinica_id,))
    
    results = cursor.fetchall()
    
    if results:
        print(f"\nRESULTADO: {len(results)} registro(s) encontrado(s)\n")
        
        print(f"{'ID':<5} {'CLINICA_ID':<15} {'ORDEM':<8} {'IMAGEM':<50}")
        print("─"*80)
        
        for row in results:
            row_id = row[0]
            row_clinica_id = row[1]
            row_ordem = row[3]
            row_imagem = row[2]
            
            # Truncar URL para exibir
            url_display = row_imagem[:50] + "..." if len(row_imagem) > 50 else row_imagem
            
            print(f"{row_id:<5} {row_clinica_id:<15} {row_ordem:<8} {url_display:<50}")
            print(f"       Full URL: {row_imagem}\n")
        
        print("─"*80)
        
        # Validações
        print("\nVALIDAÇÕES:")
        
        # 1. Verificar se todas as URLs começam com https://
        all_https = all(row[2].lower().startswith("https://") for row in results)
        print(f"  ✓ Todas as URLs começam com 'https://': {all_https}")
        
        # 2. Verificar se há exatamente 3 registros
        exactly_three = len(results) == 3
        print(f"  ✓ Exatamente 3 registros: {exactly_three}")
        
        # 3. Verificar se as ordens são 1, 2, 3
        orders = sorted([row[3] for row in results])
        correct_orders = orders == [1, 2, 3]
        print(f"  ✓ Ordens corretas (1, 2, 3): {correct_orders}")
        
        # 4. Verificar se não há duplicatas
        order_counts = {}
        for row in results:
            ordem = row[3]
            order_counts[ordem] = order_counts.get(ordem, 0) + 1
        no_duplicates = all(count == 1 for count in order_counts.values())
        print(f"  ✓ Sem duplicatas: {no_duplicates}")
        
        # 5. Verificar se todas pertencem à mesma clínica
        clinica_ids = set(row[1] for row in results)
        same_clinic = len(clinica_ids) == 1 and clinica_id in clinica_ids
        print(f"  ✓ Todos os registros pertencem à clinica_id={clinica_id}: {same_clinic}")
        
        print("\n" + "─"*80)
        
        # Resumo
        if all_https and exactly_three and correct_orders and no_duplicates and same_clinic:
            print("\n✓ RESULTADO ESPERADO ALCANÇADO - TUDO OK!")
        else:
            print("\n✗ Alguma validação falhou")
    else:
        print(f"\n✗ Nenhum registro encontrado para clinica_id={clinica_id}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "█"*80 + "\n")

if __name__ == "__main__":
    final_database_check(clinica_id=1)
