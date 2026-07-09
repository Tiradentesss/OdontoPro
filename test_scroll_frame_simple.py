"""
Teste super simples: Renderizar widgets no ScrollableFrame com grid.
"""

import customtkinter as ctk

COLORS = {
    "card": "#f5f5f5",
    "input_bg": "#ffffff",
    "hover": "#e0e0e0",
    "text": "#000000",
}

root = ctk.CTk()
root.geometry("500x600")
root.title("Teste: CTkScrollableFrame + grid rendering")

print("[TESTE] Criando scrollable frame...")

scroll_frame = ctk.CTkScrollableFrame(
    root,
    height=400,
    fg_color=COLORS["card"],
    corner_radius=8
)
scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

print("[TESTE] ScrollableFrame criado")

# Simular 3 pacientes
pacientes = [
    (1, "João da Silva", "12345678901"),
    (2, "Maria Santos", "98765432109"),
    (3, "Pedro Oliveira", "55555555555"),
]

print(f"[TESTE] Criando {len(pacientes)} widgets com grid()...")

widgets_criados = 0
for indice, (id_pac, nome, cpf) in enumerate(pacientes):
    try:
        cpf_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        bg_color = COLORS["hover"] if indice == 0 else COLORS["input_bg"]
        
        # Frame
        item_frame = ctk.CTkFrame(
            scroll_frame,
            fg_color=bg_color,
            corner_radius=6,
            height=60
        )
        item_frame.grid(row=indice, column=0, sticky="ew", padx=2, pady=2, ipady=6)
        item_frame.columnconfigure(0, weight=1)
        
        # Label
        info_text = f"{nome}\nCPF: {cpf_fmt}"
        label = ctk.CTkLabel(
            item_frame,
            text=info_text,
            text_color=COLORS["text"],
            anchor="w",
            justify="left",
            font=("Arial", 10)
        )
        label.grid(row=0, column=0, sticky="ew", padx=12, pady=6)
        
        widgets_criados += 1
        print(f"  ✓ Widget {indice}: {nome}")
        
    except Exception as e:
        print(f"  ✗ Erro: {e}")

scroll_frame.columnconfigure(0, weight=1)

print(f"[TESTE] ✓ Total criado: {widgets_criados}")
print(f"[TESTE] Rodando janela por 5 segundos...")

root.after(5000, root.destroy)
root.mainloop()

print("[TESTE] ✓ Concluído")
