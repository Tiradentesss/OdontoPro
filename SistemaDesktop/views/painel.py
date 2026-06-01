import customtkinter as ctk
from datetime import datetime, date
# Importações mantidas conforme original
from .base import BaseScreen
from .theme import font, COLORS
from controllers.consulta_controller import ConsultaController
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.gerenciamento_controller import GerenciamentoController
from controllers.financeiro_controller import FinanceiroController
from controllers.clinica_controller import ClinicaController

class Painel(BaseScreen):
    def __init__(self, parent, clinica_id=None, usuario_id=None, tipo_usuario=None):
        super().__init__(parent, "Painel")

        self.clinica_id = clinica_id
        self.usuario_id = usuario_id
        self.tipo_usuario = tipo_usuario

        # Configuração de Responsividade do Container Pai
        self.content_card.grid_rowconfigure(0, weight=1)
        self.content_card.grid_columnconfigure(0, weight=1)

        # Definição de Estilo Expandida (Mantendo sua Identidade)
        self.colors = {
            'primary': COLORS.get('primary', '#06B6D4'),
            'primary_soft': COLORS.get('primary_soft', '#164E63'),
            'success': COLORS.get('success', '#10B981'),
            'success_soft': COLORS.get('success_light', '#065F46'),
            'warning': COLORS.get('warning', '#F59E0B'),
            'warning_soft': COLORS.get('warning_light', '#78350F'),
            'danger': COLORS.get('danger', '#EF4444'),
            'danger_soft': COLORS.get('danger_light', '#7F1D1D'),
            'info': COLORS.get('secondary', '#3B82F6'),
            'info_soft': COLORS.get('accent_light', '#164E63'),
            'card': COLORS.get('card', '#1E293B'),
            'border': COLORS.get('border', '#334155'),
            'text': COLORS.get('text_primary', '#F1F5F9'),
            'text_secondary': COLORS.get('text_secondary', '#CBD5E1'),
            'text_muted': COLORS.get('text_muted', '#94A3B8'),
            'bg_app': COLORS.get('bg_soft', '#1E293B')
        }

        # Container Principal com Scroll
        self.main_container = ctk.CTkFrame(self.content_card, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=2, pady=2)

        self.scroll = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent",
            scrollbar_button_color=self.colors['border'],
            scrollbar_button_hover_color=self.colors['text_muted']
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        # Layout de 2 colunas com pesos iguais
        self.scroll.grid_columnconfigure(0, weight=1, uniform="group1")
        self.scroll.grid_columnconfigure(1, weight=1, uniform="group1")

        self._inicializar_dados()
        self._renderizar_interface()

    def _inicializar_dados(self):
        """Centraliza o carregamento de dados"""
        self.dados_consultas_hoje = self._carregar_consultas_hoje()
        self.dados_contagem_consultas = self._carregar_contagem_consultas()
        self.dados_cadastros = self._carregar_resumo_cadastros()
        self.dados_medicos = self._carregar_medicos()
        self.dados_financeiro = self._carregar_financeiro()

    def _renderizar_interface(self):
        """Orquestra a renderização dos componentes"""
        self._render_proximas_consultas(row=0, col=0)
        self._render_resumo_financeiro(row=0, col=1)
        self._render_status_consultas(row=1, col=0)
        self._render_resumo_cadastros(row=1, col=1)
        self._render_profissionais_ativos(row=2, col=0)
        self._render_alertas(row=2, col=1)

    # --- Componentes de UI Customizados ---

    def _criar_card(self, titulo, subtitulo="", row=0, col=0, padx=(0,0)):
        """Factory de Cards Modernos"""
        card = ctk.CTkFrame(
            self.scroll,
            fg_color=self.colors['card'],
            corner_radius=20,
            border_width=1,
            border_color=self.colors['border']
        )
        card.grid(row=row, column=col, sticky="nsew", padx=padx, pady=(0, 20))
        
        # Header do Card
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 15))

        ctk.CTkLabel(
            header, text=titulo,
            font=font("card_title", "bold"),
            text_color=self.colors['text']
        ).pack(anchor="w")

        if subtitulo:
            ctk.CTkLabel(
                header, text=subtitulo,
                font=font("text"),
                text_color=self.colors['text_secondary']
            ).pack(anchor="w")
            
        return card

    def _render_proximas_consultas(self, row, col):
        card = self._criar_card("Próximas Consultas", "Compromissos agendados para hoje", row, col, padx=(0, 10))
        
        if not self.dados_consultas_hoje:
            self._render_vazio(card, "Nenhum compromisso agendado para hoje")
            return

        for item in self.dados_consultas_hoje[:4]:
            # Parsing simplificado para exemplo
            nome = item[1] if isinstance(item, (list, tuple)) else "Paciente"
            horario = item[2].strftime('%H:%M') if hasattr(item[2], 'strftime') else "00:00"
            
            row_item = ctk.CTkFrame(card, fg_color="transparent")
            row_item.pack(fill="x", padx=15, pady=5)

            # Avatar Round
            avatar = ctk.CTkLabel(
                row_item, text=nome[0].upper(), width=38, height=38,
                corner_radius=19, fg_color=self.colors['primary_soft'],
                text_color=self.colors['primary'], font=font("button", "bold")
            )
            avatar.pack(side="left", padx=(5, 12))

            info = ctk.CTkFrame(row_item, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(info, text=nome, font=font("card_title", "bold"), text_color=self.colors['text']).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Horário: {horario}h", font=font("text_large"), text_color=self.colors['text_secondary']).pack(anchor="w")

            # Badge Status
            badge = ctk.CTkFrame(row_item, fg_color=self.colors['info_soft'], corner_radius=8)
            badge.pack(side="right", padx=5)
            ctk.CTkLabel(badge, text="Confirmado", text_color=self.colors['info'], font=font("small", "bold")).pack(padx=8, pady=2)

    def _render_resumo_financeiro(self, row, col):
        card = self._criar_card("Resumo Financeiro", "Receita e despesas do mês", row, col, padx=(10, 0))
        
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=10)
        container.grid_columnconfigure((0,1,2), weight=1)

        f = self.dados_financeiro
        metrics = [
            ("Faturamento", f"R$ {f['faturamento']:,.0f}", self.colors['primary']),
            ("Despesas", f"R$ {f['despesas']:,.0f}", self.colors['danger']),
            ("Lucro", f"R$ {f['lucro']:,.0f}", self.colors['success'])
        ]

        for i, (lab, val, col_text) in enumerate(metrics):
            box = ctk.CTkFrame(container, fg_color=self.colors['bg_app'], corner_radius=12)
            box.grid(row=0, column=i, padx=4, sticky="nsew")
            
            ctk.CTkLabel(box, text=lab, font=font("text_large"), text_color=self.colors['text_secondary']).pack(pady=(10, 0))
            ctk.CTkLabel(box, text=val, font=font("large_title", "bold"), text_color=col_text).pack(pady=(0, 10))

        # Footer Info
        footer = ctk.CTkLabel(
            card, text=f"✓ {f['realizadas']} de {f['total_consultas']} consultas concluídas este mês",
            font=font("text"), text_color=self.colors['text_muted']
        )
        footer.pack(pady=(15, 20))

    def _render_status_consultas(self, row, col):
        card = self._criar_card("Status das Consultas", "Distribuição de consultas por status", row, col, padx=(0, 10))
        
        contagem = self.dados_contagem_consultas
        total = contagem.get('total', 1)
        
        status_data = [
            ("Agendadas", contagem.get('agendada', 0), self.colors['warning']),
            ("Confirmadas", contagem.get('confirmada', 0), self.colors['info']),
            ("Realizadas", contagem.get('realizada', 0), self.colors['success']),
            ("Canceladas", contagem.get('cancelada', 0), self.colors['danger']),
        ]

        for label, valor, cor in status_data:
            perc = (valor / total) if total > 0 else 0
            
            row_f = ctk.CTkFrame(card, fg_color="transparent")
            row_f.pack(fill="x", padx=20, pady=8)
            
            lbl_f = ctk.CTkFrame(row_f, fg_color="transparent")
            lbl_f.pack(fill="x")
            
            ctk.CTkLabel(lbl_f, text=label, font=font("subtitle"), text_color=self.colors['text']).pack(side="left")
            ctk.CTkLabel(lbl_f, text=f"{valor}", font=font("subtitle", "bold"), text_color=self.colors['text']).pack(side="right")
            
            prog = ctk.CTkProgressBar(row_f, height=8, progress_color=cor, fg_color=self.colors['bg_app'])
            prog.pack(fill="x", pady=(5, 0))
            prog.set(perc)

    def _render_resumo_cadastros(self, row, col):
        card = self._criar_card("Base de Dados", "Usuários e registros do sistema", row, col, padx=(10, 0))
        
        # Destaque Principal
        hero = ctk.CTkFrame(card, fg_color=self.colors['primary_soft'], corner_radius=15)
        hero.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(hero, text=str(self.dados_cadastros['total_usuarios']), 
                     font=font("large_title", "bold"), text_color=self.colors['primary']).pack(pady=(15,0))
        ctk.CTkLabel(hero, text="TOTAL DE USUÁRIOS", font=font("text_large", "bold"), 
                     text_color=self.colors['primary']).pack(pady=(0, 15))

        # Grid de detalhes
        detalhe = ctk.CTkFrame(card, fg_color="transparent")
        detalhe.pack(fill="x", padx=20, pady=10)
        
        itens = [("Pacientes", 'pacientes', 'info'), ("Médicos", 'medicos', 'success'), ("Gestão", 'gerentes', 'warning')]
        for label, key, color_key in itens:
            f = ctk.CTkFrame(detalhe, fg_color=self.colors['bg_app'], corner_radius=10)
            f.pack(fill="x", pady=3)
            ctk.CTkLabel(f, text=label, font=font("text"), text_color=self.colors['text_secondary']).pack(side="left", padx=15, pady=8)
            ctk.CTkLabel(f, text=str(self.dados_cadastros[key]), font=font("card_title", "bold"), 
                         text_color=self.colors[color_key]).pack(side="right", padx=15)

    def _render_profissionais_ativos(self, row, col):
        card = self._criar_card("Corpo Clínico", "Profissionais ativos no sistema", row, col, padx=(0, 10))
        
        if not self.dados_medicos:
            self._render_vazio(card, "Nenhum profissional disponível no momento")
            return

        for prof in self.dados_medicos[:3]:
            nome = prof.get('nome', 'Médico')
            espec = prof.get('especialidade', 'Geral')
            
            item = ctk.CTkFrame(card, fg_color=self.colors['bg_app'], corner_radius=12)
            item.pack(fill="x", padx=20, pady=4)
            
            # Avatar Style
            ctk.CTkLabel(item, text="🩺", font=font("button_large")).pack(side="left", padx=15)
            txt_f = ctk.CTkFrame(item, fg_color="transparent")
            txt_f.pack(side="left", pady=10)
            ctk.CTkLabel(txt_f, text=nome, font=font("text_large", "bold"), text_color=self.colors['text']).pack(anchor="w")
            ctk.CTkLabel(txt_f, text=espec, font=font("text"), text_color=self.colors['text_muted']).pack(anchor="w")

    def _render_alertas(self, row, col):
        card = self._criar_card("Notificações", "Alertas e avisos importantes", row, col, padx=(10, 0))
        
        alertas = [
            ("⚠️", "Taxa de cancelamento subiu 5% esta semana", self.colors['danger']),
            ("📅", "3 Pacientes aguardando confirmação", self.colors['info']),
            ("🩺", "Atualização de prontuário pendente", self.colors['warning'])
        ]

        for icon, msg, color in alertas:
            f = ctk.CTkFrame(card, fg_color=self.colors['bg_app'], corner_radius=10, border_width=1, border_color=self.colors['border'])
            f.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(f, text=f"{icon}  {msg}", text_color=color, font=font("text_large", "bold")).pack(padx=15, pady=12, anchor="w")

    def _render_vazio(self, parent, mensagem):
        ctk.CTkLabel(parent, text=mensagem, text_color=self.colors['text_muted'], 
                     font=font("text")).pack(pady=40)

    # --- Métodos de Dados (Conectados ao Banco de Dados) ---
    def _carregar_consultas_hoje(self):
        """Carrega consultas agendadas para hoje"""
        try:
            if not self.clinica_id: 
                return []
            # Busca consultas de hoje
            data_hoje = date.today().strftime('%Y-%m-%d')
            consultas = ConsultaController.listar_por_clinica(
                self.clinica_id, 
                pagina=0, 
                limite=5, 
                data=data_hoje
            )
            return consultas if consultas else []
        except Exception as e:
            print(f"Erro ao carregar consultas: {e}")
            return []

    def _carregar_contagem_consultas(self):
        """Carrega contagem de consultas por status"""
        try:
            if not self.clinica_id:
                return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'total': 0}
            
            conn = None
            try:
                from config.database import get_connection
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Buscar contagens por status
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN status = 'agendada' THEN 1 ELSE 0 END) as agendada,
                        SUM(CASE WHEN status = 'confirmada' THEN 1 ELSE 0 END) as confirmada,
                        SUM(CASE WHEN status = 'realizada' THEN 1 ELSE 0 END) as realizada,
                        SUM(CASE WHEN status = 'cancelada' THEN 1 ELSE 0 END) as cancelada,
                        COUNT(*) as total
                    FROM odontoPro_consulta
                    WHERE clinica_id = %s
                """, (self.clinica_id,))
                
                resultado = cursor.fetchone()
                conn.close()
                
                return {
                    'agendada': resultado['agendada'] or 0,
                    'confirmada': resultado['confirmada'] or 0,
                    'realizada': resultado['realizada'] or 0,
                    'cancelada': resultado['cancelada'] or 0,
                    'total': resultado['total'] or 0
                }
            except Exception as e:
                print(f"Erro ao contar consultas: {e}")
                return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'total': 0}
            finally:
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Erro geral: {e}")
            return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'total': 0}

    def _carregar_resumo_cadastros(self):
        """Carrega resumo de usuários cadastrados"""
        try:
            if not self.clinica_id:
                return {'pacientes': 0, 'medicos': 0, 'gerentes': 0, 'total_usuarios': 0}
            
            conn = None
            try:
                from config.database import get_connection
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                
                # Contar pacientes
                cursor.execute("SELECT COUNT(*) as total FROM odontoPro_paciente WHERE clinica_id = %s", (self.clinica_id,))
                pacientes = cursor.fetchone()['total']
                
                # Contar médicos
                cursor.execute("SELECT COUNT(*) as total FROM odontoPro_medico WHERE clinica_id = %s", (self.clinica_id,))
                medicos = cursor.fetchone()['total']
                
                # Contar gerentes
                cursor.execute("SELECT COUNT(*) as total FROM odontoPro_gerenciamento WHERE clinica_id = %s AND ativo = 1", (self.clinica_id,))
                gerentes = cursor.fetchone()['total']
                
                conn.close()
                
                return {
                    'pacientes': pacientes,
                    'medicos': medicos,
                    'gerentes': gerentes,
                    'total_usuarios': pacientes + medicos + gerentes + 1  # +1 para a clínica
                }
            except Exception as e:
                print(f"Erro ao contar cadastros: {e}")
                return {'pacientes': 0, 'medicos': 0, 'gerentes': 0, 'total_usuarios': 0}
            finally:
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Erro geral: {e}")
            return {'pacientes': 0, 'medicos': 0, 'gerentes': 0, 'total_usuarios': 0}

    def _carregar_medicos(self):
        """Carrega lista de médicos ativos"""
        try:
            if not self.clinica_id:
                return []
            
            medicos = MedicoController.listar_medicos(self.clinica_id)
            return medicos if medicos else []
        except Exception as e:
            print(f"Erro ao carregar médicos: {e}")
            return []

    def _carregar_financeiro(self):
        """Carrega resumo financeiro do mês"""
        try:
            if not self.clinica_id:
                return {
                    'faturamento': 0,
                    'despesas': 0,
                    'lucro': 0,
                    'total_consultas': 0,
                    'realizadas': 0
                }
            
            # Buscar dados do FinanceiroController
            resumo = FinanceiroController.obter_resumo_financeiro(self.clinica_id)
            return resumo if resumo else {
                'faturamento': 0,
                'despesas': 0,
                'lucro': 0,
                'total_consultas': 0,
                'realizadas': 0
            }
        except Exception as e:
            print(f"Erro ao carregar dados financeiros: {e}")
            return {
                'faturamento': 0,
                'despesas': 0,
                'lucro': 0,
                'total_consultas': 0,
                'realizadas': 0
            }