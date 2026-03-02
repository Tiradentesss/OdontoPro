from .base import BaseScreen
from .theme import font, ICON_SIZE
import customtkinter as ctk

class Cadastro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Cadastro")

        # Configuração de cores - PALETA MAIS MODERNA
        self.cor_fundo_card = "#FFFFFF"
        self.cor_aba_ativa = "#FFFFFF"
        self.cor_aba_inativa = "#F3F4F6"  # Mais suave
        self.cor_texto_ativo = "#0EA5E9"  # Azul mais suave
        self.cor_texto_inativo = "#6B7280"
        self.cor_borda = "#E5E7EB"
        self.cor_primaria = "#0EA5E9"
        self.cor_primaria_hover = "#0284C7"
        
        # reduzido lateral para caber melhor os campos e botões
        self.padding_lateral = 60

        # armazenar referências aos entries para limpar/salvar
        self.paciente_entries = []
        self.profissional_entries = []

        # MELHORIA 1: Adicionar ícones SVG ou emoji mais modernos
        # MELHORIA 2: Aumentar contraste e espaçamento

        # =============================
        # 1. BARRA DE ABAS (TOPO)
        # =============================
        self.tab_bar = ctk.CTkFrame(self.content_card, fg_color="transparent", height=40)
        self.tab_bar.pack(fill="x", padx=20, pady=(10, 0), anchor="nw")

        self.btn_pacientes = ctk.CTkButton(
            self.tab_bar, text="👤 Pacientes", font=font("text", "bold"),
            width=150, height=40, corner_radius=10,
            command=lambda: self._trocar_aba("Pacientes")
        )
        self.btn_pacientes.pack(side="left", padx=(0, 5))

        self.btn_profissionais = ctk.CTkButton(
            self.tab_bar, text="📋 Profissionais", font=font("text", "bold"),
            width=150, height=40, corner_radius=10,
            command=lambda: self._trocar_aba("Profissionais")
        )
        self.btn_profissionais.pack(side="left")

        # =============================
        # 2. ÁREA DE CONTEÚDO (CORPO BRANCO)
        # =============================
        # Caixa externa para simular borda ao redor do formulário
        # Ajustes: borda mais sutil, cantos mais arredondados e cantos nítidos
        # - outer fg_color: cor da borda
        # - outer corner_radius: levemente maior que o interno para manter round
        # - inner padx/pady: controla espessura da borda (2 px)
        # Removida a borda cinza externa conforme solicitado
        # Mantemos o frame externo apenas para layout e cantos
        self.container_outer = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent",
            corner_radius=20
        )
        # espaço externo para não colar nas laterais da janela
        # movi mais para dentro para aproximar o stroke cinza do formulário
        # reduzido o padding inferior para trazer o conteúdo para cima
        self.container_outer.pack(fill="both", expand=True, padx=120, pady=(6, 8))

        self.container_conteudo = ctk.CTkFrame(
            self.container_outer,
            fg_color=self.cor_fundo_card,
            corner_radius=12
        )
        # Espaçamento interno (espessura da borda)
        self.container_conteudo.pack(fill="both", expand=True, padx=2, pady=(2, 1))

        # Criação das telas
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

        # list to keep entries for this form
        entries = []

        # MELHORIA: Adicionar seções com cabeçalhos
        self._secao_titulo(frame, "Informações Pessoais")

        # Grid layout para campos relacionados
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

        # store and add buttons with target entries
        self.paciente_entries = entries
        self._botoes_acao(frame, "Salvar Paciente", target_entries=self.paciente_entries)

        return frame

    def _secao_titulo(self, parent, texto):
        """Título de seção com linha decorativa"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=(20, 10))

        ctk.CTkLabel(
            container,
            text=texto,
            font=font("subtitle", "bold"),
            text_color="#374151"
        ).pack(anchor="w")

        # Linha decorativa
        linha = ctk.CTkFrame(container, height=2, width=60, fg_color=self.cor_primaria, corner_radius=1)
        linha.pack(anchor="w", pady=(5, 0))

    def _campo_duplo(self, parent, label1, label2, show1=None, show2=None):
        """Dois campos lado a lado"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=6)

        # Campo 1
        frame1 = ctk.CTkFrame(container, fg_color="transparent")
        frame1.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            frame1,
            text=label1,
            font=("Poppins", 12),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 4))

        entry1 = ctk.CTkEntry(
            frame1,
            placeholder_text=f"Digite {label1.lower()}",
            height=42, show=show1,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1.5,
            corner_radius=8,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        entry1.pack(fill="x")

        # Campo 2
        frame2 = ctk.CTkFrame(container, fg_color="transparent")
        frame2.pack(side="left", expand=True, fill="x", padx=(5, 0))

        ctk.CTkLabel(
            frame2,
            text=label2,
            font=("Poppins", 12),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 4))

        entry2 = ctk.CTkEntry(
            frame2,
            placeholder_text=f"Digite {label2.lower()}",
            height=42, show=show2,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1.5,
            corner_radius=8,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        entry2.pack(fill="x")

        return entry1, entry2

    def _campo_triplo(self, parent, label1, label2, label3):
        """Três campos lado a lado"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=6)

        entries_list = []
        for label in (label1, label2, label3):
            frame_i = ctk.CTkFrame(container, fg_color="transparent")
            frame_i.pack(side="left", expand=True, fill="x", padx=5)

            ctk.CTkLabel(
                frame_i,
                text=label,
                font=("Poppins", 12),
                text_color="#4B5563",
                anchor="w"
            ).pack(anchor="w", pady=(0, 4))

            entry_i = ctk.CTkEntry(
                frame_i,
                placeholder_text=f"Digite {label.lower()}",
                height=42,
                fg_color="#F9FAFB",
                border_color="#E5E7EB",
                border_width=1.5,
                corner_radius=8,
                text_color="#111827",
                placeholder_text_color="#9CA3AF"
            )
            entry_i.pack(fill="x")
            entries_list.append(entry_i)

        return tuple(entries_list)

    def _criar_tela_profissionais(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        self._titulo(frame, "Cadastro de Profissional")

        # Seção Pessoal
        self._secao_titulo(frame, "Dados Pessoais")
        entries = []
        e1, e2 = self._campo_duplo(frame, "Nome completo", "Email")
        entries.extend([e1, e2])

        # Função/Tipo - Armazenar referência para o OptionMenu
        self._secao_titulo(frame, "Tipo de Profissional")
        tipo_container = ctk.CTkFrame(frame, fg_color="transparent")
        tipo_container.pack(fill="x", padx=self.padding_lateral, pady=(0, 12))
        
        ctk.CTkLabel(
            tipo_container, 
            text="Selecione o tipo", 
            font=("Poppins", 12), 
            text_color="#4B5563"
        ).pack(anchor="w", pady=(0, 4))
        
        self.tipo_profissional = ctk.CTkOptionMenu(
            tipo_container,
            values=["Dentista", "Auxiliar", "Recepcionista"],
            height=40,
            fg_color="#F9FAFB", 
            button_color="#E5E7EB", 
            button_hover_color="#D1D5DB",
            text_color="#111827", 
            dropdown_fg_color="#FFFFFF", 
            dropdown_text_color="#111827",
            command=self._ao_mudar_tipo_profissional
        )
        self.tipo_profissional.pack(fill="x")

        # Container dinâmico para campos específicos por tipo
        self.campos_dinamicos_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.campos_dinamicos_container.pack(fill="x", pady=(0, 12))

        # CRO e Telefone lado a lado (inicialmente invisível)
        self.frame_cro_telefone = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.cro_entry, self.telefone_entry = self._campo_duplo(
            self.frame_cro_telefone, "CRO", "Telefone"
        )
        entries.extend([self.cro_entry, self.telefone_entry])
        
        # Frame para dados específicos de recepcionista
        self.frame_recepcionista = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.recep_entry1, self.recep_entry2 = self._campo_duplo(
            self.frame_recepcionista, "Turno (Manhã/Tarde)", "Telefone"
        )
        entries.extend([self.recep_entry1, self.recep_entry2])
        
        # Frame para dados específicos de auxiliar
        self.frame_auxiliar = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.aux_entry = self._entry_unico(
            self.frame_auxiliar, "Especialização em auxílio"
        )
        entries.append(self.aux_entry)

        # Acesso
        self._secao_titulo(frame, "Acesso ao Sistema")
        self.senha_entry, self.confirma_senha_entry = self._campo_duplo(
            frame, "Senha", "Confirme a Senha", show1="*", show2="*"
        )
        entries.extend([self.senha_entry, self.confirma_senha_entry])

        # Inicializar com o primeiro tipo
        self._ao_mudar_tipo_profissional("Dentista")

        # Ações
        self.profissional_entries = entries
        self._botoes_acao(frame, "Salvar Profissional", target_entries=self.profissional_entries)
        return frame

    def _entry_unico(self, parent, placeholder, show=None):
        """Campo único para formulários"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=6)
        
        ctk.CTkLabel(
            container,
            text=placeholder,
            font=("Poppins", 12),
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 4))
        
        entry = ctk.CTkEntry(
            container,
            placeholder_text=f"Digite {placeholder.lower()}",
            height=42, show=show,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1.5,
            corner_radius=8,
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        entry.pack(fill="x")
        
        return entry

    def _ao_mudar_tipo_profissional(self, choice):
        """Atualiza os campos conforme o tipo de profissional selecionado"""
        
        # Esconder todos os frames dinâmicos
        try:
            self.frame_cro_telefone.pack_forget()
            self.frame_recepcionista.pack_forget()
            self.frame_auxiliar.pack_forget()
        except Exception:
            pass
        
        # Mostrar campos específicos baseado no tipo
        if choice == "Dentista":
            self.frame_cro_telefone.pack(fill="x")
            # Opcional: atualizar labels específicos
            self._atualizar_labels_cro_telefone("CRO", "Telefone")
            
        elif choice == "Auxiliar":
            self.frame_auxiliar.pack(fill="x")
            # Opcional: mostrar campo adicional
            self._atualizar_label_auxiliar("Especialização em auxílio")
            
        elif choice == "Recepcionista":
            self.frame_recepcionista.pack(fill="x")
            self._atualizar_labels_recepcionista("Turno (Manhã/Tarde)", "Telefone")

    def _atualizar_labels_cro_telefone(self, label1, label2):
        """Atualiza os labels do frame CRO/Telefone"""
        # Se quiser atualizar dinamicamente os textos dos labels
        # Isso requer manter referência aos labels ou recriar os campos
        pass

    def _atualizar_label_auxiliar(self, label):
        """Atualiza label do auxiliar"""
        pass

    def _atualizar_labels_recepcionista(self, label1, label2):
        """Atualiza labels do recepcionista"""
        pass

    def _botoes_acao(self, parent, texto_principal, target_entries=None):
        """Container para botões de ação"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="bottom", fill="x", padx=self.padding_lateral, pady=12)

        # Botão principal (stub de salvar)
        def _salvar():
            # placeholder: integrar com service/DB
            print("Salvar chamado", len(target_entries or []))

        ctk.CTkButton(
            container,
            text=texto_principal.upper(),
            font=("Poppins", 13, "bold"),
            height=42,
            width=220,
            fg_color=self.cor_primaria,
            hover_color=self.cor_primaria_hover,
            text_color="#FFFFFF",
            corner_radius=8,
            border_spacing=0,
            command=_salvar
        ).pack(side="left", padx=(0, 10))

        # Botão secundário (limpar)
        def _limpar():
            entries = target_entries or []
            for e in entries:
                try:
                    # só limpar se o campo tem conteúdo real (não é placeholder vazio)
                    content = e.get()
                    if content:  # só limpa campos com valor
                        e.delete(0, "end")
                except Exception:
                    pass

        limpar_btn = ctk.CTkButton(
            container,
            text="LIMPAR",
            font=("Poppins", 13),
            height=42,
            width=120,
            fg_color="transparent",
            hover_color="#F3F4F6",
            text_color="#6B7280",
            corner_radius=8,
            border_width=1.5,
            border_color="#E5E7EB",
            command=_limpar
        )
        limpar_btn.pack(side="left")

    # =====================================================
    # COMPONENTES REUTILIZÁVEIS
    # =====================================================
    def _titulo(self, parent, texto):
        ctk.CTkLabel(
            parent, text=texto, font=("Poppins", 20, "bold"), text_color="#111827"
        ).pack(anchor="w", padx=self.padding_lateral, pady=(25, 20))

    def _entry(self, parent, placeholder, show=None):
        # ALTERAÇÃO 1: Aumentei o pady de 6 para 12
        # Isso cria o espaço "respirável" entre os inputs
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, height=42, show=show,
            fg_color="#F9FAFB", border_color="#E5E7EB", text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        entry.pack(fill="x", padx=self.padding_lateral, pady=12)
        return entry

    def _botao_salvar(self, parent, texto="Salvar"):
        # ALTERAÇÃO 2: Botão menor
        # Removi o 'fill="x"' e defini uma largura fixa (width=220)
        # Reduzi levemente a altura de 45 para 40
        ctk.CTkButton(
            parent, text=texto.upper(), font=("Poppins", 14, "bold"), 
            height=38, width=360,
            fg_color="#06B6D4", hover_color="#0891B2", text_color="#FFFFFF",
            corner_radius=10
        ).pack(pady=30)