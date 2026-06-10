from .base import BaseScreen
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .theme import font, COLORS
from datetime import datetime, timedelta
from collections import defaultdict
from controllers.financeiro_controller import FinanceiroController


class Financeiro(BaseScreen):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, "Financeiro")

        self.clinica_id = clinica_id
        # Carrega transações do banco de dados
        self.transacoes = self._carregar_transacoes()

        self.main_container = ctk.CTkScrollableFrame(self.content_card, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.setup_ui()
    
    def _carregar_transacoes(self):
        """Carrega transações do banco de dados"""
        try:
            if not self.clinica_id:
                return []
            
            # Buscar todas as transações do mês
            data_inicio = datetime.now().replace(day=1)
            transacoes_db = FinanceiroController.listar_transacoes(
                self.clinica_id, 
                data_inicio=data_inicio
            )
            
            # Converter para o formato esperado (data_str, descricao, tipo, valor)
            transacoes_formatadas = []
            for trans in transacoes_db:
                if trans and isinstance(trans, dict):
                    data_str = trans.get('data', datetime.now()).strftime('%d/%m')
                    descricao = trans.get('descricao', 'Transação')
                    tipo = trans.get('tipo', 'receita')
                    valor = float(trans.get('valor', 0))
                    transacoes_formatadas.append((data_str, descricao, tipo, valor))
            
            return transacoes_formatadas if transacoes_formatadas else []
        
        except Exception as e:
            print(f"Erro ao carregar transações: {e}")
            return []

    def setup_ui(self):
        self.create_kpi_section()
        self.create_chart_section()
        self.create_transactions_section()

    def processar_transacoes_por_periodo(self, periodo):
        """Processa transações e agrupa por período"""
        transacoes_agrupadas = defaultdict(lambda: {"receita": 0, "despesa": 0})
        
        for data_str, descricao, tipo, valor in self.transacoes:
            try:
                data = datetime.strptime(data_str, "%d/%m")
                # Assumindo ano atual
                data = data.replace(year=datetime.now().year)
            except:
                continue
            
            if tipo.lower() == "receita":
                transacoes_agrupadas[data]["receita"] += valor
            else:
                transacoes_agrupadas[data]["despesa"] += valor
        
        # Gerar dados do gráfico baseado no período
        if periodo == "Últimos 7 dias":
            return self._gerar_dados_7_dias(transacoes_agrupadas)
        elif periodo == "Últimos 30 dias":
            return self._gerar_dados_30_dias(transacoes_agrupadas)
        elif periodo == "Este Ano":
            return self._gerar_dados_ano(transacoes_agrupadas)
        
        return self._gerar_dados_7_dias(transacoes_agrupadas)
    
    def _gerar_dados_7_dias(self, transacoes_agrupadas):
        """Gera dados para os últimos 7 dias"""
        hoje = datetime.now()
        datas = [(hoje - timedelta(days=i)).date() for i in range(6, -1, -1)]
        nomes_dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        
        receitas = []
        despesas = []
        
        for data in datas:
            data_obj = datetime.combine(data, datetime.min.time())
            if data_obj in transacoes_agrupadas:
                receitas.append(transacoes_agrupadas[data_obj]["receita"])
                despesas.append(transacoes_agrupadas[data_obj]["despesa"])
            else:
                receitas.append(0)
                despesas.append(0)
        
        return nomes_dias, receitas, despesas
    
    def _gerar_dados_30_dias(self, transacoes_agrupadas):
        """Gera dados para os últimos 30 dias agrupados por semana"""
        hoje = datetime.now()
        semanas_labels = ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
        receitas = [0, 0, 0, 0]
        despesas = [0, 0, 0, 0]
        
        for data_obj, valores in transacoes_agrupadas.items():
            dias_atras = (hoje.date() - data_obj.date()).days
            if dias_atras <= 30:
                semana_idx = min(dias_atras // 7, 3)
                receitas[3 - semana_idx] += valores["receita"]
                despesas[3 - semana_idx] += valores["despesa"]
        
        return semanas_labels, receitas, despesas
    
    def _gerar_dados_ano(self, transacoes_agrupadas):
        """Gera dados para o ano agrupados por mês"""
        meses_labels = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        receitas = [0] * 12
        despesas = [0] * 12
        
        for data_obj, valores in transacoes_agrupadas.items():
            mes_idx = data_obj.month - 1
            receitas[mes_idx] += valores["receita"]
            despesas[mes_idx] += valores["despesa"]
        
        return meses_labels, receitas, despesas
    
    def calcular_kpis(self):
        """Calcula os KPIs baseado nas transações"""
        total_receita = sum(valor for _, _, tipo, valor in self.transacoes if tipo.lower() == "receita")
        total_despesa = sum(valor for _, _, tipo, valor in self.transacoes if tipo.lower() == "despesa")
        lucro = total_receita - total_despesa
        
        return total_receita, total_despesa, lucro

    def create_kpi_section(self):
        total_receita, total_despesa, lucro = self.calcular_kpis()
        
        kpi_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 15))
        kpi_frame.columnconfigure((0, 1, 2), weight=1, uniform="a")

        # Definir cor do lucro baseado no valor (positivo = azul, negativo = vermelho)
        cor_lucro = COLORS["primary"] if lucro >= 0 else COLORS["danger"]

        kpis = [
            ("📊 Faturamento", f"R$ {total_receita:,.2f}".replace(",", "."), COLORS["primary"]),
            ("📉 Despesas", f"R$ {total_despesa:,.2f}".replace(",", "."), COLORS["danger"]),
            ("💰 Lucro", f"R$ {lucro:,.2f}".replace(",", "."), cor_lucro)
        ]

        for i, (title, value, color) in enumerate(kpis):
            card = ctk.CTkFrame(kpi_frame, fg_color=COLORS["card"], corner_radius=12,
                                border_width=1, border_color=COLORS["border"])
            card.grid(row=0, column=i, sticky="ew", padx=8)

            ctk.CTkLabel(card, text=title, font=font("small"),
                         text_color=COLORS["text_secondary"]).pack(anchor="w", padx=15, pady=(10, 2))

            ctk.CTkLabel(card, text=value, font=font("title", "bold"),
                         text_color=color).pack(anchor="w", padx=15, pady=(0, 10))

    def create_chart_section(self):
        container = ctk.CTkFrame(self.main_container, fg_color=COLORS["card"],
                                 corner_radius=12, border_width=1, border_color=COLORS["border"])
        container.pack(fill="x", pady=(0, 15))

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(header, text="📈 Entradas vs Saídas",
                     font=font("subtitle", "bold")).pack(side="left")

        periodos = ["Últimos 7 dias", "Últimos 30 dias", "Este Ano"]
        combo = ctk.CTkComboBox(header,
                                values=periodos,
                                command=self.update_chart,
                                width=140,
                                font=font("small"))
        combo.set("Últimos 7 dias")
        combo.pack(side="right")

        self.plot_area = ctk.CTkFrame(container, fg_color="transparent")
        self.plot_area.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        self.update_chart("Últimos 7 dias")

    def update_chart(self, selection):
        for widget in self.plot_area.winfo_children():
            widget.destroy()

        labels, receitas, despesas = self.processar_transacoes_por_periodo(selection)
        
        # Calcular valores formatados para o título
        total_receitas = sum(receitas)
        total_despesas = sum(despesas)
        lucro = total_receitas - total_despesas

        # Criar figura
        fig, ax = plt.subplots(figsize=(8, 3.5), dpi=100)
        fig.patch.set_facecolor(COLORS["card"])
        ax.set_facecolor(COLORS["card"])

        # Criar gráfico de linha com área preenchida
        x = range(len(labels))
        
        # Linha e área para Receitas (azul primário)
        ax.plot(x, receitas, marker='o', linewidth=2.5, markersize=6,
                color=COLORS["primary"], label='⬆️ Entradas', alpha=1)
        ax.fill_between(x, receitas, alpha=0.2, color=COLORS["primary"])
        
        # Linha e área para Despesas (vermelho)
        ax.plot(x, despesas, marker='s', linewidth=2.5, markersize=6,
                color=COLORS["danger"], label='⬇️ Saídas', alpha=1)
        ax.fill_between(x, despesas, alpha=0.2, color=COLORS["danger"])
        
        # Adicionar valores nos pontos com ajuste para valores negativos
        for i, (rec, desp) in enumerate(zip(receitas, despesas)):
            # Ajustar posição do texto da receita
            if rec > 0:
                y_offset_rec = 10
            else:
                y_offset_rec = -15
            
            # Ajustar posição do texto da despesa
            if desp > 0:
                y_offset_desp = -15
            else:
                y_offset_desp = 10
            
            # Só adiciona anotação se o valor não for zero
            if rec != 0:
                ax.annotate(f'R${rec:,.0f}'.replace(',', '.'), 
                           xy=(i, rec), xytext=(0, y_offset_rec),
                           textcoords="offset points", ha='center', fontsize=6.5,
                           color=COLORS["primary"], fontweight='bold')
            
            if desp != 0:
                ax.annotate(f'R${desp:,.0f}'.replace(',', '.'), 
                           xy=(i, desp), xytext=(0, y_offset_desp),
                           textcoords="offset points", ha='center', fontsize=6.5,
                           color=COLORS["danger"], fontweight='bold')
        
        # Configurar eixo X
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, color=COLORS["text_secondary"])
        
        # Ajustar limites do eixo Y para dar espaço para valores negativos
        y_min = min(min(receitas), min(despesas), 0)
        y_max = max(max(receitas), max(despesas), 0)
        y_range = y_max - y_min
        if y_range == 0:
            y_range = 100  # Valor padrão se todos os dados forem zero
        
        # Adicionar padding de 20% acima e abaixo
        ax.set_ylim(y_min - y_range * 0.2, y_max + y_range * 0.2)
        
        # Configurar eixo Y
        ax.yaxis.set_tick_params(labelsize=7, colors=COLORS["text_secondary"])
        
        # Formatar valores do eixo Y
        def format_y(value, _):
            if value >= 1000:
                return f'R${value/1000:.0f}K'
            return f'R${value:.0f}'
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_y))
        
        # Adicionar linha horizontal em zero para destacar valores negativos
        ax.axhline(y=0, color=COLORS["border"], linestyle='-', linewidth=0.8, alpha=0.5)
        
        # Remover spines desnecessários
        ax.spines[['top', 'right']].set_visible(False)
        ax.spines['left'].set_color(COLORS["border"])
        ax.spines['bottom'].set_color(COLORS["border"])
        
        # Adicionar grid sutil
        ax.grid(axis='y', alpha=0.3, color=COLORS["border"], linestyle='--', linewidth=0.5)
        ax.grid(axis='x', alpha=0.1, color=COLORS["border"], linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Adicionar título com resumo
        titulo = f'Total: R$ {total_receitas:,.0f} | Despesas: R$ {total_despesas:,.0f} | Lucro: R$ {lucro:,.0f}'
        titulo = titulo.replace(',', '.')
        ax.set_title(titulo, fontsize=8, color=COLORS["text_secondary"], pad=15, loc='center', fontweight='bold')
        
        # Legenda com cor adaptada ao tema
        legend = ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=False,
                          fontsize=7, facecolor=COLORS["card"], edgecolor=COLORS["border"])
        
        # Define a cor do texto da legenda conforme o tema
        for text in legend.get_texts():
            text.set_color(COLORS["text"])
        
        # Ajustar layout
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close(fig)

    def create_transactions_section(self):
        container = ctk.CTkFrame(self.main_container, fg_color=COLORS["card"],
                                corner_radius=12, border_width=1, border_color=COLORS["border"])
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(10, 5))

        ctk.CTkLabel(header, text="🧾 Transações",
                     font=font("subtitle", "bold")).pack(side="left")

        # Botão para adicionar despesa
        btn_adicionar = ctk.CTkButton(
            header,
            text="+ Adicionar Despesa",
            font=font("small", "bold"),
            fg_color=COLORS["danger"],
            hover_color="#991B1B",
            text_color="white",
            height=32,
            corner_radius=6,
            command=self.abrir_dialog_adicionar_despesa
        )
        btn_adicionar.pack(side="right")

        self.render_table(container)

    def render_table(self, container):
        table_container = ctk.CTkFrame(container, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuração de colunas
        def configure_table_grid(frame):
            frame.columnconfigure(0, weight=1, uniform="col")  # Data
            frame.columnconfigure(1, weight=4, uniform="col")  # Descrição
            frame.columnconfigure(2, weight=1, uniform="col")  # Tipo
            frame.columnconfigure(3, weight=1, uniform="col")  # Valor
        
        # ========== CABEÇALHO ==========
        headers_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        headers_frame.pack(fill="x", pady=(0, 5))
        configure_table_grid(headers_frame)
        
        # Data
        ctk.CTkLabel(
            headers_frame, 
            text="Data", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=15, pady=8)
        
        # Descrição
        ctk.CTkLabel(
            headers_frame, 
            text="Descrição", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=15, pady=8)
        
        # Tipo
        ctk.CTkLabel(
            headers_frame, 
            text="Tipo", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="center"
        ).grid(row=0, column=2, sticky="we", padx=0, pady=8)
        
        # Valor
        ctk.CTkLabel(
            headers_frame, 
            text="Valor", 
            font=font("small", "bold"), 
            text_color=COLORS["text_secondary"],
            anchor="e"
        ).grid(row=0, column=3, sticky="e", padx=15, pady=8)
        
        # Linha separadora
        ctk.CTkFrame(table_container, height=1, fg_color=COLORS["border"]).pack(fill="x", pady=5)
        
        # ========== DADOS DA TABELA ==========
        for i, (data, descricao, tipo, valor) in enumerate(self.transacoes):
            # Definir cor baseado no tipo
            cor = COLORS["primary"] if tipo.lower() == "receita" else COLORS["danger"]
            
            # Cor de fundo alternada
            bg = COLORS["bg_soft"] if i % 2 == 0 else "transparent"
            row_frame = ctk.CTkFrame(table_container, fg_color=bg, corner_radius=8)
            row_frame.pack(fill="x", pady=2)
            configure_table_grid(row_frame)
            
            # Data
            ctk.CTkLabel(
                row_frame, 
                text=data, 
                font=font("small"),
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=15, pady=8)
            
            # Descrição
            ctk.CTkLabel(
                row_frame, 
                text=descricao, 
                font=font("small"),
                anchor="w"
            ).grid(row=0, column=1, sticky="w", padx=15, pady=8)
            
            # Tipo (com badge)
            ctk.CTkLabel(
                row_frame, 
                text=tipo, 
                font=font("small", "bold"),
                text_color=("white", "white"),
                fg_color=cor,
                corner_radius=10,
                anchor="center",
                width=55,
                height=22
            ).grid(row=0, column=2, sticky="we", padx=0, pady=8)
            
            # Valor
            ctk.CTkLabel(
                row_frame, 
                text=f"R$ {valor:,.2f}".replace(",", "."), 
                font=font("small", "bold"), 
                text_color=cor,
                anchor="e"
            ).grid(row=0, column=3, sticky="e", padx=15, pady=8)

    def adicionar_transacao(self, data, descricao, tipo, valor):
        """Adiciona uma nova transação e sincroniza a interface"""
        self.transacoes.append((data, descricao, tipo, valor))
        self.atualizar_interface()
    
    def remover_transacao(self, indice):
        """Remove uma transação pelo índice e sincroniza a interface"""
        if 0 <= indice < len(self.transacoes):
            del self.transacoes[indice]
            self.atualizar_interface()
    
    def atualizar_interface(self):
        """Sincroniza todos os componentes da interface com os dados atuais"""
        # Limpar e reconstruir a interface
        for widget in self.main_container.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def obter_transacoes(self):
        """Retorna a lista de transações"""
        return self.transacoes
    
    def obter_totais(self):
        """Retorna os totais de receita e despesa"""
        total_receita, total_despesa, lucro = self.calcular_kpis()
        return {
            "receita": total_receita,
            "despesa": total_despesa,
            "lucro": lucro
        }

    def abrir_dialog_adicionar_despesa(self):
        """Abre um diálogo para adicionar uma nova despesa"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Adicionar Despesa")
        dialog.geometry("450x500")
        dialog.resizable(False, False)
        dialog.attributes("-topmost", True)
        dialog.grab_set()
        
        # Configurar cor de fundo da janela
        dialog.configure(fg_color=COLORS["bg"])

        # Frame principal com padding generoso
        main_frame = ctk.CTkFrame(dialog, fg_color=COLORS["card"], corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Título
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="📝 Nova Despesa",
            font=font("card_title", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        # Separador visual
        separator = ctk.CTkFrame(main_frame, height=1, fg_color=COLORS["border"])
        separator.pack(fill="x", padx=20, pady=(0, 20))

        # Frame de conteúdo com scroll se necessário
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=0)

        # Data
        ctk.CTkLabel(
            content_frame,
            text="Data",
            font=font("text", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 8))
        
        # Frame para o campo de data com botão de calendário
        data_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        data_frame.pack(fill="x", pady=(0, 20))
        
        entry_data = ctk.CTkEntry(
            data_frame,
            placeholder_text="DD/MM/AAAA",
            height=45,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            font=font("text")
        )
        entry_data.pack(side="left", fill="both", expand=True, padx=(0, 10))
        entry_data.delete(0, "end")
        entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        
        def abrir_seletor_data():
            """Abre um seletor de data simples"""
            data_atual = datetime.now()
            try:
                data_atual = datetime.strptime(entry_data.get(), "%d/%m/%Y")
            except:
                pass
            
            cal_window = ctk.CTkToplevel(dialog)
            cal_window.title("Selecione a Data")
            cal_window.geometry("320x280")
            cal_window.resizable(False, False)
            cal_window.grab_set()
            cal_window.configure(fg_color=COLORS["bg"])
            
            cal_frame = ctk.CTkFrame(cal_window, fg_color=COLORS["card"], corner_radius=12)
            cal_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título
            ctk.CTkLabel(
                cal_frame,
                text="Selecione a Data",
                font=font("subtitle", "bold"),
                text_color=COLORS["text"]
            ).pack(pady=(15, 10))
            
            # Frame para seletores
            selector_frame = ctk.CTkFrame(cal_frame, fg_color="transparent")
            selector_frame.pack(fill="both", padx=15, pady=10)
            
            # Dia
            ctk.CTkLabel(selector_frame, text="Dia", font=font("small", "bold")).pack(anchor="w", pady=(0, 5))
            dia_var = tk.StringVar(value=f"{data_atual.day:02d}")
            dia_menu = ctk.CTkComboBox(
                selector_frame,
                values=[f"{i:02d}" for i in range(1, 32)],
                variable=dia_var,
                height=35,
                corner_radius=6,
                font=font("text")
            )
            dia_menu.pack(fill="x", pady=(0, 10))
            
            # Mês
            ctk.CTkLabel(selector_frame, text="Mês", font=font("small", "bold")).pack(anchor="w", pady=(0, 5))
            meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            mes_var = tk.StringVar(value=meses[data_atual.month - 1])
            mes_menu = ctk.CTkComboBox(
                selector_frame,
                values=meses,
                variable=mes_var,
                height=35,
                corner_radius=6,
                font=font("text")
            )
            mes_menu.pack(fill="x", pady=(0, 10))
            
            # Ano
            ctk.CTkLabel(selector_frame, text="Ano", font=font("small", "bold")).pack(anchor="w", pady=(0, 5))
            ano_var = tk.StringVar(value=str(data_atual.year))
            anos = [str(year) for year in range(2020, 2031)]
            ano_menu = ctk.CTkComboBox(
                selector_frame,
                values=anos,
                variable=ano_var,
                height=35,
                corner_radius=6,
                font=font("text")
            )
            ano_menu.pack(fill="x", pady=(0, 15))
            
            def confirmar_data():
                dia = dia_var.get()
                mes = meses.index(mes_var.get()) + 1
                ano = ano_var.get()
                data_formatada = f"{dia}/{mes:02d}/{ano}"
                entry_data.delete(0, "end")
                entry_data.insert(0, data_formatada)
                cal_window.destroy()
            
            btn_confirmar = ctk.CTkButton(
                cal_frame,
                text="✓ Confirmar",
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_dark"],
                height=40,
                corner_radius=6,
                font=font("button", "bold"),
                command=confirmar_data
            )
            btn_confirmar.pack(fill="x", padx=15, pady=(0, 15))
        
        btn_calendario = ctk.CTkButton(
            data_frame,
            text="📅",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            width=45,
            height=45,
            corner_radius=8,
            font=font("text", "bold"),
            command=abrir_seletor_data
        )
        btn_calendario.pack(side="left")

        # Descrição
        ctk.CTkLabel(
            content_frame,
            text="Descrição",
            font=font("text", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 8))
        
        entry_descricao = ctk.CTkEntry(
            content_frame,
            placeholder_text="Ex: Aluguel do consultório",
            height=45,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            font=font("text")
        )
        entry_descricao.pack(fill="x", pady=(0, 20))

        # Valor
        ctk.CTkLabel(
            content_frame,
            text="Valor (R$)",
            font=font("text", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 8))
        
        entry_valor = ctk.CTkEntry(
            content_frame,
            placeholder_text="0,00",
            height=45,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            font=font("text")
        )
        entry_valor.pack(fill="x", pady=(0, 30))

        def salvar_despesa():
            """Salva a despesa no banco de dados"""
            try:
                data_str = entry_data.get().strip()
                descricao = entry_descricao.get().strip()
                valor_str = entry_valor.get().strip().replace(",", ".")
                
                # Validações
                if not all([data_str, descricao, valor_str]):
                    messagebox.showerror("Erro", "Preencha todos os campos!")
                    return
                
                # Validar formato de data
                try:
                    datetime.strptime(data_str, "%d/%m/%Y")
                except ValueError:
                    messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA")
                    return
                
                # Validar valor
                try:
                    valor = float(valor_str)
                    if valor <= 0:
                        messagebox.showerror("Erro", "O valor deve ser maior que zero!")
                        return
                except ValueError:
                    messagebox.showerror("Erro", "Valor inválido!")
                    return
                
                # Salvar no banco de dados
                if self.clinica_id:
                    resultado = FinanceiroController.criar_transacao(
                        tipo="despesa",
                        descricao=descricao,
                        valor=valor,
                        clinica_id=self.clinica_id,
                        data=datetime.strptime(data_str, "%d/%m/%Y")
                    )
                    
                    if resultado.get("sucesso"):
                        messagebox.showinfo("Sucesso", "Despesa adicionada com sucesso!")
                        dialog.destroy()
                        # Recarregar os dados
                        self.transacoes = self._carregar_transacoes()
                        self.atualizar_interface()
                    else:
                        messagebox.showerror("Erro", resultado.get("mensagem", "Erro ao adicionar despesa"))
                else:
                    messagebox.showerror("Erro", "Clínica não identificada!")
            
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar despesa: {str(e)}")

        # Frame dos botões com melhor espaçamento
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Botão Confirmar (Salvar)
        btn_salvar = ctk.CTkButton(
            button_frame,
            text="✓  Confirmar",
            font=font("button", "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            text_color="white",
            height=45,
            corner_radius=8,
            border_width=0,
            command=salvar_despesa
        )
        btn_salvar.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Botão Cancelar
        btn_cancelar = ctk.CTkButton(
            button_frame,
            text="✕  Cancelar",
            font=font("button", "bold"),
            fg_color=COLORS["danger"],
            hover_color="#DC2626",
            text_color="white",
            height=45,
            corner_radius=8,
            border_width=0,
            command=dialog.destroy
        )
        btn_cancelar.pack(side="left", fill="both", expand=True)