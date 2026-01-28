import customtkinter as ctk

# =====================
# CONFIGURAÇÃO GERAL
# =====================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("OdontoPro - Agendamentos")
app.geometry("1200x720")
app.configure(fg_color="#F5F7FB")

# =====================
# CORES
# =====================
WHITE = "#FFFFFF"
PRIMARY = "#2563EB"
TEXT = "#1F2937"
SOFT = "#6B7280"

STATUS_COLORS = {
    "Confirmado": "#22C55E",
    "Não Confirmado": "#EF4444",
    "Reagendado": "#3B82F6"
}

# =====================
# LAYOUT PRINCIPAL
# =====================
main = ctk.CTkFrame(app, fg_color="transparent")
main.pack(expand=True, fill="both")

# =====================
# SIDEBAR
# =====================
sidebar = ctk.CTkFrame(main, width=210, fg_color=WHITE)
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(
    sidebar,
    text="OdontoPro",
    font=("Arial", 20, "bold"),
    text_color=PRIMARY
).pack(pady=(30, 40))

menu_items = ["Painel", "Agendamento", "Meus Pacientes", "Relatório", "Configuração"]

for item in menu_items:
    ctk.CTkButton(
        sidebar,
        text=item,
        fg_color="transparent",
        hover_color="#EEF2FF",
        text_color=TEXT,
        anchor="w",
        height=42
    ).pack(fill="x", padx=20, pady=4)

ctk.CTkButton(
    sidebar,
    text="Sair",
    fg_color="transparent",
    hover_color="#FEE2E2",
    text_color="#DC2626"
).pack(side="bottom", pady=20)

# =====================
# CONTEÚDO
# =====================
content = ctk.CTkFrame(main, fg_color="transparent")
content.pack(expand=True, fill="both", padx=35, pady=25)

# HEADER
header = ctk.CTkFrame(content, fg_color="transparent")
header.pack(fill="x", pady=(0, 20))

ctk.CTkLabel(
    header,
    text="Olá Lucas 👋",
    font=("Arial", 22, "bold"),
    text_color=PRIMARY
).pack(side="left")

# =====================
# CARD PRINCIPAL
# =====================
card = ctk.CTkFrame(content, fg_color=WHITE, corner_radius=18)
card.pack(expand=True, fill="both")

ctk.CTkLabel(
    card,
    text="Consultas da Semana",
    font=("Arial", 18, "bold"),
    text_color=TEXT
).pack(anchor="w", padx=25, pady=(20, 10))

# =====================
# TABELA
# =====================
table = ctk.CTkFrame(card, fg_color="transparent")
table.pack(fill="both", expand=True, padx=25)

headers = ["Paciente", "Data", "Horário", "Status"]

for col, h in enumerate(headers):
    ctk.CTkLabel(
        table,
        text=h,
        font=("Arial", 13),
        text_color=SOFT
    ).grid(row=0, column=col, sticky="w", pady=(0, 12))

# =====================
# FUNÇÕES FUTURAS (MYSQL)
# =====================
def carregar_consultas():
    """
    Futuramente:
    - Buscar dados do MySQL
    - Retornar lista de tuplas
    """
    return [
        ("Victor Araújo", "14/12/2025", "09:30", "Confirmado"),
        ("Natália Silva", "15/12/2025", "12:00", "Não Confirmado"),
        ("Ronald Richards", "18/12/2025", "08:00", "Reagendado"),
        ("Marvin McKinney", "16/12/2025", "11:45", "Confirmado"),
        ("Jerome Bell", "16/12/2025", "14:00", "Confirmado"),
        ("Kathryn Murphy", "17/12/2025", "07:30", "Confirmado"),
        ("Jacob Jones", "17/12/2025", "09:45", "Confirmado"),
        ("Kristin Watson", "17/12/2025", "10:00", "Confirmado"),
    ]

def renderizar_consultas(dados):
    for row, consulta in enumerate(dados, start=1):
        paciente, data, hora, status = consulta

        ctk.CTkLabel(
            table,
            text=paciente,
            text_color=TEXT
        ).grid(row=row, column=0, sticky="w", pady=8)

        ctk.CTkLabel(
            table,
            text=data,
            text_color=TEXT
        ).grid(row=row, column=1, sticky="w")

        ctk.CTkLabel(
            table,
            text=hora,
            text_color=TEXT
        ).grid(row=row, column=2, sticky="w")

        ctk.CTkLabel(
            table,
            text=status,
            fg_color=STATUS_COLORS[status],
            corner_radius=6,
            text_color="white",
            font=("Arial", 12),
            padx=10,
            pady=4
        ).grid(row=row, column=3, sticky="w")

# =====================
# RENDER
# =====================
consultas = carregar_consultas()
renderizar_consultas(consultas)

app.mainloop()