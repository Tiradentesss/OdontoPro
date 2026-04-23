from .base import BaseScreen
from .theme import font, ICON_SIZE, COLORS
import customtkinter as ctk
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.gerenciamento_controller import GerenciamentoController
import hashlib

class Cadastro(BaseScreen):
    def __init__(self, parent, clinica_id=None):
        super().__init__(parent, "Cadastro")
        self.clinica_id = clinica_id

        # Configuração de cores - PALETA MAIS MODERNA
        self.cor_fundo_card = COLORS["card"]
        self.cor_aba_ativa = COLORS["card"]
        self.cor_aba_inativa = COLORS["bg_soft"]
        self.cor_texto_ativo = COLORS["primary"]
        self.cor_texto_inativo = COLORS["text_secondary"]
        self.cor_borda = COLORS["border"]
        self.cor_primaria = COLORS["primary"]
        self.cor_primaria_hover = COLORS["primary_dark"]
        
        self.padding_lateral = 25

        self.paciente_entries = []
        self.profissional_entries = []

        # =============================
        # 1. BARRA DE ABAS (TOPO) - AUMENTO MODERADO
        # =============================
        self.tab_bar = ctk.CTkFrame(self.content_card, fg_color="transparent", height=44)  # 40 -> 44
        self.tab_bar.pack(fill="x", padx=25, pady=(9, 0), anchor="nw")  # 8 -> 9

        self.btn_pacientes = ctk.CTkButton(
            self.tab_bar, text="👤   Pacientes",  # 2 espaços -> 3 espaços
            font=font("button_large", "bold"),  # 14 -> 15
            width=135, height=37, corner_radius=6,  # 125x34 -> 135x37
            command=lambda: self._trocar_aba("Pacientes")
        )
        self.btn_pacientes.pack(side="left", padx=(0, 5))  # 4 -> 5

        self.btn_profissionais = ctk.CTkButton(
            self.tab_bar, text="📋   Profissionais",  # 2 espaços -> 3 espaços
            font=font("button_large", "bold"),  # 14 -> 15
            width=135, height=37, corner_radius=6,  # 125x34 -> 135x37
            command=lambda: self._trocar_aba("Profissionais")
        )
        self.btn_profissionais.pack(side="left")

        # =============================
        # 2. ÁREA DE CONTEÚDO (CORPO BRANCO)
        # =============================
        self.container_outer = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent",
            corner_radius=20
        )
        self.container_outer.pack(fill="both", expand=True, padx=25, pady=25)

        self.container_conteudo = ctk.CTkFrame(
            self.container_outer,
            fg_color=self.cor_fundo_card,
            corner_radius=12
        )
        self.container_conteudo.pack(fill="both", expand=True, padx=2, pady=(2, 1))

        self.frame_pacientes = self._criar_tela_pacientes()
        self.frame_profissionais = self._criar_tela_profissionais()

        self._trocar_aba("Pacientes")

    def _trocar_aba(self, aba_selecionada):
        self._atualizar_estilo_abas(aba_selecionada)
        self.frame_pacientes.pack_forget()
        self.frame_profissionais.pack_forget()

        if aba_selecionada == "Pacientes":
            self.frame_pacientes.pack(fill="both", expand=True)
        else:
            self.frame_profissionais.pack(fill="both", expand=True)

    def _atualizar_estilo_abas(self, ativa):
        estilo_ativo = {
            "fg_color": self.cor_aba_ativa,
            "text_color": self.cor_texto_ativo,
            "hover_color": self.cor_aba_ativa
        }
        estilo_inativo = {
            "fg_color": "transparent",
            "text_color": self.cor_texto_inativo,
            "hover_color": "#D1D5DB"
        }

        if ativa == "Pacientes":
            self.btn_pacientes.configure(**estilo_ativo)
            self.btn_profissionais.configure(**estilo_inativo)
        else:
            self.btn_pacientes.configure(**estilo_inativo)
            self.btn_profissionais.configure(**estilo_ativo)

    # =====================================================
    # CRIAÇÃO DAS TELAS
    # =====================================================
    def _criar_tela_pacientes(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        self._titulo(frame, "Cadastro de Pacientes")

        entries = []

        self._secao_titulo(frame, "Informações Pessoais")

        e1, e2 = self._campo_duplo(frame, "Nome completo", "CPF")
        entries.extend([e1, e2])
        e1, e2 = self._campo_duplo(frame, "Data de nascimento", "Telefone")
        entries.extend([e1, e2])

        self._secao_titulo(frame, "Endereço")
        e1, e2, e3 = self._campo_triplo(frame, "CEP", "UF", "Cidade")
        entries.extend([e1, e2, e3])
        e = self._entry(frame, "Logradouro")
        entries.append(e)
        e1, e2 = self._campo_duplo(frame, "Número", "Complemento")
        entries.extend([e1, e2])

        self._secao_titulo(frame, "Acesso ao Sistema")
        e1, e2 = self._campo_duplo(frame, "Email", "Senha", show2="*")
        entries.extend([e1, e2])

        self.paciente_entries = entries
        self._botoes_acao(frame, "Salvar Paciente", target_entries=self.paciente_entries)

        return frame

    def _secao_titulo(self, parent, texto):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=(16, 8))  # (14,7) -> (16,8)

        ctk.CTkLabel(
            container,
            text=texto,
            font=font("subtitle", "bold"),  # 15 -> 16
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")

        linha = ctk.CTkFrame(container, height=2, width=52, fg_color=self.cor_primaria, corner_radius=1)  # 48 -> 52
        linha.pack(anchor="w", pady=(4, 0))  # 3 -> 4

    def _campo_duplo(self, parent, label1, label2, show1=None, show2=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=5)  # 4 -> 5

        frame1 = ctk.CTkFrame(container, fg_color="transparent")
        frame1.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            frame1,
            text=label1,
            font=font("text"),  # 13 -> 14
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))  # 2 -> 3

        entry1 = ctk.CTkEntry(
            frame1,
            placeholder_text=f"Digite {label1.lower()}",
            height=44, show=show1,  # 40 -> 44
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=5,  # 4 -> 5
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        entry1.pack(fill="x")

        frame2 = ctk.CTkFrame(container, fg_color="transparent")
        frame2.pack(side="left", expand=True, fill="x", padx=(5, 0))

        ctk.CTkLabel(
            frame2,
            text=label2,
            font=font("text"),  # 13 -> 14
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))  # 2 -> 3

        entry2 = ctk.CTkEntry(
            frame2,
            placeholder_text=f"Digite {label2.lower()}",
            height=44, show=show2,  # 40 -> 44
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=5,  # 4 -> 5
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        entry2.pack(fill="x")

        return entry1, entry2

    def _campo_triplo(self, parent, label1, label2, label3):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=5)  # 4 -> 5

        entries_list = []
        for label in (label1, label2, label3):
            frame_i = ctk.CTkFrame(container, fg_color="transparent")
            frame_i.pack(side="left", expand=True, fill="x", padx=5)

            ctk.CTkLabel(
                frame_i,
                text=label,
                font=font("text"),  # 13 -> 14
                text_color="#4B5563",
                anchor="w"
            ).pack(anchor="w", pady=(0, 3))  # 2 -> 3

            entry_i = ctk.CTkEntry(
                frame_i,
                placeholder_text=f"Digite {label.lower()}",
                height=44,  # 40 -> 44
                fg_color="#F9FAFB",
                border_color="#E5E7EB",
                border_width=1,
                corner_radius=5,  # 4 -> 5
                text_color="#111827",
                placeholder_text_color="#9CA3AF"
            )
            entry_i.pack(fill="x")
            entries_list.append(entry_i)

        return tuple(entries_list)

    def _criar_tela_profissionais(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        self._titulo(frame, "Cadastro de Profissional")

        self._secao_titulo(frame, "Dados Pessoais e Acesso ao Sistema")
        entries = []
        
        # Linha 1: Nome | Senha
        container1 = ctk.CTkFrame(frame, fg_color="transparent")
        container1.pack(fill="x", padx=self.padding_lateral, pady=(0, 0))

        # Frame Nome (tamanho fixo)
        frame_nome = ctk.CTkFrame(container1, fg_color="transparent")
        frame_nome.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            frame_nome,
            text="Nome completo",
            font=font("text"),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        nome_entry = ctk.CTkEntry(
            frame_nome,
            placeholder_text="Digite seu nome",
            height=44,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        nome_entry.pack(fill="x")
        entries.append(nome_entry)

        # Frame Senha (tamanho fixo, maior)
        frame_senha = ctk.CTkFrame(container1, fg_color="transparent")
        frame_senha.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(
            frame_senha,
            text="Senha",
            font=font("text"),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        self.senha_entry = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Sua senha",
            height=44,
            width=200,
            show="*",
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        self.senha_entry.pack()
        entries.append(self.senha_entry)

        # Linha 2: Email | Confirmar Senha
        container2 = ctk.CTkFrame(frame, fg_color="transparent")
        container2.pack(fill="x", padx=self.padding_lateral, pady=(0, 0))

        # Frame Email (tamanho fixo)
        frame_email = ctk.CTkFrame(container2, fg_color="transparent")
        frame_email.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            frame_email,
            text="Email",
            font=font("text"),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        email_entry = ctk.CTkEntry(
            frame_email,
            placeholder_text="seu@email.com",
            height=44,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        email_entry.pack(fill="x")
        entries.append(email_entry)

        # Frame Confirmar Senha (tamanho fixo, maior)
        frame_confirma_senha = ctk.CTkFrame(container2, fg_color="transparent")
        frame_confirma_senha.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(
            frame_confirma_senha,
            text="Confirmar Senha",
            font=font("text"),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        self.confirma_senha_entry = ctk.CTkEntry(
            frame_confirma_senha,
            placeholder_text="Confirme",
            height=44,
            width=200,
            show="*",
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        self.confirma_senha_entry.pack()
        entries.append(self.confirma_senha_entry)

        self._secao_titulo(frame, "Tipo de Profissional")
        tipo_container = ctk.CTkFrame(frame, fg_color="transparent")
        tipo_container.pack(fill="x", padx=self.padding_lateral, pady=(0, 10))
        
        ctk.CTkLabel(
            tipo_container, 
            text="Selecione o tipo", 
            font=font("text"),
            text_color="#4B5563"
        ).pack(anchor="w", pady=(0, 3))
        
        self.tipo_profissional = ctk.CTkOptionMenu(
            tipo_container,
            values=["Médico", "Gerente"],
            height=44,
            fg_color="#F9FAFB", 
            button_color="#E5E7EB", 
            button_hover_color="#D1D5DB",
            text_color="#111827", 
            dropdown_fg_color="#FFFFFF", 
            dropdown_text_color="#111827",
            dropdown_font=font("text"),
            command=self._ao_mudar_tipo_profissional
        )
        self.tipo_profissional.pack(fill="x")

        self.campos_dinamicos_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.campos_dinamicos_container.pack(fill="x", pady=(0, 10))

        self.frame_medico = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.cro_entry, self.telefone_entry = self._campo_duplo(
            self.frame_medico, "CRO", "Telefone"
        )
        entries.extend([self.cro_entry, self.telefone_entry])

        self._ao_mudar_tipo_profissional("Médico")

        self.profissional_entries = entries
        self._botoes_acao(frame, "Salvar Profissional", target_entries=self.profissional_entries)
        return frame

    def _ao_mudar_tipo_profissional(self, choice):
        try:
            self.frame_medico.pack_forget()
        except Exception:
            pass
        
        if choice == "Médico":
            self.frame_medico.pack(fill="x")

    def _botoes_acao(self, parent, texto_principal, target_entries=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="bottom", fill="x", padx=self.padding_lateral, pady=14)  # 12 -> 14

        def _salvar():
            tipo_aba = "Pacientes" if hasattr(self, 'paciente_entries') and self.paciente_entries == target_entries else "Profissionais"
            tipo_prof = self.tipo_profissional.get() if hasattr(self, 'tipo_profissional') else None
            
            try:
                if tipo_aba == "Pacientes":
                    self._salvar_paciente(target_entries)
                elif tipo_prof == "Médico":
                    self._salvar_medico(target_entries)
                elif tipo_prof == "Gerente":
                    self._salvar_gerente(target_entries)
            except Exception as e:
                self._mostrar_mensagem(f"Erro: {str(e)}", sucesso=False)

        ctk.CTkButton(
            container,
            text=texto_principal.upper(),
            font=font("button_large", "bold"),  # 14 -> 15
            height=44,  # 40 -> 44
            width=220,  # 200 -> 220
            fg_color=self.cor_primaria,
            hover_color=self.cor_primaria_hover,
            text_color="#FFFFFF",
            corner_radius=5,  # 4 -> 5
            border_spacing=0,
            command=_salvar
        ).pack(side="left", padx=(0, 8))  # 7 -> 8

        def _limpar():
            entries = target_entries or []
            for e in entries:
                try:
                    content = e.get()
                    if content:
                        e.delete(0, "end")
                except Exception:
                    pass

        limpar_btn = ctk.CTkButton(
            container,
            text="LIMPAR",
            font=font("button_large"),  # 14 -> 15
            height=44,  # 40 -> 44
            width=125,  # 115 -> 125
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color="#6B7280",
            corner_radius=5,  # 4 -> 5
            border_width=1,
            border_color="#E5E7EB",
            command=_limpar
        )
        limpar_btn.pack(side="left")

    # =====================================================
    # COMPONENTES REUTILIZÁVEIS
    # =====================================================
    def _titulo(self, parent, texto):
        ctk.CTkLabel(
            parent, text=texto, font=font("title", "bold"),  # 22 -> 24
            text_color="#111827"
        ).pack(anchor="w", padx=self.padding_lateral, pady=(24, 17))  # (22,15) -> (24,17)

    def _entry(self, parent, placeholder, show=None):
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, height=44, show=show,  # 40 -> 44
            fg_color="#F9FAFB", border_color="#E5E7EB", text_color="#111827",
            placeholder_text_color="#9CA3AF", corner_radius=5  # 4 -> 5
        )
        entry.pack(fill="x", padx=self.padding_lateral, pady=8)  # 7 -> 8
        return entry

    def _botao_salvar(self, parent, texto="Salvar"):
        ctk.CTkButton(
            parent, text=texto.upper(), font=font("button_large", "bold"),  # 14 -> 15
            height=44, width=330,  # 40x310 -> 44x330
            fg_color="#06B6D4", hover_color="#0891B2", text_color="#FFFFFF",
            corner_radius=5  # 4 -> 5
        ).pack(pady=22)  # 20 -> 22

    def _salvar_paciente(self, entries):
        """Valida e salva paciente no banco de dados"""
        try:
            nome = entries[0].get().strip()
            cpf = entries[1].get().strip()
            data_nasc = entries[2].get().strip()
            telefone = entries[3].get().strip()
            cep = entries[4].get().strip()
            uf = entries[5].get().strip()
            cidade = entries[6].get().strip()
            rua = entries[7].get().strip()
            numero = entries[8].get().strip()
            complemento = entries[9].get().strip()
            email = entries[10].get().strip()
            senha = entries[11].get().strip()
            
            # Validações básicas
            if not all([nome, email, telefone, senha]):
                self._mostrar_mensagem("Preencha todos os campos obrigatórios (inclusive senha)", sucesso=False)
                return
            
            resultado = PacienteController.criar_paciente(
                nome=nome,
                cpf=cpf or None,
                sexo=None,
                email=email,
                data_nascimento=data_nasc or None,
                telefone=telefone,
                clinica_id=self.clinica_id,
                senha=senha
            )
            
            if resultado["sucesso"]:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=True)
                self._limpar_campos(entries)
            else:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=False)
        except Exception as e:
            self._mostrar_mensagem(f"Erro ao salvar paciente: {str(e)}", sucesso=False)

    def _salvar_medico(self, entries):
        """Valida e salva médico no banco de dados"""
        try:
            nome = entries[0].get().strip()
            email = entries[1].get().strip()
            cro = self.cro_entry.get().strip()
            telefone = self.telefone_entry.get().strip()
            senha = self.senha_entry.get().strip()
            confirma_senha = self.confirma_senha_entry.get().strip()
            
            # Validações
            if not all([nome, email, cro, telefone, senha]):
                self._mostrar_mensagem("Preencha todos os campos obrigatórios (inclusive senha)", sucesso=False)
                return
            
            if senha != confirma_senha:
                self._mostrar_mensagem("As senhas não coincidem", sucesso=False)
                return
            
            resultado = MedicoController.criar_medico(
                nome=nome,
                cpf=None,
                sexo="m",
                email=email,
                data_nascimento=None,
                telefone=telefone,
                cro=cro,
                clinica_id=self.clinica_id,
                senha=senha,
                especialidades=None
            )
            
            if resultado["sucesso"]:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=True)
                self._limpar_campos([entries[0], entries[1]])
                self._limpar_campos([self.cro_entry, self.telefone_entry])
                self._limpar_campos([self.senha_entry, self.confirma_senha_entry])
            else:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=False)
        except Exception as e:
            self._mostrar_mensagem(f"Erro ao salvar médico: {str(e)}", sucesso=False)

    def _salvar_gerente(self, entries):
        """Valida e salva gerente no banco de dados"""
        try:
            nome = entries[0].get().strip()
            email = entries[1].get().strip()
            senha = self.senha_entry.get().strip()
            confirma_senha = self.confirma_senha_entry.get().strip()
            
            # Validações
            if not all([nome, email, senha]):
                self._mostrar_mensagem("Preencha todos os campos obrigatórios (inclusive senha)", sucesso=False)
                return
            
            if senha != confirma_senha:
                self._mostrar_mensagem("As senhas não coincidem", sucesso=False)
                return
            
            resultado = GerenciamentoController.criar_gerente(
                nome=nome,
                email=email,
                clinica_id=self.clinica_id,
                senha=senha,
                permissoes=None
            )
            
            if resultado["sucesso"]:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=True)
                self._limpar_campos([entries[0], entries[1]])
                self._limpar_campos([self.senha_entry, self.confirma_senha_entry])
            else:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=False)
        except Exception as e:
            self._mostrar_mensagem(f"Erro ao salvar gerente: {str(e)}", sucesso=False)

    def _limpar_campos(self, entries):
        """Limpa os campos de entrada"""
        for e in entries:
            try:
                e.delete(0, "end")
            except Exception:
                pass

    def _mostrar_mensagem(self, mensagem, sucesso=True):
        """Exibe uma mensagem de feedback ao usuário"""
        cor = "#10B981" if sucesso else "#EF4444"
        msg_label = ctk.CTkLabel(
            self.content_card,
            text=mensagem,
            text_color=cor,
            font=font("text", "bold")
        )
        msg_label.pack(pady=10)
        
        # Remove a mensagem após 3 segundos
        self.after(3000, lambda: msg_label.pack_forget())
