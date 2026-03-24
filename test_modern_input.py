#!/usr/bin/env python3
"""Teste de ModernInput.set() funcionando corretamente"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

# Teste 1: Verificar se ModernInput.set() funciona
print("[TESTE] Verificando ModernInput.set() funcionamento...")

# Importar a classe ModernInput
from views.configuracoes import ModernInput
import customtkinter as ctk

# Criar uma janela de teste
root = ctk.CTk()
root.geometry("400x300")

# Criar um ModernInput
test_input = ModernInput(root, label="Nome de Teste", placeholder="Digite aqui", required=True)
test_input.pack(pady=20)

# Testar set() com um valor
test_value = "Clínica Odonto Floress"
print(f"[TESTE] Tentando setar valor: '{test_value}'")

try:
    test_input.set(test_value)
    retrieved_value = test_input.get()
    print(f"[TESTE] Valor setado com sucesso!")
    print(f"[TESTE] Valor recuperado: '{retrieved_value}'")
    if retrieved_value == test_value:
        print(f"[✓] SUCCESS: Valor corresponde!")
    else:
        print(f"[✗] ERRO: Valor não corresponde! Recebido: '{retrieved_value}'")
except Exception as e:
    print(f"[✗] ERRO ao chamar set(): {e}")
    import traceback
    traceback.print_exc()

# Manter a janela aberta por um momento
root.after(2000, root.quit)
root.mainloop()

print("[TESTE] Teste finalizado")
