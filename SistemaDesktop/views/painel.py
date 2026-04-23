from .base import BaseScreen
import customtkinter as ctk
from .theme import font, ICON_SIZE, COLORS

class Painel(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Painel")

        dashboard = ctk.CTkFrame(self.content_card, fg_color="transparent")
        dashboard.pack(expand=True, fill="both", padx=25, pady=25)

        dashboard.grid_columnconfigure((0, 1), weight=1)

        # ---- Próximas Consultas ----
        consultas = ctk.CTkFrame(
            dashboard,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        consultas.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        ctk.CTkLabel(
            consultas,
            text="Próximas Consultas",
            font=font("subtitle", "bold")
        ).pack(anchor="w", padx=20, pady=15)

        dados = [
            ("Victor Araújo", "Hoje • 09:00"),
            ("Natália Silva", "Hoje • 12:00"),
            ("Hugo Pontes", "Hoje • 14:30"),
        ]

        for nome, horario in dados:
            row = ctk.CTkFrame(consultas, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)

            ctk.CTkLabel(row, text=nome, font=font("text", "bold")).pack(anchor="w")
            ctk.CTkLabel(row, text=horario, text_color=COLORS["text_secondary"], font=font("small")).pack(anchor="w")

        # ---- Relatório ----
        relatorio = ctk.CTkFrame(
            dashboard,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        relatorio.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(
            relatorio,
            text="Relatório",
            font=font("subtitle", "bold")
        ).pack(anchor="w", padx=20, pady=15)

        progresso = ctk.CTkProgressBar(
            relatorio,
            width=220,
            height=14,
            progress_color=COLORS["warning"]
        )
        progresso.set(0.92)
        progresso.pack(pady=25)

        ctk.CTkLabel(
            relatorio,
            text="92% de comparecimento",
            font=font("text", "bold")
        ).pack(pady=(0, 10))

        legendas = [
            ("Agendados", "#22C55E"),
            ("Atendidos", "#FACC15"),
            ("Primeira vez", "#0EA5E9"),
            ("Faltas", "#A78BFA"),
        ]

        legenda_cores = [
            ("Agendados", COLORS["success"]),
            ("Atendidos", COLORS["warning"]),
            ("Primeira vez", COLORS["primary"]),
            ("Faltas", COLORS["secondary"]),
        ]

        for texto, cor in legenda_cores:
            item = ctk.CTkFrame(relatorio, fg_color="transparent")
            item.pack(anchor="w", padx=20, pady=4)

            ctk.CTkLabel(item, text="●", text_color=cor, font=font("text")).pack(side="left")
            ctk.CTkLabel(item, text=f" {texto}", text_color=COLORS["text_secondary"], font=font("text")).pack(side="left")
    pass
