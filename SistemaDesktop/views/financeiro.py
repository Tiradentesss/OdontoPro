from .base import BaseScreen
import customtkinter as ctk

class Financeiro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Financeiro")

        grid = ctk.CTkFrame(self.content_card, fg_color="transparent")
        grid.pack(padx=25, pady=25)

        dados = [
            ("Faturamento Mensal", "R$ 25.480", "#22C55E"),
            ("Despesas", "R$ 9.320", "#EF4444"),
            ("Lucro Líquido", "R$ 16.160", "#0EA5E9"),
        ]

        for i, (label, valor, cor) in enumerate(dados):
            card = ctk.CTkFrame(
                grid,
                fg_color="#F8FAFC",
                corner_radius=14,
                width=240,
                height=120
            )
            card.grid(row=0, column=i, padx=12)

            ctk.CTkLabel(card, text=label, text_color="#6B7280").pack(pady=(25, 5))
            ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20, weight="bold"), text_color=cor).pack()


    pass