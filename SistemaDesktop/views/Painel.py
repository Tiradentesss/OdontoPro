from .base import BaseScreen
import customtkinter as ctk
from .theme import font, ICON_SIZE
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Painel(BaseScreen):

    def __init__(self, parent):
        super().__init__(parent, "Painel")

        self.main_container = ctk.CTkFrame(
            self.content_card,
            fg_color="#F1F5F9", 
            corner_radius=0
        )
        self.main_container.pack(expand=True, fill="both")

        self.main_container.grid_columnconfigure((0, 1), weight=1, uniform="equal")
        self.main_container.grid_rowconfigure((0, 1), weight=1, uniform="equal")

        self.style = {
            "fg_color": "#FFFFFF",
            "corner_radius": 20,
            "border_width": 1,
            "border_color": "#E2E8F0"
        }

        self.setup_consultas()
        self.setup_performance()
        self.setup_pacientes()
        self.setup_financeiro()

    # --------------------------------------------------
    # HELPERS DE DESIGN E GRÁFICOS
    # --------------------------------------------------

    def create_card(self, row, column):
        card = ctk.CTkFrame(self.main_container, **self.style)
        card.grid(row=row, column=column, padx=12, pady=12, sticky="nsew")
        return card

    def create_header(self, parent, text):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 5))
        ctk.CTkLabel(header, text=text, font=font("subtitle", "bold"), text_color="#1E293B").pack(anchor="w")
        return header

    def embed_pie_chart(self, parent, values, labels, colors):
        """Gráfico ampliado com informações coladas (side-by-side)"""
        # Container centralizado para alinhar gráfico + legenda
        chart_container = ctk.CTkFrame(parent, fg_color="transparent")
        chart_container.pack(expand=True, fill="both", padx=10, pady=(0, 10))

        # Matplotlib Figure - Tamanho aumentado para 2.4x2.4
        fig, ax = plt.subplots(figsize=(2.4, 2.4), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        
        # Gráfico Donut
        wedges, texts, autotexts = ax.pie(
            values, 
            colors=colors, 
            startangle=90, 
            autopct='%1.0f%%',
            pctdistance=0.75, # % dentro do arco
            wedgeprops={'width': 0.5, 'edgecolor': 'white'},
            textprops={'color': "white", 'weight': 'bold', 'size': 9}
        )
        ax.axis('equal')

        # Canvas do Gráfico - Reduzi o padx lateral para aproximar da legenda
        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.config(bg='#FFFFFF', highlightthickness=0)
        canvas_widget.pack(side="left", expand=True, padx=(5, 0))

        # Legenda Lateral - Colada no gráfico
        legend_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        legend_frame.pack(side="left", fill="y", padx=(0, 15), pady=35)

        for label, color in zip(labels, colors):
            item = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item.pack(fill="x", pady=3)
            
            # Marcador
            ctk.CTkFrame(item, width=12, height=12, fg_color=color, corner_radius=3).pack(side="left", padx=(0, 6))
            # Texto
            ctk.CTkLabel(item, text=label, font=font("small", "bold"), text_color="#475569").pack(side="left")

        plt.close(fig)

    # --------------------------------------------------
    # SEÇÕES
    # --------------------------------------------------

    def setup_performance(self):
        card = self.create_card(0, 1)
        self.create_header(card, "📊 Status de Presença")
        
        self.embed_pie_chart(
            card, 
            [92, 8], 
            ["Presença", "Faltas"], 
            ["#10B981", "#F1F5F9"]
        )

    def setup_financeiro(self):
        card = self.create_card(1, 1)
        self.create_header(card, "💰 Origem da Receita")
        
        self.embed_pie_chart(
            card, 
            [60, 30, 10], 
            ["Convênio", "Particular", "Outros"], 
            ["#6366F1", "#818CF8", "#C7D2FE"]
        )
        
        # Valor total logo abaixo do gráfico para reforçar a informação
        ctk.CTkLabel(card, text="Total: R$ 12.450", font=font("text", "bold"), text_color="#1E293B").pack(pady=(0, 15))

    # Consultas e Pacientes (Mantidos conforme solicitado)
    def setup_consultas(self):
        card = self.create_card(0, 0)
        self.create_header(card, "📅 Próximas Consultas")
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for nome, hora, status in [("Victor Araújo", "09:00", "Confirmado"), ("Natália Silva", "12:00", "Pendente")]:
            item = ctk.CTkFrame(container, fg_color="#F8FAFC", corner_radius=12, height=54)
            item.pack(fill="x", pady=4); item.pack_propagate(False)
            ctk.CTkLabel(item, text=nome, font=font("text", "bold"), text_color="#334155").pack(side="left", padx=18)
            badge_bg = "#EEF2FF" if status == "Confirmado" else "#F1F5F9"
            ctk.CTkLabel(item, text=hora, font=font("small", "bold"), text_color="#4F46E5", fg_color=badge_bg, corner_radius=8, width=65, height=28).pack(side="right", padx=15)

    def setup_pacientes(self):
        card = self.create_card(1, 0)
        self.create_header(card, "👥 Novos Pacientes")
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=(0, 24))
        for p in ["Ana Costa", "Carlos Melo"]:
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=6)
            avatar = ctk.CTkLabel(row, text=p[0], width=40, height=40, fg_color="#F1F5F9", text_color="#6366F1", corner_radius=20, font=font("text", "bold"))
            avatar.pack(side="left")
            ctk.CTkLabel(row, text=p, font=font("text", "bold"), text_color="#334155").pack(side="left", padx=15)

    pass