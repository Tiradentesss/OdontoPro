import os
from io import BytesIO
from datetime import datetime, date

import customtkinter as ctk
import requests
from PIL import Image, ImageDraw, ImageFont

# Importações mantidas conforme original
from .base import BaseScreen
from .theme import font, COLORS, INNER_CARD_BORDER, INNER_CARD_RADIUS
from controllers.consulta_controller import ConsultaController
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.gerenciamento_controller import GerenciamentoController
from controllers.relatorios_controller import RelatoriosController
from controllers.clinica_controller import ClinicaController
from services.cloudinary_service import get_cloudinary_config

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
        self._proximas_consultas_avatar_cache = {}
        self._proximas_consultas_image_refs = []

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
        card = self._criar_card("Próximas Consultas", "Próximas consultas confirmadas", row, col, padx=(0, 10))
        self._proximas_consultas_avatar_cache = {}
        self._proximas_consultas_image_refs = []

        if not self.dados_consultas_hoje:
            self._render_vazio(card, "Nenhuma consulta confirmada próxima")
            return

        for item in self.dados_consultas_hoje[:3]:
            if isinstance(item, dict):
                nome = item.get('nome') or 'Paciente'
                foto = item.get('foto')
                horario = item.get('data_hora')
            else:
                nome = item[1] if len(item) > 1 else 'Paciente'
                foto = item[9] if len(item) > 9 else None
                horario = item[2] if len(item) > 2 else None

            horario_txt = horario.strftime('%H:%M') if hasattr(horario, 'strftime') else '00:00'
            avatar_size = 38
            avatar_img, has_photo = self._create_patient_avatar(nome, foto, avatar_size)

            row_item = ctk.CTkFrame(card, fg_color="transparent")
            row_item.pack(fill="x", padx=15, pady=5)

            avatar = ctk.CTkLabel(
                row_item,
                text='',
                image=None,
                width=avatar_size,
                height=avatar_size,
                corner_radius=avatar_size // 2,
                fg_color="transparent",
                text_color=self.colors['primary'],
                font=ctk.CTkFont(weight="bold")
            )

            if has_photo:
                avatar.configure(
                    text='',
                    image=avatar_img,
                    fg_color='transparent',
                    width=avatar_size,
                    height=avatar_size,
                    corner_radius=avatar_size // 2,
                    compound='center'
                )
                avatar.image = avatar_img
                print(f"[PAINEL AVATAR] {nome}: exibindo foto, widget transparente e tamanho {avatar_size}x{avatar_size}")
            else:
                inicial = (nome or '?')[0].upper() if nome else '?'
                avatar.configure(
                    text=inicial,
                    image=None,
                    fg_color=self.colors['primary_soft'],
                    width=avatar_size,
                    height=avatar_size,
                    corner_radius=avatar_size // 2,
                    compound='center'
                )
                avatar.image = None
                print(f"[PAINEL AVATAR] {nome}: exibindo inicial como fallback")

            avatar.pack(side="left", padx=(5, 12))

            info = ctk.CTkFrame(row_item, fg_color="transparent")
            info.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(info, text=nome, font=ctk.CTkFont(size=18, weight="bold"), text_color=self.colors['text']).pack(anchor="w")
            ctk.CTkLabel(info, text=f"Horário: {horario_txt}h", font=ctk.CTkFont(size=14), text_color=self.colors['text_secondary']).pack(anchor="w")

            badge = ctk.CTkFrame(row_item, fg_color=self.colors['info_soft'], corner_radius=8)
            badge.pack(side="right", padx=5)
            ctk.CTkLabel(badge, text="Confirmado", text_color=self.colors['info'], font=ctk.CTkFont(size=10, weight="bold")).pack(padx=8, pady=2)

        self._criar_botao_ir_para(card, 'agenda')

    def _create_patient_avatar(self, nome, foto, size):
        if foto and foto in self._proximas_consultas_avatar_cache:
            return self._proximas_consultas_avatar_cache[foto], True

        if foto:
            print(f"[PAINEL AVATAR] Paciente: {nome or 'Paciente'}")
            print(f"[PAINEL AVATAR] Foto recebida: {foto}")
            try:
                is_http_url = isinstance(foto, str) and foto.lower().startswith(('http://', 'https://'))
                is_absolute_path = isinstance(foto, str) and os.path.isabs(foto)
                has_extension = isinstance(foto, str) and '.' in os.path.basename(foto)
                img = None
                url_to_load = None
                classification = "Arquivo local"

                if is_http_url:
                    classification = "URL remota"
                    url_to_load = foto
                    print(f"[PAINEL AVATAR] Classificação: {classification}")
                elif is_absolute_path:
                    classification = "Arquivo local (caminho absoluto)"
                    print(f"[PAINEL AVATAR] Classificação: {classification}")
                    if os.path.exists(foto):
                        img = Image.open(foto).convert('RGBA')
                    else:
                        raise FileNotFoundError(f"Arquivo não encontrado: {foto}")
                elif isinstance(foto, str) and '/' in foto and not has_extension:
                    classification = "Cloudinary public_id"
                    print(f"[PAINEL AVATAR] Classificação: {classification}")
                    cloudinary_config = get_cloudinary_config()
                    if cloudinary_config:
                        cloud_name = cloudinary_config.get('cloud_name')
                        print(f"[PAINEL AVATAR] Cloud name: {cloud_name}")
                        url_to_load = f"https://res.cloudinary.com/{cloud_name}/image/upload/{foto}"
                        print(f"[PAINEL AVATAR] URL gerada: {url_to_load}")
                    else:
                        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                        path = os.path.join(root, foto)
                        if os.path.exists(path):
                            img = Image.open(path).convert('RGBA')
                        else:
                            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
                else:
                    classification = "Arquivo local (relativo)"
                    print(f"[PAINEL AVATAR] Classificação: {classification}")
                    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                    if foto.startswith('media/'):
                        path = os.path.join(root, foto)
                    else:
                        path = os.path.join(root, 'media', foto)
                    if os.path.exists(path):
                        img = Image.open(path).convert('RGBA')
                    else:
                        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

                if url_to_load and img is None:
                    response = requests.get(url_to_load, timeout=15)
                    print(f"[PAINEL AVATAR] Status HTTP: {response.status_code}")
                    response.raise_for_status()
                    img = Image.open(BytesIO(response.content)).convert('RGBA')

                if img is not None:
                    min_d = min(img.size)
                    img = img.crop(((img.width - min_d) // 2, (img.height - min_d) // 2, (img.width + min_d) // 2, (img.height + min_d) // 2))
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                    mask = Image.new('L', (size, size), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0, size, size), fill=255)
                    img.putalpha(mask)
                    avatar_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
                    self._proximas_consultas_avatar_cache[foto] = avatar_img
                    self._proximas_consultas_image_refs.append(avatar_img)
                    print(f"[PAINEL AVATAR] Imagem carregada com sucesso")
                    return avatar_img, True
            except Exception as exc:
                print(f"[PAINEL AVATAR] Erro: {type(exc).__name__} - {str(exc)[:120]}")
                print(f"[PAINEL AVATAR] Aplicando fallback com inicial")

        inicial = (nome or '?')[0].upper() if nome else '?'
        color = self.colors['primary_soft']
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((0, 0, size, size), fill=color)
        try:
            fonte = ImageFont.truetype('arial.ttf', int(size * 0.50))
        except Exception:
            fonte = ImageFont.load_default()
        draw.text((size / 2, size / 2), inicial, fill=self.colors['primary'], font=fonte, anchor='mm')
        avatar_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        if foto:
            self._proximas_consultas_avatar_cache[foto] = avatar_img
        self._proximas_consultas_image_refs.append(avatar_img)
        return avatar_img, False

    def _render_resumo_relatorios(self, row, col):
        card = self._criar_card("Resumo dos Relatórios", "", row, col, padx=(10, 0))
        # Reutiliza os dados reais carregados em self.dados_relatorios
        # e apresenta 4 indicadores internos com destaque no valor.
        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(fill="x", padx=20, pady=10)

        f = self.dados_relatorios or {}
        # Indicadores preferenciais vindos da lógica de Relatórios
        metrics = [
            ("👥", "Pacientes atendidos", str(f.get('atendidos', 0)), self.colors['info']),
            ("✅", "Consultas realizadas", str(f.get('realizadas', 0)), self.colors['success']),
            ("❌", "Cancelamentos", str(f.get('cancelamentos', 0)), self.colors['danger']),
            ("📊", "Comparecimento", f"{f.get('comparecimento', 0)}%", self.colors['warning']),
        ]

        # Reorganizar em grade 2x2 para melhorar legibilidade
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        for i, (icon, title, value, col_text) in enumerate(metrics):
            r = i // 2
            c = i % 2
            box = ctk.CTkFrame(
                container,
                fg_color=self.colors['bg_app'],
                corner_radius=12,
                border_width=1,
                border_color=INNER_CARD_BORDER
            )
            box.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")

            # Ícone + título (superior)
            header = ctk.CTkFrame(box, fg_color="transparent")
            header.pack(fill="x", padx=14, pady=(12, 6))
            ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=18), text_color=col_text).pack(side="left")
            ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=13), text_color=self.colors['text_secondary']).pack(side="left", padx=(10, 0))

            # Valor em destaque (centralizado à esquerda)
            ctk.CTkLabel(box, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color=col_text).pack(anchor="w", padx=14, pady=(2, 14))

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
            ("Faltas", contagem.get('falta', 0), self.colors['text_muted']),
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
        # Gerar até 3 notificações reais e relevantes, priorizando eventos que precisam de atenção.
        notificacoes = []
        try:
            hoje = date.today()

            # 1) Próxima consulta (mais próxima no futuro)
            proximas = ConsultaController.listar_proximas_por_clinica(self.clinica_id, limite=5)
            if proximas:
                primeiro = proximas[0]
                nome = primeiro[1] if not isinstance(primeiro, dict) else primeiro.get('nome')
                dt = primeiro[2] if not isinstance(primeiro, dict) else primeiro.get('data_hora')
                if hasattr(dt, 'strftime'):
                    when = f"Hoje às {dt.strftime('%H:%M')}" if getattr(dt, 'date', lambda: None)() == hoje else dt.strftime('%d/%m %H:%M')
                else:
                    when = ''
                notificacoes.append(("Próxima consulta", f"{nome} • {when}", self.colors['info']))

            # 2) Consulta aguardando confirmação para hoje
            aguardando = ConsultaController.listar_por_clinica(self.clinica_id, data=hoje, status='agendada', limite=5)
            if aguardando:
                # pegar a primeira (mais próxima) que esteja com status 'agendada'
                item = None
                for it in aguardando:
                    status = it[3] if not isinstance(it, dict) else it.get('status')
                    if isinstance(status, str) and status.strip().lower() == 'agendada':
                        item = it
                        break
                if item:
                    nome = item[1] if not isinstance(item, dict) else item.get('nome')
                    dt = item[2] if not isinstance(item, dict) else item.get('data_hora')
                    when = f"Hoje às {dt.strftime('%H:%M')}" if hasattr(dt, 'strftime') and getattr(dt, 'date', lambda: None)() == hoje else (dt.strftime('%d/%m %H:%M') if hasattr(dt, 'strftime') else '')
                    notificacoes.append(("Aguardando confirmação", f"{nome} • {when}", self.colors['warning']))

            # 3) Consulta cancelada recentemente (ordenar por data_hora desc)
            canceladas = ConsultaController.listar_por_clinica(self.clinica_id, status='cancelada', limite=10)
            if canceladas:
                cancel_sorted = sorted(canceladas, key=lambda c: (c[2] if not isinstance(c, dict) else c.get('data_hora')) or datetime.min, reverse=True)
                recent = cancel_sorted[0]
                nome = recent[1] if not isinstance(recent, dict) else recent.get('nome')
                dt = recent[2] if not isinstance(recent, dict) else recent.get('data_hora')
                when = f"Hoje às {dt.strftime('%H:%M')}" if hasattr(dt, 'strftime') and getattr(dt, 'date', lambda: None)() == hoje else (dt.strftime('%d/%m %H:%M') if hasattr(dt, 'strftime') else '')
                notificacoes.append(("Consulta cancelada", f"{nome} • {when}", self.colors['danger']))

            # 4) Novo paciente cadastrado (mais recente)
            pacientes = PacienteController.listar_pacientes(self.clinica_id)
            if pacientes:
                recent_p = sorted(pacientes, key=lambda p: p.get('id', 0) if isinstance(p, dict) else (p[0] if len(p) > 0 else 0), reverse=True)[0]
                nome_p = recent_p.get('nome') if isinstance(recent_p, dict) else recent_p[1] if len(recent_p) > 1 else ''
                notificacoes.append(("Novo paciente cadastrado", f"{nome_p}", self.colors['primary']))

            # 5) Novo médico cadastrado (mais recente)
            medicos = MedicoController.listar_medicos(self.clinica_id)
            if medicos:
                recent_m = sorted(medicos, key=lambda m: m.get('id', 0) if isinstance(m, dict) else (m[0] if len(m) > 0 else 0), reverse=True)[0]
                nome_m = recent_m.get('nome') if isinstance(recent_m, dict) else recent_m[1] if len(recent_m) > 1 else ''
                notificacoes.append(("Novo médico cadastrado", f"{nome_m}", self.colors['success']))

        except Exception as e:
            print(f"Erro ao gerar notificações: {e}")

        # Remover duplicatas simples (mesmo título e texto)
        vistos = set()
        finais = []
        for t, m, col in notificacoes:
            key = (t, m)
            if key in vistos:
                continue
            vistos.add(key)
            finais.append((t, m, col))
            if len(finais) >= 3:
                break

        if not finais:
            ctk.CTkLabel(card, text="Nenhuma notificação importante no momento.", text_color=self.colors['text_muted'], font=ctk.CTkFont(slant="italic")).pack(pady=20)
            return

        for title, msg, color in finais:
            f = ctk.CTkFrame(card, fg_color=self.colors['bg_app'], corner_radius=10, border_width=1, border_color=self.colors['border'])
            f.pack(fill="x", padx=20, pady=6)
            ctk.CTkLabel(f, text=title, text_color=color, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=12, pady=(10, 0))
            ctk.CTkLabel(f, text=msg, text_color=self.colors['text_secondary'], font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=(0, 10))

    def _render_vazio(self, parent, mensagem):
        ctk.CTkLabel(parent, text=mensagem, text_color=self.colors['text_muted'], 
                     font=ctk.CTkFont(slant="italic")).pack(pady=40)

    # --- Métodos de Dados (Conectados ao Banco de Dados) ---
    @staticmethod
    def _resumir_status_consultas(consultas):
        """Resume os status a partir da mesma lista de consultas usada pela agenda."""
        contagem = {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'falta': 0, 'total': 0}

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
                limite=3,
                apenas_confirmadas_futuras=True,
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
                return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'falta': 0, 'total': 0}

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
            for status_key in ['agendada', 'confirmada', 'realizada', 'cancelada', 'falta']:
                print(f"[PAINEL] {status_key} = {contagem.get(status_key, 0)}")

            return contagem
        except Exception as e:
            print(f"[PAINEL] Erro ao carregar contagem de consultas: {e}")
            import traceback
            traceback.print_exc()
            return {'agendada': 0, 'confirmada': 0, 'realizada': 0, 'cancelada': 0, 'falta': 0, 'total': 0}

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

            resumo = RelatoriosController.obter_resumo_consultas(
                self.clinica_id,
                usar_desfechos_comparecimento=True,
            )
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