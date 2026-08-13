import customtkinter as ctk
from datetime import datetime, date
# Importações mantidas conforme original
from .base import BaseScreen
from .theme import font, COLORS, INNER_CARD_BORDER, INNER_CARD_RADIUS
from controllers.consulta_controller import ConsultaController
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.gerenciamento_controller import GerenciamentoController
from controllers.relatorios_controller import RelatoriosController
from controllers.clinica_controller import ClinicaController

class Painel(BaseScreen):
    def __init__(self, parent, clinica_id=None, usuario_id=None, tipo_usuario=None):
        super().__init__(parent, "Painel")

        self.clinica_id = clinica_id
        self.usuario_id = usuario_id
        self.tipo_usuario = tipo_usuario

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

        self.scroll = ctk.CTkScrollableFrame(
            self.content_card,
            fg_color="transparent",
            scrollbar_button_color=self.colors['border'],
            scrollbar_button_hover_color=self.colors['text_muted']
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # Layout de 2 colunas com pesos iguais
        self.scroll.grid_columnconfigure(0, weight=1, uniform="group1")
        self.scroll.grid_columnconfigure(1, weight=1, uniform="group1")

        self._inicializar_dados()
        self._renderizar_interface()

    def refresh(self):
        print("Painel.refresh() chamado")
        self._inicializar_dados()
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self._renderizar_interface()

    def _inicializar_dados(self):
        """Centraliza o carregamento de dados"""
        self.dados_consultas_hoje = self._carregar_consultas_hoje()
        self.dados_contagem_consultas = self._carregar_contagem_consultas()
        self.dados_cadastros = self._carregar_resumo_cadastros()
        self.dados_medicos = self._carregar_medicos()
        self.dados_relatorios = self._carregar_relatorios()
        pass

    def _renderizar_interface(self):
        """Orquestra a renderização dos componentes"""
        self._render_proximas_consultas(row=0, col=0)
        self._render_resumo_relatorios(row=0, col=1)
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
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        card.grid(row=row, column=col, sticky="nsew", padx=padx, pady=(0, 20))
        
        # Header do Card
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 15))

        ctk.CTkLabel(
            header, text=titulo,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.colors['text']
        ).pack(anchor="w")

        if subtitulo:
            ctk.CTkLabel(
                header, text=subtitulo,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=self.colors['text_secondary']
            ).pack(anchor="w")

        return card

    def _navegar_para(self, nome_tela):
        app = getattr(self.master, 'master', None)
        if app and hasattr(app, 'show_frame'):
            app.show_frame(nome_tela)

    def _criar_botao_ir_para(self, parent, destino):
        # Reserve a small footer area inside the card so content never
        # overlaps the button. The footer is transparent and only used
        # to position the button at the bottom-right with consistent
        # spacing from card borders and content above.
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.pack(fill="x", side="bottom", padx=20, pady=(8, 12))

        botao = ctk.CTkButton(
            footer,
            text="Ir para",
            width=90,
            height=30,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_soft'],
            text_color="white",
            corner_radius=12,
            font=ctk.CTkFont(size=12, weight="bold"),
            border_width=0,
            cursor="hand2",
            command=lambda: self._navegar_para(destino)
        )
        botao.pack(side="right")
        return botao

    def _render_proximas_consultas(self, row, col):
        card = self._criar_card("Próximas Consultas", "Compromissos agendados para hoje", row, col, padx=(0, 10))
        
        if not self.dados_consultas_hoje:
            self._render_vazio(card, "Nenhum compromisso agendado para hoje")
            return

        for item in self.dados_consultas_hoje[:2]:
            # Parsing simplificado para exemplo
            nome = item[1] if isinstance(item, (list, tuple)) else "Paciente"
            horario = item[2].strftime('%H:%M') if hasattr(item[2], 'strftime') else "00:00"
            
            row_item = ctk.CTkFrame(card, fg_color="transparent")
            row_item.pack(fill="x", padx=15, pady=5)

            # Avatar Round
            avatar = ctk.CTkLabel(
                row_item, text=nome[0].upper(), width=38, height=38,
                corner_radius=19, fg_color=self.colors['primary_soft'],
                text_color=self.colors['primary'], font=ctk.CTkFont(weight="bold")
            )
            avatar.pack(side="left", padx=(5, 12))

            info = ctk.CTkFrame(row_item, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)
            
            ctk.CTkLabel(info, text=nome, font=ctk.CTkFont(size=18, weight="bold"), text_color=self.colors['text']).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Horário: {horario}h", font=ctk.CTkFont(size=14), text_color=self.colors['text_secondary']).pack(anchor="w")

            # Badge Status
            badge = ctk.CTkFrame(row_item, fg_color=self.colors['info_soft'], corner_radius=8)
            badge.pack(side="right", padx=5)
            ctk.CTkLabel(badge, text="Confirmado", text_color=self.colors['info'], font=ctk.CTkFont(size=10, weight="bold")).pack(padx=8, pady=2)

        self._criar_botao_ir_para(card, 'agenda')

    def _render_resumo_relatorios(self, row, col):
        card = self._criar_card("📊 Resumo dos Relatórios", "", row, col, padx=(10, 0))

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=10)
        container.grid_columnconfigure((0, 1, 2, 3), weight=1)

        f = self.dados_relatorios or {}
        metrics = [
            ("Atendidos", str(f.get('atendidos', 0)), self.colors['primary']),
            ("Profissionais", str(f.get('total_medicos', 0)), self.colors['success']),
            ("Consultas", str(f.get('total_consultas', 0)), self.colors['info']),
            ("Comparecimento", f"{f.get('comparecimento', 0)}%", self.colors['warning'])
        ]

        for i, (lab, val, col_text) in enumerate(metrics):
            box = ctk.CTkFrame(
                container,
                fg_color=self.colors['bg_app'],
                corner_radius=12,
                border_width=1,
                border_color=INNER_CARD_BORDER
            )
            box.grid(row=0, column=i, padx=4, sticky="nsew")

            ctk.CTkLabel(box, text=lab, font=ctk.CTkFont(size=14), text_color=self.colors['text_secondary']).pack(pady=(10, 0))
            ctk.CTkLabel(box, text=val, font=ctk.CTkFont(size=19, weight="bold"), text_color=col_text).pack(pady=(0, 10))

        botao_relatorios = self._criar_botao_ir_para(card, 'relatorios')

    def _render_status_consultas(self, row, col):
        card = self._criar_card("Status das Consultas", "Distribuição de consultas por status", row, col, padx=(0, 10))
        
        contagem = self.dados_contagem_consultas
        total = contagem.get('total', 0)
        
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
            
            ctk.CTkLabel(lbl_f, text=label, font=ctk.CTkFont(size=16), text_color=self.colors['text']).pack(side="left")
            ctk.CTkLabel(lbl_f, text=f"{valor}", font=ctk.CTkFont(size=16, weight="bold"), text_color=self.colors['text']).pack(side="right")
            
            prog = ctk.CTkProgressBar(row_f, height=8, progress_color=cor, fg_color=self.colors['bg_app'])
            prog.pack(fill="x", pady=(5, 0))
            prog.set(perc)

        self._criar_botao_ir_para(card, 'agenda')

    def _render_resumo_cadastros(self, row, col):
        card = self._criar_card("Base de Dados", "Usuários e registros do sistema", row, col, padx=(10, 0))
        
        # Destaque Principal
        hero = ctk.CTkFrame(card, fg_color=self.colors['primary_soft'], corner_radius=15)
        hero.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(hero, text=str(self.dados_cadastros['total_usuarios']), 
                     font=ctk.CTkFont(size=48, weight="bold"), text_color=self.colors['primary']).pack(pady=(15,0))
        ctk.CTkLabel(hero, text="TOTAL DE USUÁRIOS", font=ctk.CTkFont(size=14, weight="bold"), 
                     text_color=self.colors['primary']).pack(pady=(0, 15))

        # Grid de detalhes
        detalhe = ctk.CTkFrame(card, fg_color="transparent")
        detalhe.pack(fill="x", padx=20, pady=10)
        
        itens = [("Consultas Realizadas", 'consultas_realizadas', 'info'), ("Médicos", 'medicos', 'success'), ("Gestão", 'gerentes', 'warning')]
        for label, key, color_key in itens:
            f = ctk.CTkFrame(detalhe, fg_color=self.colors['bg_app'], corner_radius=10)
            f.pack(fill="x", pady=3)
            ctk.CTkLabel(f, text=label, text_color=self.colors['text_secondary']).pack(side="left", padx=15, pady=8)
            ctk.CTkLabel(f, text=str(self.dados_cadastros[key]), font=ctk.CTkFont(size=15, weight="bold"), 
                         text_color=self.colors[color_key]).pack(side="right", padx=15)

    def _render_profissionais_ativos(self, row, col):
        card = self._criar_card("Corpo Clínico", "Profissionais ativos no sistema", row, col, padx=(0, 10))
        
        if not self.dados_medicos:
            self._render_vazio(card, "Nenhum profissional disponível no momento")
            return

        # Garantir que apenas médicos sejam considerados (fonte já é MedicoController)
        # Ordenar localmente por ID decrescente para mostrar os mais recentes
        medicos_para_exibir = sorted(self.dados_medicos or [], key=lambda m: m.get('id', 0), reverse=True)[:3]

        for prof in medicos_para_exibir:
            nome = prof.get('nome', 'Médico')
            espec = prof.get('especialidade', 'Geral')
            
            item = ctk.CTkFrame(card, fg_color=self.colors['bg_app'], corner_radius=12)
            item.pack(fill="x", padx=20, pady=4)
            
            # Avatar Style
            ctk.CTkLabel(item, text="🩺", font=ctk.CTkFont(size=20)).pack(side="left", padx=15)
            txt_f = ctk.CTkFrame(item, fg_color="transparent")
            txt_f.pack(side="left", pady=10)
            ctk.CTkLabel(txt_f, text=nome, font=ctk.CTkFont(size=15, weight="bold"), text_color=self.colors['text']).pack(anchor="w")
            ctk.CTkLabel(txt_f, text=espec, font=ctk.CTkFont(size=14), text_color=self.colors['text_muted']).pack(anchor="w")

        self._criar_botao_ir_para(card, 'gerenciamento')

    def _render_alertas(self, row, col):
        card = self._criar_card("Notificações", "Alertas e avisos importantes", row, col, padx=(10, 0))

        resumo = self.dados_relatorios or {}
        alertas = [
            ("📊", f"{resumo.get('total_consultas', 0)} consultas no período", self.colors['info']),
            ("✅", f"{resumo.get('atendidos', 0)} pacientes atendidos", self.colors['success']),
            ("⚠️", f"{resumo.get('cancelamentos', 0)} consultas canceladas", self.colors['danger'])
        ]

        for icon, msg, color in alertas:
            f = ctk.CTkFrame(card, fg_color=self.colors['bg_app'], corner_radius=10, border_width=1, border_color=self.colors['border'])
            f.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(f, text=f"{icon}  {msg}", text_color=color, font=ctk.CTkFont(size=14, weight="bold")).pack(padx=15, pady=12, anchor="w")

    def _render_vazio(self, parent, mensagem):
        ctk.CTkLabel(parent, text=mensagem, text_color=self.colors['text_muted'], 
                     font=ctk.CTkFont(slant="italic")).pack(pady=40)

    # --- Métodos de Dados (Conectados ao Banco de Dados) ---
    @staticmethod
    def _resumir_status_consultas(consultas):
        """Resume os status a partir da mesma lista de consultas usada pela agenda."""
        contagem = {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'total': 0}

        for item in consultas or []:
            status = None
            if isinstance(item, dict):
                status = item.get('status')
            elif isinstance(item, (list, tuple)) and len(item) > 3:
                status = item[3]

            if isinstance(status, str):
                status_normalizado = status.strip().lower()
                if status_normalizado in contagem:
                    contagem[status_normalizado] += 1

        contagem['total'] = len(consultas or [])
        return contagem

    def _carregar_consultas_hoje(self):
        """Carrega as próximas consultas da clínica logada, excluindo consultas passadas e canceladas."""
        try:
            if not self.clinica_id:
                return []

            consultas = ConsultaController.listar_proximas_por_clinica(
                self.clinica_id,
                limite=5
            )
            return consultas if consultas else []
        except Exception as e:
            print(f"Erro ao carregar consultas: {e}")
            return []

    def _carregar_contagem_consultas(self):
        """Carrega contagem de consultas por status usando a mesma origem da agenda."""
        try:
            if not self.clinica_id:
                print("[PAINEL] Clínica não informada; retornando zeros")
                return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'total': 0}

            print(f"[PAINEL] Clínica: {self.clinica_id}")
            print("[PAINEL] Reutilizando ConsultaController.listar_por_clinica() para resumir status")
            consultas = ConsultaController.listar_por_clinica(
                self.clinica_id,
                pagina=0,
                limite=10000,
                data=None,
                status=None,
                medico=None,
                especialidade=None,
            )

            contagem = self._resumir_status_consultas(consultas)
            print(f"[PAINEL] Total de consultas encontradas: {contagem.get('total', 0)}")
            print("[PAINEL] Status encontrados:")
            for status_key in ['agendada', 'confirmada', 'realizada', 'cancelada']:
                print(f"[PAINEL] {status_key} = {contagem.get(status_key, 0)}")

            return contagem
        except Exception as e:
            print(f"[PAINEL] Erro ao carregar contagem de consultas: {e}")
            import traceback
            traceback.print_exc()
            return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'total': 0}

    def _carregar_resumo_cadastros(self):
        """Carrega resumo de usuários cadastrados"""
        try:
            if not self.clinica_id:
                return {'pacientes': 0, 'consultas_realizadas': 0, 'medicos': 0, 'gerentes': 0, 'total_usuarios': 0}
            
            conn = None
            cursor = None
            try:
                from config.database import get_connection
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                
                print("========== BASE DE DADOS ===========")
                print(f"Clínica ID: {self.clinica_id}")

                # Pacientes: usar a tabela de pacientes atual da clínica
                sql_pacientes = (
                    "SELECT COUNT(*) AS total "
                    "FROM odontoPro_paciente "
                    "WHERE clinica_id = %s AND ativo = 1"
                )
                print("Tabela consultada: odontoPro_paciente")
                print(f"SQL executado (pacientes): {sql_pacientes}")
                cursor.execute(sql_pacientes, (self.clinica_id,))
                pacientes = cursor.fetchone()['total'] or 0
                print(f"Pacientes encontrados: {pacientes}")

                sql_consultas_realizadas = (
                    "SELECT COUNT(*) AS total "
                    "FROM odontoPro_consulta "
                    "WHERE clinica_id = %s "
                    "AND LOWER(TRIM(status)) = 'realizada'"
                )
                cursor.execute(sql_consultas_realizadas, (self.clinica_id,))
                consultas_realizadas = cursor.fetchone()['total'] or 0

                # Médicos: usar a mesma origem de dados do Corpo Clínico
                print("Tabela consultada: odontoPro_medico via MedicoController.listar_medicos")
                print("SQL executado (médicos): SELECT id, nome, email, crm_cro, ativo FROM odontoPro_medico WHERE clinica_id = %s ORDER BY nome ASC")
                medicos_lista = MedicoController.listar_medicos(self.clinica_id)
                medicos = len(medicos_lista)
                print(f"Médicos encontrados: {medicos}")

                # Gestão: usuários administrativos ativos da clínica
                sql_gerentes = "SELECT COUNT(DISTINCT id) as total FROM odontoPro_gerenciamento WHERE clinica_id = %s AND ativo = 1"
                print("Tabela consultada: odontoPro_gerenciamento")
                print(f"SQL executado (usuários gestão): {sql_gerentes}")
                cursor.execute(sql_gerentes, (self.clinica_id,))
                gerentes = cursor.fetchone()['total'] or 0
                print(f"Usuários gestão encontrados: {gerentes}")
                
                total_usuarios = pacientes + medicos + gerentes
                print(f"Total calculado: {total_usuarios}")
                print("====================================")
                
                return {
                    'pacientes': pacientes,
                    'consultas_realizadas': consultas_realizadas,
                    'medicos': medicos,
                    'gerentes': gerentes,
                    'total_usuarios': total_usuarios
                }
            except Exception as e:
                print(f"Erro ao contar cadastros: {e}")
                print("====================================")
                return {'pacientes': 0, 'consultas_realizadas': 0, 'medicos': 0, 'gerentes': 0, 'total_usuarios': 0}
            finally:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Erro geral: {e}")
            print("====================================")
            return {'pacientes': 0, 'consultas_realizadas': 0, 'medicos': 0, 'gerentes': 0, 'total_usuarios': 0}

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

    def _carregar_relatorios(self):
        """Carrega o resumo do mesmo domínio de indicadores usado pela aba Relatórios."""
        try:
            if not self.clinica_id:
                return {
                    'total_consultas': 0,
                    'total_pacientes': 0,
                    'total_medicos': 0,
                    'comparecimento': 0,
                }

            resumo = RelatoriosController.obter_resumo_consultas(self.clinica_id)
            return resumo if resumo else {
                'total_consultas': 0,
                'total_pacientes': 0,
                'total_medicos': 0,
                'comparecimento': 0,
            }
        except Exception as e:
            print(f"Erro ao carregar dados de relatórios: {e}")
            return {
                'total_consultas': 0,
                'total_pacientes': 0,
                'total_medicos': 0,
                'comparecimento': 0,
            }