from .base import BaseScreen
import customtkinter as ctk

# 🔽 IMPORTA DO MODELS
from models.data import (
    LIMITE_CONSULTAS,
    CONSULTAS_DATA,
    STATUS_COLORS
)


class Agenda(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Agenda")

        self.pagina_atual = 0

        self.render()

    def render(self):
        for w in self.content_card.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(self.content_card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=25)

        # ---------- TABELA ----------
        table = ctk.CTkFrame(container, fg_color="transparent")
        table.pack(fill="both", expand=True)

        headers = ["Paciente", "Data", "Horário", "Status"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=h,
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            ).grid(row=0, column=i, sticky="w", padx=20, pady=(0, 10))

        inicio = self.pagina_atual * LIMITE_CONSULTAS
        fim = inicio + LIMITE_CONSULTAS
        dados = CONSULTAS_DATA[inicio:fim]

        for r, (nome, data, hora, status) in enumerate(dados, start=1):
            ctk.CTkLabel(
                table,
                text=nome,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=r, column=0, sticky="w", padx=20, pady=14)

            ctk.CTkLabel(table, text=data).grid(row=r, column=1, sticky="w", padx=20)
            ctk.CTkLabel(table, text=hora).grid(row=r, column=2, sticky="w", padx=20)

            info = STATUS_COLORS[status]
            badge = ctk.CTkFrame(
                table,
                fg_color=info["bg"],
                corner_radius=6
            )
            badge.grid(row=r, column=3, sticky="w", padx=20)

            ctk.CTkLabel(
                badge,
                text=status,
                text_color=info["text"],
                font=ctk.CTkFont(size=11, weight="bold"),
                padx=10,
                pady=3
            ).pack()

        # ---------- PAGINAÇÃO ----------
        pag = ctk.CTkFrame(container, fg_color="transparent")
        pag.pack(anchor="e", pady=(20, 0))

        total_paginas = (len(CONSULTAS_DATA) + LIMITE_CONSULTAS - 1) // LIMITE_CONSULTAS

        def btn(text, ativo=False, cmd=None):
            return ctk.CTkButton(
                pag,
                text=text,
                width=32,
                height=32,
                corner_radius=6,
                fg_color="#0d99c7" if ativo else "#F3F4F6",
                text_color="white" if ativo else "#6B7280",
                hover_color="#0b86af",
                command=cmd
            )

        if self.pagina_atual > 0:
            btn("‹", cmd=lambda: self.trocar_pagina(self.pagina_atual - 1)).pack(side="left", padx=4)

        for i in range(total_paginas):
            btn(
                str(i + 1),
                ativo=i == self.pagina_atual,
                cmd=lambda idx=i: self.trocar_pagina(idx)
            ).pack(side="left", padx=4)

        if self.pagina_atual < total_paginas - 1:
            btn("›", cmd=lambda: self.trocar_pagina(self.pagina_atual + 1)).pack(side="left", padx=4)

    def trocar_pagina(self, pagina):
        self.pagina_atual = pagina
        self.render()
    pass
