from .base import BaseScreen
import customtkinter as ctk
from .theme import font, ICON_SIZE

class Financeiro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Financeiro")

        # MAIN CONTAINER - Seguindo padrão do Painel
        main_container = ctk.CTkFrame(self.content_card, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=25, pady=25)

        # =============================
        # CARDS DE RESUMO
        # =============================
        cards_container = ctk.CTkFrame(main_container, fg_color="transparent")
        cards_container.pack(fill="x", pady=(0, 25))
        
        # Configurar grid para 3 colunas iguais
        for i in range(3):
            cards_container.grid_columnconfigure(i, weight=1, uniform="cards")

        dados = [
            {"label": "Faturamento Mensal", "valor": "R$ 25.480", "cor": "#22C55E", "icone": "📈"},
            {"label": "Despesas", "valor": "R$ 9.320", "cor": "#EF4444", "icone": "📉"},
            {"label": "Lucro Líquido", "valor": "R$ 16.160", "cor": "#0EA5E9", "icone": "💰"},
        ]

        for i, item in enumerate(dados):
            card = self._criar_card_resumo(
                cards_container,
                icone=item["icone"],
                label=item["label"],
                valor=item["valor"],
                cor=item["cor"]
            )
            card.grid(row=0, column=i, padx=(0 if i == 0 else 15, 0 if i == 2 else 0), sticky="ew")

        # =============================
        # GRÁFICO SIMULADO
        # =============================
        grafico_card = ctk.CTkFrame(
            main_container,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        grafico_card.pack(fill="both", expand=True, pady=(0, 20))

        # Header do gráfico
        header = ctk.CTkFrame(grafico_card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header,
            text="📊 Fluxo de Caixa",
            font=font("subtitle", "bold")
        ).pack(side="left")

        # Seletor de período
        periodo_btn = ctk.CTkOptionMenu(
            header,
            values=["Últimos 30 dias", "Últimos 90 dias", "Este ano"],
            font=font("small"),
            fg_color="#F9FAFB",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            text_color="#111827",
            dropdown_fg_color="white",
            dropdown_text_color="#111827",
            dropdown_font=font("small"),
            width=120,
            height=30
        )
        periodo_btn.pack(side="right")
        periodo_btn.set("Últimos 30 dias")

        # Container do gráfico
        grafico_container = ctk.CTkFrame(grafico_card, fg_color="transparent")
        grafico_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Simulação de gráfico de barras
        barras_container = ctk.CTkFrame(grafico_container, fg_color="transparent")
        barras_container.pack(fill="x", pady=(20, 30))
        
        # Configurar grid para 7 colunas (dias da semana)
        for i in range(7):
            barras_container.grid_columnconfigure(i, weight=1)

        dias = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        valores = [85, 70, 95, 80, 90, 65, 55]  # Percentuais para as barras

        for i, (dia, valor) in enumerate(zip(dias, valores)):
            coluna = ctk.CTkFrame(barras_container, fg_color="transparent")
            coluna.grid(row=0, column=i, padx=5)
            
            # Barra
            barra_frame = ctk.CTkFrame(coluna, fg_color="transparent", height=150)
            barra_frame.pack(fill="x")
            
            barra = ctk.CTkFrame(
                barra_frame,
                fg_color="#0EA5E9",
                height=int(150 * (valor / 100)),
                width=30,
                corner_radius=4
            )
            barra.pack(side="bottom", pady=(0, 5))
            
            # Valor
            ctk.CTkLabel(
                coluna,
                text=f"R$ {valor*100}",
                font=font("small", "bold"),
                text_color="#0EA5E9"
            ).pack(pady=(5, 0))
            
            # Dia
            ctk.CTkLabel(
                coluna,
                text=dia,
                font=font("small"),
                text_color="#6B7280"
            ).pack()

        # =============================
        # TABELA DE ÚLTIMAS TRANSAÇÕES
        # =============================
        tabela_card = ctk.CTkFrame(
            main_container,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        tabela_card.pack(fill="x")

        # Header da tabela
        tabela_header = ctk.CTkFrame(tabela_card, fg_color="transparent")
        tabela_header.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            tabela_header,
            text="📋 Últimas Transações",
            font=font("subtitle", "bold")
        ).pack(side="left")

        # Botão ver todas
        ctk.CTkButton(
            tabela_header,
            text="Ver todas",
            font=font("small", "bold"),
            fg_color="transparent",
            text_color="#0EA5E9",
            hover_color="#F3F4F6",
            width=80,
            height=30,
            corner_radius=5
        ).pack(side="right")

        # Linha divisória
        divider = ctk.CTkFrame(tabela_card, height=1, fg_color="#E5E7EB")
        divider.pack(fill="x")

        # Cabeçalhos da tabela
        headers_frame = ctk.CTkFrame(tabela_card, fg_color="#F9FAFB", height=40)
        headers_frame.pack(fill="x")
        headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers = ["Data", "Descrição", "Tipo", "Valor"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                headers_frame,
                text=header,
                font=font("small", "bold"),
                text_color="#374151"
            ).grid(row=0, column=i, padx=20, pady=10, sticky="w")

        # Linhas da tabela
        transacoes = [
            {"data": "15/03/2024", "descricao": "Consulta - Victor Araújo", "tipo": "Receita", "valor": "R$ 250,00", "cor": "#22C55E"},
            {"data": "15/03/2024", "descricao": "Compra de materiais", "tipo": "Despesa", "valor": "R$ 450,00", "cor": "#EF4444"},
            {"data": "14/03/2024", "descricao": "Consulta - Natália Silva", "tipo": "Receita", "valor": "R$ 300,00", "cor": "#22C55E"},
            {"data": "14/03/2024", "descricao": "Pagamento fornecedor", "tipo": "Despesa", "valor": "R$ 1.200,00", "cor": "#EF4444"},
            {"data": "13/03/2024", "descricao": "Procedimento - Hugo Pontes", "tipo": "Receita", "valor": "R$ 800,00", "cor": "#22C55E"},
        ]

        for i, trans in enumerate(transacoes):
            # Linha alternada para melhor legibilidade
            bg_color = "white" if i % 2 == 0 else "#F9FAFB"
            
            linha = ctk.CTkFrame(tabela_card, fg_color=bg_color, height=45)
            linha.pack(fill="x")
            linha.grid_columnconfigure((0, 1, 2, 3), weight=1)

            # Data
            ctk.CTkLabel(
                linha,
                text=trans["data"],
                font=font("small"),
                text_color="#6B7280"
            ).grid(row=0, column=0, padx=20, pady=12, sticky="w")

            # Descrição
            ctk.CTkLabel(
                linha,
                text=trans["descricao"],
                font=font("small"),
                text_color="#111827"
            ).grid(row=0, column=1, padx=20, pady=12, sticky="w")

            # Tipo
            tipo_frame = ctk.CTkFrame(linha, fg_color="transparent")
            tipo_frame.grid(row=0, column=2, padx=20, pady=12, sticky="w")
            
            tipo_label = ctk.CTkLabel(
                tipo_frame,
                text=trans["tipo"],
                font=font("small", "bold"),
                text_color="white",
                fg_color=trans["cor"],
                corner_radius=4,
                padx=8,
                pady=2
            )
            tipo_label.pack()

            # Valor
            ctk.CTkLabel(
                linha,
                text=trans["valor"],
                font=font("small", "bold"),
                text_color=trans["cor"]
            ).grid(row=0, column=3, padx=20, pady=12, sticky="w")

    def _criar_card_resumo(self, parent, icone, label, valor, cor):
        """Cria um card de resumo padronizado"""
        card = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E5E7EB"
        )
        
        # Container interno
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Linha superior com ícone e label
        linha_superior = ctk.CTkFrame(container, fg_color="transparent")
        linha_superior.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            linha_superior,
            text=icone,
            font=font("title"),
            width=30
        ).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(
            linha_superior,
            text=label,
            font=font("text"),
            text_color="#6B7280"
        ).pack(side="left")

        # Valor
        ctk.CTkLabel(
            container,
            text=valor,
            font=("Poppins", 24, "bold"),
            text_color=cor
        ).pack(anchor="w")

        return card