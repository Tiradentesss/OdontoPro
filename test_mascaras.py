#!/usr/bin/env python3
"""
Script de teste para as máscaras de digitação.
Testa as funções de formatação sem necessidade de interface gráfica.
"""

from SistemaDesktop.services.mascaras_service import MascarasService


def teste_cpf():
    """Testa formatação de CPF."""
    print("\n" + "="*60)
    print("TESTE: CPF (000.000.000-00)")
    print("="*60)
    
    casos = [
        ("1", "1"),
        ("12", "12"),
        ("123", "123"),
        ("1234", "123.4"),
        ("12345", "123.45"),
        ("123456", "123.456"),
        ("1234567", "123.456.7"),
        ("12345678", "123.456.78"),
        ("123456789", "123.456.789"),
        ("1234567890", "123.456.789-0"),
        ("12345678901", "123.456.789-01"),
        ("123456789012", "123.456.789-01"),  # Excesso - deve limitar
    ]
    
    todos_passaram = True
    for entrada, esperado in casos:
        resultado, _ = MascarasService.formatar_cpf(entrada)
        status = "✅" if resultado == esperado else "❌"
        if resultado != esperado:
            todos_passaram = False
        print(f"{status} Entrada: {entrada:12} → Resultado: {resultado:20} (Esperado: {esperado})")
    
    return todos_passaram


def teste_data():
    """Testa formatação de Data."""
    print("\n" + "="*60)
    print("TESTE: DATA (DD/MM/AAAA)")
    print("="*60)
    
    casos = [
        ("1", "1"),
        ("12", "12"),
        ("120", "12/0"),
        ("1205", "12/05"),
        ("12052", "12/05/2"),
        ("120520", "12/05/20"),
        ("1205200", "12/05/200"),
        ("12052000", "12/05/2000"),
        ("120520001", "12/05/2000"),  # Excesso - deve limitar
    ]
    
    todos_passaram = True
    for entrada, esperado in casos:
        resultado, _ = MascarasService.formatar_data(entrada)
        status = "✅" if resultado == esperado else "❌"
        if resultado != esperado:
            todos_passaram = False
        print(f"{status} Entrada: {entrada:12} → Resultado: {resultado:20} (Esperado: {esperado})")
    
    return todos_passaram


def teste_telefone():
    """Testa formatação de Telefone."""
    print("\n" + "="*60)
    print("TESTE: TELEFONE (10 ou 11 dígitos)")
    print("="*60)
    
    casos = [
        ("1", "(1"),
        ("12", "(12"),
        ("123", "(12) 3"),
        ("1234", "(12) 34"),
        ("12345", "(12) 345"),
        ("123456", "(12) 3456"),
        ("1234567", "(12) 34567"),  # 7 dígitos, sem hífen ainda
        ("12345678", "(12) 345678"), # 8 dígitos, sem hífen ainda
        ("1234567890", "(12) 3456-7890"),  # 10 dígitos - fixo
        ("12345678901", "(12) 34567-8901"),  # 11 dígitos - celular
        ("123456789012", "(12) 34567-8901"),  # Excesso - deve limitar
    ]
    
    todos_passaram = True
    for entrada, esperado in casos:
        resultado, _ = MascarasService.formatar_telefone(entrada)
        status = "✅" if resultado == esperado else "❌"
        if resultado != esperado:
            todos_passaram = False
        print(f"{status} Entrada: {entrada:12} → Resultado: {resultado:20} (Esperado: {esperado})")
    
    return todos_passaram


def teste_extracoes():
    """Testa extração de números."""
    print("\n" + "="*60)
    print("TESTE: EXTRAÇÃO DE NÚMEROS")
    print("="*60)
    
    casos = [
        ("123.456.789-01", "12345678901"),  # CPF formatado
        ("12/05/2000", "12052000"),         # Data formatada
        ("(12) 34567-8901", "12345678901"), # Telefone formatado
        ("abc123def456", "123456"),         # Misto
        ("", ""),                            # Vazio
    ]
    
    todos_passaram = True
    for entrada, esperado in casos:
        resultado = MascarasService.extrair_numeros(entrada)
        status = "✅" if resultado == esperado else "❌"
        if resultado != esperado:
            todos_passaram = False
        print(f"{status} Entrada: {entrada:25} → Resultado: {resultado:15} (Esperado: {esperado})")
    
    return todos_passaram


def main():
    """Executa todos os testes."""
    print("\n" + "🧪 TESTES DE MÁSCARAS DE DIGITAÇÃO".center(60, "="))
    
    resultados = {
        "CPF": teste_cpf(),
        "DATA": teste_data(),
        "TELEFONE": teste_telefone(),
        "EXTRAÇÃO": teste_extracoes(),
    }
    
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    for nome, passou in resultados.items():
        status = "✅ PASSOU" if passou else "❌ FALHOU"
        print(f"{status}: {nome}")
    
    todos_passaram = all(resultados.values())
    
    print("\n" + "="*60)
    if todos_passaram:
        print("✅ TODOS OS TESTES PASSARAM!".center(60))
    else:
        print("❌ ALGUNS TESTES FALHARAM!".center(60))
    print("="*60 + "\n")
    
    return todos_passaram


if __name__ == "__main__":
    main()
