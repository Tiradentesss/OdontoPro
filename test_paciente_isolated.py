"""
Teste isolado do PacienteSearchComboBox.
Simula um paciente selecionado sem a necessidade de login ou banco full.
"""

import sys
import os

# Adicionar path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'SistemaDesktop'))

import customtkinter as ctk
from views.theme import COLORS, font

# Mock do ConsultaController para não precisar de BD real
class MockConsultaController:
    @staticmethod
    def buscar_pacientes_dinamico(termo, limite=20):
        """Retorna pacientes simulados."""
        pacientes_banco = [
            (1, "João da Silva", "12345678901", "joao@email.com", "11999999999", "1990-01-01"),
            (2, "João Santos", "98765432109", "joao.santos@email.com", "11888888888", "1985-05-15"),
            (3, "Maria Oliveira", "55555555555", "maria@email.com", "11777777777", "1992-03-20"),
            (4, "Pedro Costa", "12121212121", "pedro@email.com", "11666666666", "1988-07-10"),
            (5, "Ana Silva", "32323232323", "ana@email.com", "11555555555", "1995-11-25"),
        ]
        
        if not termo or len(termo) < 2:
            return []
        
        termo_lower = termo.lower()
        resultado = [p for p in pacientes_banco if termo_lower in p[1].lower() or termo_lower in p[2]]
        return resultado[:limite]

# Substituir no módulo views
sys.modules['controllers.consulta_controller'] = type(sys)('controllers.consulta_controller')
sys.modules['controllers.consulta_controller'].ConsultaController = MockConsultaController

# Agora importar o componente
from views.paciente_search_combo import PacienteSearchComboBox

# Criar janela de teste
root = ctk.CTk()
root.geometry("600x500")
root.title("Teste: PacienteSearchComboBox com dados simulados")

print("=" * 60)
print("TESTE ISOLADO: PacienteSearchComboBox")
print("=" * 60)

# Variável para armazenar seleção
paciente_selecionado = {'id': None, 'dados': None}

def ao_selecionar_paciente(id_pac, nome, cpf, email, telefone, data_nasc):
    """Callback quando paciente é selecionado."""
    paciente_selecionado['id'] = id_pac
    paciente_selecionado['dados'] = (id_pac, nome, cpf, email, telefone, data_nasc)
    print(f"[CALLBACK] ✓ Paciente selecionado: {nome} (ID: {id_pac})")

# Label
label = ctk.CTkLabel(
    root,
    text="👤 Paciente*",
    font=font("subtitle"),
    text_color=COLORS['text_primary']
)
label.pack(anchor='w', padx=15, pady=(15, 5))

# Componente PacienteSearchComboBox
print("\n[TESTE] Criando PacienteSearchComboBox...")
paciente_combo = PacienteSearchComboBox(
    root,
    height=40,
    fg_color=COLORS['input_bg'],
    border_color=COLORS['border'],
    corner_radius=8,
    command=ao_selecionar_paciente,
    placeholder_text="Selecione um paciente"
)
paciente_combo.pack(fill='x', padx=15, pady=(0, 20))
print("[TESTE] ✓ PacienteSearchComboBox criado")

# Info label
info_label = ctk.CTkLabel(
    root,
    text="Digite 2+ caracteres na caixa acima para pesquisar.\nExemplos: 'jo', 'maria', '123'",
    text_color=COLORS['text_muted'],
    font=("Arial", 10)
)
info_label.pack(anchor='w', padx=15, pady=(0, 20))

# Frame de resultado
result_frame = ctk.CTkFrame(root, fg_color=COLORS['card'], corner_radius=8)
result_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))

result_label = ctk.CTkLabel(
    result_frame,
    text="Selecione um paciente para ver os dados aqui...",
    text_color=COLORS['text_muted'],
    anchor="nw",
    justify="left",
    wraplength=300
)
result_label.pack(fill='both', expand=True, padx=15, pady=15)

def atualizar_resultado():
    """Atualiza a label de resultado."""
    if paciente_selecionado['dados']:
        id_pac, nome, cpf, email, telefone, data_nasc = paciente_selecionado['dados']
        cpf_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        texto = f"""ID: {id_pac}
Nome: {nome}
CPF: {cpf_fmt}
Email: {email}
Telefone: {telefone}
Data de Nascimento: {data_nasc}"""
        result_label.configure(text=texto, text_color=COLORS['text'])
    
    # Próxima verificação
    root.after(100, atualizar_resultado)

atualizar_resultado()

print("\n[TESTE] Janela rodando - teste manual")
print("[TESTE] 1. Clique no campo 'Selecione um paciente'")
print("[TESTE] 2. Digite 'jo' ou 'maria' na caixa de pesquisa")
print("[TESTE] 3. Selecione um paciente da lista")
print("[TESTE] 4. Verifique os dados aparecem abaixo")
print("\n" + "=" * 60)

root.mainloop()

print("\n[TESTE] Janela fechada")
print(f"[TESTE] Último paciente selecionado: {paciente_selecionado['dados']}")
print("=" * 60)
