import customtkinter as ctk
from PIL import Image

# Configurações de aparência
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class OdontoProApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("OdontoPro - Sistema de Gerenciamento")
        self.geometry("1100 objetivos x 700")
        self.configure(fg_color="#F0F2F5") # Cor de fundo da imagem

        # Configuração de Grid Principal (Sidebar | Conteúdo)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_content()

    def setup_sidebar(self):
        # Frame da Barra Lateral
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="white", border_width=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Espaço para o botão sair no fundo

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="OdontoPro", 
                                       font=ctk.CTkFont(size=22, weight="bold"), text_color="#00B4D8")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 5))
        
        self.sub_logo = ctk.CTkLabel(self.sidebar_frame, text="SISTEMA DE GERENCIAMENTO", 
                                     font=ctk.CTkFont(size=9), text_color="gray")
        self.sub_logo.grid(row=1, column=0, padx=20, pady=(0, 40))

        # Menu de Navegação
        menu_items = [
            ("Painel", True),
            ("Agendamento", False),
            ("Meus Pacientes", False),
            ("Relatório", False),
            ("Mensagens", False),
            ("Configuração", False)
        ]

        for i, (item, active) in enumerate(menu_items):
            fg_color = "#E0F7FA" if active else "transparent"
            text_color = "#00B4D8" if active else "#A0A0A0"
            
            btn = ctk.CTkButton(self.sidebar_frame, text=item, corner_radius=10, height=40,
                                fg_color=fg_color, text_color=text_color, 
                                hover_color="#F0F0F0", anchor="w", font=ctk.CTkFont(size=13, weight="bold" if active else "normal"))
            btn.grid(row=i+2, column=0, padx=20, pady=5, sticky="ew")

        # Botão Sair
        self.exit_btn = ctk.CTkButton(self.sidebar_frame, text="Sair", fg_color="transparent", 
                                      text_color="gray", anchor="w", hover_color="#FEEBEB")
        self.exit_btn.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

    def setup_main_content(self):
        # Frame Principal (Direita)
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=30, pady=20)
        self.main_view.grid_columnconfigure((0, 1, 2), weight=1)
        self.main_view.grid_rowconfigure((1, 2), weight=1)

        # --- HEADER ---
        self.header_label = ctk.CTkLabel(self.main_view, text="Olá, Lucas 👋", 
                                         font=ctk.CTkFont(size=24, weight="bold"), text_color="#00B4D8")
        self.header_label.grid(row=0, column=0, sticky="nw", pady=(0, 20))

        # --- LINHA 1: Próximas Consultas e Relatório ---
        # Card Próximas Consultas
        self.consultas_card = self.create_card(self.main_view, "Próximas Consultas", row=1, col=0, colspan=2)
        self.add_appointment_item(self.consultas_card, "Victor Araujo", "Hoje as 09:00 - 09:30AM", 0)
        self.add_appointment_item(self.consultas_card, "Natália Silva", "Hoje as 12:00 - 12:30AM", 1)
        self.add_appointment_item(self.consultas_card, "Hugo Pontes", "Hoje as 14:00 - 14:30PM", 2)

        # Card Relatório (Espaço para Gráfico Pizza/Donut)
        self.relatorio_card = self.create_card(self.main_view, "Relatório", row=1, col=2)
        self.graph_placeholder(self.relatorio_card, "Espaço para Gráfico de Rosca (92%)")

        # --- LINHA 2: Consultas Agendadas, Pacientes Recentes e Faturamento ---
        # Card Consultas Agendadas (Número Grande)
        self.agendadas_card = self.create_card(self.main_view, "Consultas Agendadas", row=2, col=0)
        ctk.CTkLabel(self.agendadas_card, text="12", font=ctk.CTkFont(size=48, weight="bold"), 
                     text_color="#00B4D8").pack(pady=(20, 0))
        ctk.CTkLabel(self.agendadas_card, text="Somente este Mês", font=ctk.CTkFont(size=12), 
                     text_color="gray").pack()

        # Card Pacientes Recentes
        self.pacientes_card = self.create_card(self.main_view, "Pacientes Recentes", row=2, col=1)
        self.add_patient_item(self.pacientes_card, "Bruno Martins", "bruno.martins@gmail.com", 0)
        self.add_patient_item(self.pacientes_card, "Camila Rocha", "camila.rocha@gmail.com", 1)
        self.add_patient_item(self.pacientes_card, "Felipe Andrade", "felipe.andrade@gmail.com", 2)

        # Card Faturamento (Espaço para Gráfico de Linha)
        self.faturamento_card = self.create_card(self.main_view, "Faturamento", row=2, col=2)
        self.graph_placeholder(self.faturamento_card, "Espaço para Gráfico de Linhas")

    def create_card(self, parent, title, row, col, colspan=1):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=20)
        card.grid(row=row, column=col, columnspan=colspan, padx=10, pady=10, sticky="nsew")
        
        label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"))
        label.pack(anchor="nw", padx=20, pady=15)
        
        return card

    def add_appointment_item(self, parent, name, time, idx):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=20, pady=5)
        
        # Placeholder para Avatar
        avatar = ctk.CTkFrame(item_frame, width=35, height=35, corner_radius=17, fg_color="#00B4D8")
        avatar.pack(side="left", padx=(0, 10))
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left")
        
        ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(size=13, weight="bold"), text_color="#00B4D8").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=time, font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w")

    def add_patient_item(self, parent, name, email, idx):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(fill="x", padx=20, pady=2)
        
        avatar = ctk.CTkFrame(item_frame, width=30, height=30, corner_radius=15, fg_color="#E0E0E0")
        avatar.pack(side="left", padx=(0, 10))
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left")
        
        ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(size=12, weight="bold"), text_color="#00B4D8").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=email, font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w")

    def graph_placeholder(self, parent, text):
        # Frame cinza claro para simular onde o gráfico ficaria
        placeholder = ctk.CTkFrame(parent, fg_color="#F9F9F9", corner_radius=10)
        placeholder.pack(expand=True, fill="both", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(placeholder, text=text, text_color="silver", font=ctk.CTkFont(slant="italic")).place(relx=0.5, rely=0.5, anchor="center")

if __name__ == "__main__":
    app = OdontoProApp()
    app.mainloop()