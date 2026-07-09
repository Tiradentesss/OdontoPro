"""
Script de teste isolado para PacienteSearchComboBox.
Testa cada etapa: consulta BD, criação widgets, renderização.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

from controllers.consulta_controller import ConsultaController
from config.database import get_connection

print("=" * 60)
print("TESTE: PacienteSearchComboBox - Diagnóstico")
print("=" * 60)

# ========== PASSO 1: Verificar conexão com BD ==========
print("\n[PASSO 1] Testando conexão com banco de dados...")
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM pacientes")
    total = cursor.fetchone()[0]
    print(f"✓ Conexão OK - Total de pacientes no BD: {total}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Erro de conexão: {e}")
    sys.exit(1)

# ========== PASSO 2: Testar busca de pacientes ==========
print("\n[PASSO 2] Testando ConsultaController.buscar_pacientes_dinamico()...")
termos_teste = ["jo", "silva", "maria"]

for termo in termos_teste:
    try:
        resultados = ConsultaController.buscar_pacientes_dinamico(termo, limite=20)
        print(f"  Termo '{termo}': {len(resultados)} resultados")
        if resultados:
            for idx, (id_pac, nome, cpf, email, telefone, data_nasc) in enumerate(resultados[:2]):
                print(f"    [{idx}] {nome} - CPF: {cpf}")
    except Exception as e:
        print(f"  ✗ Erro com termo '{termo}': {e}")

# ========== PASSO 3: Testar criação de widgets com grid ==========
print("\n[PASSO 3] Testando criação de widgets com grid()...")
import customtkinter as ctk
from views.theme import COLORS

root = ctk.CTk()
root.geometry("400x600")

try:
    # Criar ScrollableFrame
    scroll_frame = ctk.CTkScrollableFrame(
        root,
        height=400,
        fg_color=COLORS.get("card", "white"),
        corner_radius=8
    )
    scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    print(f"✓ CTkScrollableFrame criado")
    
    # Simular pacientes
    pacientes_simulados = [
        (1, "João da Silva", "12345678901", "joao@email.com", "11999999999", "1990-01-01"),
        (2, "Maria Santos", "98765432109", "maria@email.com", "11888888888", "1985-05-15"),
        (3, "Pedro Oliveira", "55555555555", "pedro@email.com", "11777777777", "1992-03-20"),
    ]
    
    widgets_criados = 0
    for indice, (id_pac, nome, cpf, email, telefone, data_nasc) in enumerate(pacientes_simulados):
        try:
            cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
            fg_color = COLORS.get("hover", "#e0e0e0") if indice == 0 else COLORS.get("input_bg", "white")
            
            # Frame para paciente
            paciente_item = ctk.CTkFrame(
                scroll_frame,
                fg_color=fg_color,
                corner_radius=6,
                height=60
            )
            paciente_item.grid(row=indice, column=0, sticky="ew", padx=2, pady=2, ipady=6)
            paciente_item.columnconfigure(0, weight=1)
            
            # Label com info
            info_text = f"{nome}\nCPF: {cpf_formatado}"
            info_label = ctk.CTkLabel(
                paciente_item,
                text=info_text,
                text_color=COLORS.get("text", "black"),
                anchor="w",
                justify="left",
                font=("Arial", 10)
            )
            info_label.grid(row=0, column=0, sticky="ew", padx=12, pady=6)
            
            widgets_criados += 1
            print(f"  ✓ Widget {indice}: {nome}")
            
        except Exception as e:
            print(f"  ✗ Erro ao criar widget {indice}: {e}")
    
    scroll_frame.columnconfigure(0, weight=1)
    
    print(f"\n✓ Total de widgets criados: {widgets_criados}")
    print(f"✓ Total de widgets no frame: {len(scroll_frame.winfo_children())}")
    
    # Mostrar janela por 3 segundos
    print("\n[PASSO 4] Exibindo janela de teste por 3 segundos...")
    root.after(3000, root.destroy)
    root.mainloop()
    
    print("✓ Teste visual concluído")
    
except Exception as e:
    print(f"✗ Erro ao criar widgets: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
