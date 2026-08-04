from .base import BaseScreen, ActionButtons
from .theme import font, ICON_SIZE, COLORS, INNER_CARD_BORDER, INNER_CARD_RADIUS, OUTER_CARD_BORDER, OUTER_CARD_RADIUS
import customtkinter as ctk
from controllers.paciente_controller import PacienteController
from controllers.medico_controller import MedicoController
from controllers.gerenciamento_controller import GerenciamentoController
from controllers.consulta_controller import ConsultaController
from services.campos_mascarados import GerenciadorMascaras
from services.endereco_service import EnderecoService
from services.localidades_service import LocalidadesService
from datetime import datetime
import re


class CidadeSearchComboBox(ctk.CTkFrame):
    def __init__(self, master, values=None, command=None, **kwargs):
        super().__init__(master, fg_color="transparent")
        self.values = list(values or [])
        self.filtered_values = self.values.copy()
        self.command = command
        self.dropdown = None
        self.selected_index = 0

        self.entry = ctk.CTkEntry(self, **kwargs)
        self.entry.pack(fill="x")
        self.entry.bind("<Button-1>", lambda event: self.abrir_lista())
        self.entry.bind("<FocusIn>", lambda event: self.abrir_lista())
        self.entry.bind("<KeyRelease>", self._filtrar_pelo_campo)
        self.entry.bind("<Down>", self._mover_selecao_baixo)
        self.entry.bind("<Up>", self._mover_selecao_cima)
        self.entry.bind("<Return>", self._selecionar_atual)
        self.entry.bind("<Escape>", lambda event: self.fechar_lista())

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value or ""))

    def delete(self, first, last=None):
        self.entry.delete(first, last)

    def insert(self, index, text):
        self.entry.insert(index, text)

    def bind(self, sequence=None, command=None, add=None):
        return self.entry.bind(sequence, command, add)

    def configure(self, **kwargs):
        if "values" in kwargs:
            self.values = list(kwargs.pop("values") or [])
            self.filtered_values = self.values.copy()
            if self.dropdown and self.dropdown.winfo_exists():
                self._atualizar_lista(self.filtered_values)

        if kwargs:
            self.entry.configure(**kwargs)

    config = configure

    def abrir_lista(self):
        if self.dropdown and self.dropdown.winfo_exists():
            return

        self.filtered_values = self.values.copy()
        largura = max(self.winfo_width(), 260)
        altura = 420
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2

        self.dropdown = ctk.CTkToplevel(self)
        self.dropdown.overrideredirect(True)
        self.dropdown.geometry(f"{largura}x{altura}+{x}+{y}")
        self.dropdown.configure(fg_color=COLORS["card"])
        self.dropdown.bind("<Escape>", lambda event: self.fechar_lista())
        self.dropdown.bind("<FocusOut>", self._fechar_se_foco_sair)

        self.search_entry = ctk.CTkEntry(
            self.dropdown,
            height=34,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"],
            placeholder_text="Pesquisar cidade"
        )
        self.search_entry.pack(fill="x", padx=6, pady=(6, 4))
        self.search_entry.bind("<KeyRelease>", self._filtrar_pelo_dropdown)
        self.search_entry.bind("<Down>", self._mover_selecao_baixo)
        self.search_entry.bind("<Up>", self._mover_selecao_cima)
        self.search_entry.bind("<Return>", self._selecionar_atual)
        self.search_entry.bind("<Escape>", lambda event: self.fechar_lista())

        self.lista_frame = ctk.CTkScrollableFrame(
            self.dropdown,
            height=360,
            fg_color=COLORS["card"],
            corner_radius=8
        )
        self.lista_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.selected_index = 0
        self._atualizar_lista(self.filtered_values)
        self.search_entry.focus_set()

    def fechar_lista(self):
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
        self.dropdown = None

    def _filtrar_pelo_campo(self, event=None):
        if event and event.keysym in {"Up", "Down", "Return", "Escape"}:
            return

        if self.dropdown and self.dropdown.winfo_exists():
            self._filtrar(self.entry.get())

    def _filtrar_pelo_dropdown(self, event=None):
        if event and event.keysym in {"Up", "Down", "Return", "Escape"}:
            return

        self._filtrar(self.search_entry.get())

    def _filtrar(self, termo):
        self.filtered_values = self._filtrar_valores(termo)
        self.selected_index = 0
        self._atualizar_lista(self.filtered_values)

    def _filtrar_valores(self, termo):
        termo_normalizado = LocalidadesService._normalizar(termo)
        if not termo_normalizado:
            return self.values.copy()

        comeca = [
            cidade for cidade in self.values
            if LocalidadesService._normalizar(cidade).startswith(termo_normalizado)
        ]
        contem = [
            cidade for cidade in self.values
            if termo_normalizado in LocalidadesService._normalizar(cidade)
            and not LocalidadesService._normalizar(cidade).startswith(termo_normalizado)
        ]
        return comeca + contem

    def _atualizar_lista(self, cidades):
        for child in self.lista_frame.winfo_children():
            child.destroy()

        if not cidades:
            ctk.CTkLabel(
                self.lista_frame,
                text="Nenhuma cidade encontrada",
                text_color=COLORS["text_muted"],
                anchor="w"
            ).pack(fill="x", padx=8, pady=8)
            return

        for indice, cidade in enumerate(cidades):
            fg_color = COLORS["hover"] if indice == self.selected_index else "transparent"
            botao = ctk.CTkButton(
                self.lista_frame,
                text=cidade,
                height=30,
                fg_color=fg_color,
                hover_color=COLORS["hover"],
                text_color=COLORS["text"],
                anchor="w",
                corner_radius=6,
                command=lambda valor=cidade: self._selecionar(valor)
            )
            botao.pack(fill="x", padx=2, pady=1)

    def _mover_selecao_baixo(self, event=None):
        if not self.dropdown or not self.filtered_values:
            self.abrir_lista()
            return "break"

        self.selected_index = min(self.selected_index + 1, len(self.filtered_values) - 1)
        self._atualizar_lista(self.filtered_values)
        return "break"

    def _mover_selecao_cima(self, event=None):
        if not self.dropdown or not self.filtered_values:
            return "break"

        self.selected_index = max(self.selected_index - 1, 0)
        self._atualizar_lista(self.filtered_values)
        return "break"

    def _selecionar_atual(self, event=None):
        if self.filtered_values:
            self._selecionar(self.filtered_values[self.selected_index])
        return "break"

    def _selecionar(self, cidade):
        self.set(cidade)
        if self.command:
            self.command(cidade)
        self.fechar_lista()

    def _fechar_se_foco_sair(self, event=None):
        self.after(120, self._fechar_se_sem_foco)

    def _fechar_se_sem_foco(self):
        if not self.dropdown or not self.dropdown.winfo_exists():
            return

        foco = self.focus_get()
        if foco and (foco == self.entry or str(foco).startswith(str(self.dropdown))):
            return

        self.fechar_lista()


class Cadastro(BaseScreen):
    ESPECIALIDADE_PLACEHOLDER = "Selecione uma especialidade"

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
        
        self.padding_lateral = 15

        self.paciente_entries = []
        self.profissional_entries = []
        
        # Gerenciador de máscaras
        self.mascaras_paciente = GerenciadorMascaras()
        self.mascaras_profissional = GerenciadorMascaras()
        self._aplicando_mascara_endereco = False
        self._cep_after_id = None
        self._ultimo_cep_consultado = None

        # =============================
        # 1. BARRA DE ABAS (TOPO)
        # =============================
        self.cadastro_card = self.content_card

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.cadastro_card,
            fg_color=COLORS["card"],
            corner_radius=INNER_CARD_RADIUS,
            border_width=1,
            border_color=INNER_CARD_BORDER
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.container_conteudo = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        self.container_conteudo.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_bar = ctk.CTkFrame(
            self.container_conteudo,
            fg_color="transparent",
            height=44
        )
        self.tab_bar.pack(fill="x", padx=20, pady=(9, 0), anchor="nw")

        self.btn_pacientes = ctk.CTkButton(
            self.tab_bar, text="👤   Pacientes",
            font=font("button_large", "bold"),
            width=135, height=37, corner_radius=6,
            command=lambda: self._trocar_aba("Pacientes")
        )
        self.btn_pacientes.pack(side="left", padx=(0, 5))

        self.btn_profissionais = ctk.CTkButton(
            self.tab_bar, text="📋   Profissionais",
            font=font("button_large", "bold"),
            width=135, height=37, corner_radius=6,
            command=lambda: self._trocar_aba("Profissionais")
        )
        self.btn_profissionais.pack(side="left")

        self.frame_pacientes = self._criar_tela_pacientes()
        self.frame_profissionais = self._criar_tela_profissionais()

        self._trocar_aba("Pacientes")

    def _trocar_aba(self, aba_selecionada):
        self._atualizar_estilo_abas(aba_selecionada)
        
        if hasattr(self, 'frame_pacientes') and self.frame_pacientes:
            self.frame_pacientes.pack_forget()
        if hasattr(self, 'frame_profissionais') and self.frame_profissionais:
            self.frame_profissionais.pack_forget()

        if aba_selecionada == "Pacientes":
            if self.frame_pacientes:
                self.frame_pacientes.pack(fill="both", expand=True)
        else:
            if self.frame_profissionais:
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
            "hover_color": COLORS["hover"]
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
        # Aplicar máscara de CPF
        self.mascaras_paciente.adicionar_campo('cpf_paciente', e2, 'cpf')
        # Campo visual: Sexo (não persiste nem altera lógica de salvamento)
        sexo_container = ctk.CTkFrame(frame, fg_color="transparent")
        sexo_container.pack(fill="x", padx=self.padding_lateral, pady=5)

        ctk.CTkLabel(
            sexo_container,
            text="Genero",
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        self.sexo_paciente = ctk.CTkComboBox(
            sexo_container,
            values=["Masculino", "Feminino"],
            height=44,
            state="readonly",
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            dropdown_font=font("text")
        )
        self.sexo_paciente.set("")
        self.sexo_paciente.pack(fill="x")
        
        e1, e2 = self._campo_duplo(frame, "Data de nascimento", "Telefone")
        entries.extend([e1, e2])
        # Aplicar máscaras de Data e Telefone
        self.mascaras_paciente.adicionar_campo('data_paciente', e1, 'data')
        self.mascaras_paciente.adicionar_campo('telefone_paciente', e2, 'telefone')

        self._secao_titulo(frame, "Endereço")
        e1, e2, e3 = self._campo_triplo(frame, "CEP", "UF", "Cidade")
        entries.extend([e1, e2, e3])
        e = self._entry(frame, "Logradouro")
        entries.append(e)
        e1, e2 = self._campo_duplo(frame, "Número", "Complemento")
        entries.extend([e1, e2])

        self._configurar_campos_endereco_paciente(entries[4], entries[5], entries[6], entries[7])

        self._secao_titulo(frame, "Acesso ao Sistema")
        e1, e2, e3 = self._campo_triplo(
            frame,
            "Email",
            "Senha",
            "Confirmar Senha",
            show2="*",
            show3="*"
        )
        entries.extend([e1, e2, e3])

        self.paciente_entries = entries
        self._botoes_acao(frame, "Salvar Paciente", target_entries=self.paciente_entries)

        return frame

    def _criar_tela_profissionais(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        self._titulo(frame, "Cadastro de Profissional")

        self._secao_titulo(frame, "Dados Pessoais e Acesso ao Sistema")
        entries = []
        
        # Linha 1: Nome | Senha | Confirmar Senha (visual arrangement)
        container1 = ctk.CTkFrame(frame, fg_color="transparent")
        container1.pack(fill="x", padx=self.padding_lateral, pady=(0, 0))

        # Frame Nome (esquerda, expansível)
        frame_nome = ctk.CTkFrame(container1, fg_color="transparent")
        frame_nome.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            frame_nome,
            text="Nome completo",
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        nome_entry = ctk.CTkEntry(
            frame_nome,
            placeholder_text="Digite seu nome",
            height=44,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        nome_entry.pack(fill="x")
        entries.append(nome_entry)

        # Frame Senha (meio)
        frame_senha = ctk.CTkFrame(container1, fg_color="transparent")
        frame_senha.pack(side="left", padx=(5, 5))

        ctk.CTkLabel(
            frame_senha,
            text="Senha",
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        self.senha_entry = ctk.CTkEntry(
            frame_senha,
            placeholder_text="Sua senha",
            height=44,
            width=200,
            show="*",
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        self.senha_entry.pack()
        entries.append(self.senha_entry)

        # Frame Confirmar Senha (direita)
        frame_confirma_senha = ctk.CTkFrame(container1, fg_color="transparent")
        frame_confirma_senha.pack(side="left", padx=(5, 0))

        ctk.CTkLabel(
            frame_confirma_senha,
            text="Confirmar Senha",
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        self.confirma_senha_entry = ctk.CTkEntry(
            frame_confirma_senha,
            placeholder_text="Confirme",
            height=44,
            width=200,
            show="*",
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        self.confirma_senha_entry.pack()
        # NOTE: keep confirma_senha appended after email to preserve expected entries ordering

        # Linha 2: Email + Gênero (mesmo container, mesma linha do grid)
        container2 = ctk.CTkFrame(frame, fg_color="transparent")
        container2.pack(fill="x", padx=self.padding_lateral, pady=(0, 0))

        # Criar uma única linha interna que usa grid para labels (row 0) e campos (row 1)
        row_email_genero = ctk.CTkFrame(container2, fg_color="transparent")
        row_email_genero.pack(fill="x")

        # configurar colunas: coluna 0 (Email) mais larga, coluna 1 (Gênero) menor
        # aumentar um pouco o peso da coluna 0 para alargar o campo Email
        row_email_genero.grid_columnconfigure(0, weight=5)
        row_email_genero.grid_columnconfigure(1, weight=1)

        # Labels na mesma linha (row 0)
        lbl_email = ctk.CTkLabel(
            row_email_genero,
            text="Email",
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        lbl_email.grid(row=0, column=0, sticky="w", pady=(0, 3))

        lbl_genero = ctk.CTkLabel(
            row_email_genero,
            text="Gênero",
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        lbl_genero.grid(row=0, column=1, sticky="w", pady=(0, 3))

        # Campos na mesma linha (row 1)
        email_frame_inner = ctk.CTkFrame(row_email_genero, fg_color="transparent")
        email_frame_inner.grid(row=1, column=0, sticky="ew", padx=(0, 5))

        email_entry = ctk.CTkEntry(
            email_frame_inner,
            placeholder_text="seu@email.com",
            height=44,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        email_entry.pack(fill="x")
        entries.append(email_entry)

        genero_frame_inner = ctk.CTkFrame(row_email_genero, fg_color="transparent", width=200)
        genero_frame_inner.grid(row=1, column=1, sticky="ew")
        genero_frame_inner.grid_propagate(False)

        self.sexo_profissional = ctk.CTkComboBox(
            genero_frame_inner,
            values=["Masculino", "Feminino"],
            height=44,
            width=200,
            state="readonly",
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            button_color=COLORS["border"],
            button_hover_color=COLORS["border"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            dropdown_font=font("text")
        )
        self.sexo_profissional.set("")
        self.sexo_profissional.pack(fill="x")

        # Agora append do Confirmar Senha (mantendo ordem de índices esperada pelo salvamento)
        entries.append(self.confirma_senha_entry)

        self._secao_titulo(frame, "Tipo de Profissional")
        tipo_container = ctk.CTkFrame(frame, fg_color="transparent")
        tipo_container.pack(fill="x", padx=self.padding_lateral, pady=(0, 10))
        
        ctk.CTkLabel(
            tipo_container, 
            text="Selecione o tipo", 
            font=font("text"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 3))
        
        self.tipo_profissional = ctk.CTkOptionMenu(
            tipo_container,
            values=["Médico", "Gerente"],
            height=44,
            fg_color=COLORS["input_bg"], 
            button_color=COLORS["border"], 
            button_hover_color=COLORS["border"],
            text_color=COLORS["text"], 
            dropdown_fg_color=COLORS["card"], 
            dropdown_text_color=COLORS["text"],
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
        self.cro_entry.bind("<KeyRelease>", self._validar_cro_em_tempo_real)
        self.cro_entry.bind("<FocusOut>", self._validar_cro_em_tempo_real)
        # Aplicar máscara de Telefone para profissional
        self.mascaras_profissional.adicionar_campo('telefone_medico', self.telefone_entry, 'telefone')

        # Adicionar campo de especialidade para médico
        self._secao_titulo(self.frame_medico, "Especialidade")
        especialidade_container = ctk.CTkFrame(self.frame_medico, fg_color="transparent")
        especialidade_container.pack(fill="x", padx=self.padding_lateral, pady=(0, 10))
        
        ctk.CTkLabel(
            especialidade_container, 
            text="Selecione a especialidade", 
            font=font("text"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=(0, 3))
        
        self.especialidade_map = {self.ESPECIALIDADE_PLACEHOLDER: None}
        especialidade_valores = [self.ESPECIALIDADE_PLACEHOLDER]
        try:
            especialidades = ConsultaController.listar_especialidades_para_combo()
            if especialidades:
                especialidade_valores = [self.ESPECIALIDADE_PLACEHOLDER] + [nome for _, nome in especialidades]
                self.especialidade_map = {nome: especialidade_id for especialidade_id, nome in especialidades}
                self.especialidade_map[self.ESPECIALIDADE_PLACEHOLDER] = None
        except Exception:
            pass
        
        self.especialidade_medico = ctk.CTkOptionMenu(
            especialidade_container,
            values=especialidade_valores,
            height=44,
            fg_color=COLORS["input_bg"], 
            button_color=COLORS["border"], 
            button_hover_color=COLORS["border"],
            text_color=COLORS["text"], 
            dropdown_fg_color=COLORS["card"], 
            dropdown_text_color=COLORS["text"],
            dropdown_font=font("text")
        )
        self.especialidade_medico.set(self.ESPECIALIDADE_PLACEHOLDER)
        self.especialidade_medico.pack(fill="x")

        self._ao_mudar_tipo_profissional("Médico")

        self.profissional_entries = entries
        self._botoes_acao(frame, "Salvar Profissional", target_entries=self.profissional_entries)
        
        return frame

    def _secao_titulo(self, parent, texto):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=(16, 8))

        ctk.CTkLabel(
            container,
            text=texto,
            font=font("subtitle", "bold"),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")

        linha = ctk.CTkFrame(container, height=2, width=52, fg_color=self.cor_primaria, corner_radius=1)
        linha.pack(anchor="w", pady=(4, 0))

    def _campo_duplo(self, parent, label1, label2, show1=None, show2=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=5)

        frame1 = ctk.CTkFrame(container, fg_color="transparent")
        frame1.pack(side="left", expand=True, fill="x", padx=(0, 5))

        ctk.CTkLabel(
            frame1,
            text=label1,
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        entry1 = ctk.CTkEntry(
            frame1,
            placeholder_text=f"Digite {label1.lower()}",
            height=44, show=show1,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        entry1.pack(fill="x")

        frame2 = ctk.CTkFrame(container, fg_color="transparent")
        frame2.pack(side="left", expand=True, fill="x", padx=(5, 0))

        ctk.CTkLabel(
            frame2,
            text=label2,
            font=font("text"),
            text_color=COLORS["text_secondary"],
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))

        entry2 = ctk.CTkEntry(
            frame2,
            placeholder_text=f"Digite {label2.lower()}",
            height=44, show=show2,
            fg_color=COLORS["input_bg"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            text_color=COLORS["text"],
            placeholder_text_color=COLORS["text_muted"]
        )
        entry2.pack(fill="x")

        return entry1, entry2

    def _campo_triplo(self, parent, label1, label2, label3, show1=None, show2=None, show3=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=5)

        entries_list = []
        labels = (label1, label2, label3)
        shows = (show1, show2, show3)
        for index, (label, show) in enumerate(zip(labels, shows)):
            frame_i = ctk.CTkFrame(container, fg_color="transparent")
            frame_i.pack(
                side="left",
                expand=True,
                fill="x",
                padx=(0, 5) if index < 2 else (0, 0)
            )

            ctk.CTkLabel(
                frame_i,
                text=label,
                font=font("text"),
                text_color=COLORS["text_secondary"],
                anchor="w"
            ).pack(anchor="w", pady=(0, 3))

            if label == "UF":
                entry_i = ctk.CTkComboBox(
                    frame_i,
                    values=self.carregar_estados(),
                    height=44,
                    state="readonly",
                    fg_color=COLORS["input_bg"],
                    border_color=COLORS["border"],
                    border_width=1,
                    corner_radius=8,
                    text_color=COLORS["text"],
                    button_color=COLORS["border"],
                    button_hover_color=COLORS["border"],
                    dropdown_fg_color=COLORS["card"],
                    dropdown_text_color=COLORS["text"],
                    dropdown_font=font("text"),
                    command=self._ao_selecionar_uf_paciente
                )
                entry_i.set("")
            elif label == "Cidade":
                entry_i = CidadeSearchComboBox(
                    frame_i,
                    values=[],
                    height=44,
                    fg_color=COLORS["input_bg"],
                    border_color=COLORS["border"],
                    border_width=1,
                    corner_radius=8,
                    text_color=COLORS["text"],
                    placeholder_text_color=COLORS["text_muted"]
                )
                entry_i.set("")
            else:
                placeholder = f"Digite {label.lower()}"
                if label == "Confirmar Senha":
                    placeholder = "Confirme sua senha"
                if label == "Email":
                    placeholder = "seu@email.com"

                entry_i = ctk.CTkEntry(
                    frame_i,
                    placeholder_text=placeholder,
                    height=44,
                    show=show,
                    fg_color=COLORS["input_bg"],
                    border_color=COLORS["border"],
                    border_width=1,
                    corner_radius=8,
                    text_color=COLORS["text"],
                    placeholder_text_color=COLORS["text_muted"]
                )
            entry_i.pack(fill="x")
            entries_list.append(entry_i)

        return tuple(entries_list)

    def _configurar_campos_endereco_paciente(self, cep_entry, uf_entry, cidade_entry, rua_entry):
        self.endereco_paciente_entries = {
            "CEP": cep_entry,
            "UF": uf_entry,
            "Cidade": cidade_entry,
            "Logradouro": rua_entry
        }

        cep_entry.bind("<KeyRelease>", self._ao_digitar_cep_paciente, add="+")
        self._bind_combobox_keyrelease(cidade_entry, self._ao_digitar_cidade_paciente)
        cidade_entry.bind("<FocusOut>", self._validar_cidade_paciente, add="+")

    def carregar_estados(self):
        return LocalidadesService.carregar_estados()

    def carregar_cidades(self, uf):
        cidades = LocalidadesService.carregar_cidades(uf)
        cidade_entry = getattr(self, "endereco_paciente_entries", {}).get("Cidade")
        if cidade_entry:
            cidade_atual = cidade_entry.get().strip()
            cidade_entry.configure(values=cidades)
            if cidade_atual and not LocalidadesService.cidade_existe(uf, cidade_atual):
                cidade_entry.set("")
        return cidades

    def filtrar_cidades(self, termo):
        uf = self.endereco_paciente_entries["UF"].get().strip()
        cidades = LocalidadesService.filtrar_cidades(uf, termo)
        self.endereco_paciente_entries["Cidade"].configure(values=cidades)
        return cidades

    def selecionar_cidade(self, cidade):
        campos = self.endereco_paciente_entries
        uf = campos["UF"].get().strip()
        cidade_valida = LocalidadesService.selecionar_cidade(uf, cidade)
        campos["Cidade"].set(cidade_valida)
        return cidade_valida

    def preencher_por_cep(self, endereco):
        self._aplicar_endereco_paciente(endereco)

    def _ao_selecionar_uf_paciente(self, uf):
        self.carregar_cidades(uf)

    def _ao_digitar_cidade_paciente(self, event=None):
        if self._aplicando_mascara_endereco:
            return

        if not getattr(self, "endereco_paciente_entries", None):
            return

        cidade_entry = self.endereco_paciente_entries["Cidade"]
        self.filtrar_cidades(cidade_entry.get())

    def _validar_cidade_paciente(self, event=None):
        if not getattr(self, "endereco_paciente_entries", None):
            return

        cidade_entry = self.endereco_paciente_entries["Cidade"]
        cidade = cidade_entry.get().strip()
        if cidade and not self.selecionar_cidade(cidade):
            cidade_entry.set("")

    def _bind_combobox_keyrelease(self, combobox, callback):
        combobox.bind("<KeyRelease>", callback, add="+")
        entry_interno = getattr(combobox, "_entry", None)
        if entry_interno:
            entry_interno.bind("<KeyRelease>", callback, add="+")

    def formatar_cep(self, valor):
        return EnderecoService.formatar_cep(valor)

    def buscar_cep(self, cep):
        EnderecoService.buscar_cep_async(
            cep,
            callback=self._preencher_endereco_paciente_por_cep,
            erro_callback=self._tratar_erro_cep_paciente
        )

    def formatar_uf(self, valor):
        return EnderecoService.formatar_uf(valor)

    def formatar_cidade(self, valor):
        filtrado = ''.join(c for c in valor if c.isalpha() or c == " ")
        palavras_pequenas = {"de", "da", "do", "dos", "das", "e"}
        palavras = []

        for indice, palavra in enumerate(filtrado.split(" ")):
            if not palavra:
                palavras.append(palavra)
                continue

            palavra_lower = palavra.lower()
            if palavra_lower in {"sao", "s\u00e3o"}:
                palavras.append("S\u00e3o")
            elif indice > 0 and palavra_lower in palavras_pequenas:
                palavras.append(palavra_lower)
            else:
                palavras.append(palavra_lower.capitalize())

        formatado = " ".join(palavras)
        return formatado, len(formatado)

    def _ao_digitar_cep_paciente(self, event=None):
        if not hasattr(self, "endereco_paciente_entries"):
            return

        cep_entry = self.endereco_paciente_entries["CEP"]
        self._aplicar_mascara_entry(
            cep_entry,
            self.formatar_cep,
            lambda texto: [c for c in texto if c.isdigit()]
        )

        cep_numeros = EnderecoService.extrair_cep_numeros(cep_entry.get())
        if len(cep_numeros) != 8:
            self._ultimo_cep_consultado = None
            return

        if cep_numeros == self._ultimo_cep_consultado:
            return

        if self._cep_after_id:
            try:
                self.after_cancel(self._cep_after_id)
            except Exception:
                pass

        self._cep_after_id = self.after(350, lambda: self._consultar_cep_paciente(cep_numeros))

    def _consultar_cep_paciente(self, cep_numeros):
        if not hasattr(self, "endereco_paciente_entries"):
            return

        cep_atual = EnderecoService.extrair_cep_numeros(self.endereco_paciente_entries["CEP"].get())
        if cep_atual != cep_numeros:
            return

        self._ultimo_cep_consultado = cep_numeros
        self.buscar_cep(cep_numeros)

    def _preencher_endereco_paciente_por_cep(self, endereco):
        if not endereco:
            self.after(0, self._limpar_endereco_paciente_automatico)
            return

        self.after(0, lambda: self._aplicar_endereco_paciente(endereco))

    def _aplicar_endereco_paciente(self, endereco):
        if not hasattr(self, "endereco_paciente_entries"):
            return

        campos = self.endereco_paciente_entries
        uf, _ = self.formatar_uf(endereco.get("estado", ""))
        campos["UF"].set(uf)
        self.carregar_cidades(uf)
        self.selecionar_cidade(endereco.get("cidade", ""))
        self._definir_valor_entry(campos["Logradouro"], endereco.get("rua", ""))

    def _tratar_erro_cep_paciente(self, mensagem):
        self.after(0, lambda: self._mostrar_erro_cep_paciente(mensagem))

    def _mostrar_erro_cep_paciente(self, mensagem):
        self._limpar_endereco_paciente_automatico()
        self._mostrar_mensagem(
            f"{mensagem}. Campos de endereco preenchidos automaticamente foram limpos.",
            sucesso=False
        )

    def _limpar_endereco_paciente_automatico(self):
        if not hasattr(self, "endereco_paciente_entries"):
            return

        for nome in ("UF", "Cidade", "Logradouro"):
            self._definir_valor_entry(self.endereco_paciente_entries[nome], "")

    def _aplicar_mascara_entry(self, entry, formatter, contador_logico):
        if self._aplicando_mascara_endereco:
            return

        try:
            self._aplicando_mascara_endereco = True
            texto_antigo = entry.get()
            pos_antiga = entry.index("insert")
            logicos_antes = len(contador_logico(texto_antigo[:pos_antiga]))
            formatado, _ = formatter(texto_antigo)

            if texto_antigo != formatado:
                entry.delete(0, "end")
                entry.insert(0, formatado)

            entry.icursor(self._calcular_cursor_logico(formatado, logicos_antes, contador_logico))
        finally:
            self._aplicando_mascara_endereco = False

    def _calcular_cursor_logico(self, texto, quantidade_logica, contador_logico):
        if quantidade_logica <= 0:
            return 0

        vistos = 0
        for indice, caractere in enumerate(texto):
            if contador_logico(caractere):
                vistos += 1
                if vistos >= quantidade_logica:
                    return indice + 1

        return len(texto)

    def _definir_valor_entry(self, entry, valor, formatter=None):
        texto = str(valor or "")
        if formatter:
            texto, _ = formatter(texto)

        if isinstance(entry, ctk.CTkComboBox):
            entry.set(texto)
            return

        entry.delete(0, "end")
        entry.insert(0, texto)

    def _ao_mudar_tipo_profissional(self, choice):
        try:
            self.frame_medico.pack_forget()
        except Exception:
            pass
        
        if choice == "Médico":
            self.frame_medico.pack(fill="x")

    # =====================================================
    # BOTÕES DE AÇÃO - CORRIGIDO
    # =====================================================
    def _botoes_acao(self, parent, texto_principal, target_entries=None):
        # ESPAÇADOR PARA GARANTIR QUE OS BOTÕES APAREÇAM
        espacador = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        espacador.pack(fill="x")
        
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=14)

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

        def _limpar():
            entries = target_entries or []
            for e in entries:
                try:
                    content = e.get()
                    if content:
                        if isinstance(e, ctk.CTkComboBox):
                            e.set("")
                        else:
                            e.delete(0, "end")
                except Exception:
                    pass

        ActionButtons(
            container,
            primary_text=texto_principal.upper(),
            secondary_text="LIMPAR",
            on_primary=_salvar,
            on_secondary=_limpar
        ).pack(anchor="w")

    # =====================================================
    # COMPONENTES REUTILIZÁVEIS
    # =====================================================
    def _titulo(self, parent, texto):
        ctk.CTkLabel(
            parent, text=texto, font=font("title", "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=self.padding_lateral, pady=(24, 17))

    def _entry(self, parent, placeholder, show=None):
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder, height=44, show=show,
            fg_color=COLORS["input_bg"], border_color=COLORS["border"], 
            text_color=COLORS["text"], placeholder_text_color=COLORS["text_muted"], 
            corner_radius=8
        )
        entry.pack(fill="x", padx=self.padding_lateral, pady=8)
        return entry

    # =====================================================
    # MÉTODOS DE SALVAMENTO
    # =====================================================
    def _salvar_paciente(self, entries):
        """Valida e salva paciente no banco de dados"""
        try:
            nome = entries[0].get().strip()
            cpf = self.mascaras_paciente.obter_valor_numerico().get('cpf_paciente', '').strip()
            data_nasc = entries[2].get().strip()
            telefone = self.mascaras_paciente.obter_valor_numerico().get('telefone_paciente', '').strip()
            cep = entries[4].get().strip()
            uf = entries[5].get().strip()
            cidade = entries[6].get().strip()
            rua = entries[7].get().strip()
            numero = entries[8].get().strip()
            complemento = entries[9].get().strip()
            email = entries[10].get().strip()
            senha = entries[11].get().strip()
            confirma_senha = entries[12].get().strip()
            
            # Validações básicas
            
            # Verificar campos obrigatórios com mensagens específicas
            if not nome:
                self._mostrar_mensagem("❌ Nome completo é obrigatório!", sucesso=False)
                return
            
            if not email:
                self._mostrar_mensagem("❌ Email é obrigatório!", sucesso=False)
                return
            
            if not telefone:
                self._mostrar_mensagem("❌ Telefone é obrigatório!", sucesso=False)
                return
            
            if not senha:
                self._mostrar_mensagem("❌ Senha é obrigatória!", sucesso=False)
                return

            if not confirma_senha:
                self._mostrar_mensagem("❌ Confirmar senha é obrigatório!", sucesso=False)
                return

            if senha != confirma_senha:
                self._mostrar_mensagem("❌ As senhas informadas não coincidem.", sucesso=False)
                return
            
            # Validações extras de formato
            if '@' not in email:
                self._mostrar_mensagem("❌ Email inválido. Deve conter '@'", sucesso=False)
                return
            
            if len(telefone) < 10:
                self._mostrar_mensagem("❌ Telefone inválido. Deve ter pelo menos 10 dígitos", sucesso=False)
                return
            
            # Converter data de nascimento para o formato ISO esperado pelo banco
            data_nasc_iso = None
            if data_nasc:
                try:
                    data_nasc_iso = datetime.strptime(data_nasc, '%d/%m/%Y').strftime('%Y-%m-%d')
                except ValueError:
                    data_nasc_iso = data_nasc
            
            print(f"[DEBUG] ✓ Validação passou! Prosseguindo com o salvamento...")
            
            resultado = PacienteController.criar_paciente(
                nome=nome,
                cpf=cpf or None,
                sexo=None,
                email=email,
                data_nascimento=data_nasc_iso or None,
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

    def _validar_cro_em_tempo_real(self, event=None):
        """
        Validação em tempo real para o campo CRO enquanto o usuário digita.

        Regras aplicadas aqui (apenas comportamento de UI):
        - Aceita apenas dígitos (0-9)
        - Permite até 5 dígitos durante a digitação
        - Remove quaisquer letras ou caracteres especiais imediatamente
        """
        try:
            raw = (self.cro_entry.get() or "").strip()
            if not raw:
                return

            # Permitir apenas dígitos, letras e hífen na digitação de CRO.
            # Aceitamos tanto formato numérico (1234/12345) quanto opcionais prefixos de UF.
            filtered = ''.join(ch.upper() for ch in raw if ch.isalnum() or ch == '-')
            if filtered.count('-') > 1:
                parts = filtered.split('-')
                filtered = parts[0] + '-' + ''.join(parts[1:])

            filtered = filtered[:8]

            if filtered != self.cro_entry.get().strip():
                self.cro_entry.delete(0, 'end')
                self.cro_entry.insert(0, filtered)

        except Exception:
            pass

    def _validar_cro(self, cro):
        """
        Validação final do CRO antes de salvar.

        Regras (apenas números):
        - Somente dígitos 0-9
        - Comprimento mínimo: 4
        - Comprimento máximo: 5
        """
        if not cro:
            return False, "CRO inválido. Deve conter entre 4 e 5 dígitos numéricos."

        texto = str(cro).strip().upper()
        if not re.fullmatch(r"\d{4,5}|[A-Z]{2}-?\d{4,5}", texto):
            return False, "CRO inválido. Utilize 1234, 12345, UF-1234 ou UF-12345."

        return True, ""

    def _salvar_medico(self, entries):
        """Valida e salva médico no banco de dados"""
        try:
            nome = entries[0].get().strip()
            email = entries[2].get().strip()
            cro = self.cro_entry.get().strip()
            telefone = self.mascaras_profissional.obter_valor_numerico().get('telefone_medico', '').strip()
            senha = self.senha_entry.get().strip()
            confirma_senha = self.confirma_senha_entry.get().strip()
            especialidade = self.especialidade_medico.get().strip()
            
            # Validações específicas
            if not nome:
                self._mostrar_mensagem("❌ Nome completo é obrigatório!", sucesso=False)
                return
            
            if not email:
                self._mostrar_mensagem("❌ Email é obrigatório!", sucesso=False)
                return
            
            if '@' not in email:
                self._mostrar_mensagem("❌ Email inválido. Deve conter '@'", sucesso=False)
                return
            
            if not cro:
                self._mostrar_mensagem("❌ CRO é obrigatório!", sucesso=False)
                return

            cro_valido, msg_cro = self._validar_cro(cro)
            if not cro_valido:
                self._mostrar_mensagem(f"❌ {msg_cro}", sucesso=False)
                return
            
            if not telefone:
                self._mostrar_mensagem("❌ Telefone é obrigatório!", sucesso=False)
                return
            
            if len(telefone) < 10:
                self._mostrar_mensagem("❌ Telefone inválido. Deve ter pelo menos 10 dígitos", sucesso=False)
                return
            
            if not senha:
                self._mostrar_mensagem("❌ Senha é obrigatória!", sucesso=False)
                return
            
            if especialidade == self.ESPECIALIDADE_PLACEHOLDER:
                self._mostrar_mensagem("Selecione uma especialidade.", sucesso=False)
                return

            especialidade_id = self.especialidade_map.get(especialidade)
            if especialidade_id is None:
                self._mostrar_mensagem("Selecione uma especialidade.", sucesso=False)
                return
            
            if senha != confirma_senha:
                self._mostrar_mensagem("❌ As senhas não coincidem", sucesso=False)
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
                especialidades=[especialidade_id]
            )
            
            if resultado["sucesso"]:
                self._mostrar_mensagem(resultado["mensagem"], sucesso=True)
                self._limpar_campos([entries[0], entries[1]])
                self._limpar_campos([self.cro_entry, self.telefone_entry])
                self._limpar_campos([self.senha_entry, self.confirma_senha_entry])
                self.especialidade_medico.set(self.ESPECIALIDADE_PLACEHOLDER)

                print("========== CADASTRO ===========")
                print("Médico salvo com sucesso")
                print(f"ID do médico: {resultado.get('id')}")
                print(f"Clínica: {self.clinica_id}")

                app = self.winfo_toplevel()
                target = None
                if hasattr(app, 'frames') and 'gerenciamento' in app.frames:
                    target = app.frames['gerenciamento']
                else:
                    parent = self.master
                    while parent is not None and target is None:
                        if hasattr(parent, 'frames') and 'gerenciamento' in parent.frames:
                            target = parent.frames['gerenciamento']
                        parent = getattr(parent, 'master', None)

                if target is not None:
                    print("Chamando atualização do Gerenciamento...")
                    print(f"Instância alvo Gerenciamento id(self): {id(target)}")
                    try:
                        target.refresh()
                    except Exception as e:
                        print(f"Erro ao atualizar Gerenciamento: {e}")
                else:
                    print("Gerenciamento não encontrado para refresh.")
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
            
            # Validações específicas
            if not nome:
                self._mostrar_mensagem("❌ Nome completo é obrigatório!", sucesso=False)
                return
            
            if not email:
                self._mostrar_mensagem("❌ Email é obrigatório!", sucesso=False)
                return
            
            if '@' not in email:
                self._mostrar_mensagem("❌ Email inválido. Deve conter '@'", sucesso=False)
                return
            
            if not senha:
                self._mostrar_mensagem("❌ Senha é obrigatória!", sucesso=False)
                return
            
            if senha != confirma_senha:
                self._mostrar_mensagem("❌ As senhas não coincidem", sucesso=False)
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
                if isinstance(e, ctk.CTkComboBox):
                    e.set("")
                else:
                    e.delete(0, "end")
            except Exception:
                pass

    def _mostrar_mensagem(self, mensagem, sucesso=True):
        """Exibe uma mensagem de feedback ao usuário"""
        cor = COLORS["success"] if sucesso else COLORS["danger"]
        msg_label = ctk.CTkLabel(
            self.content_card,
            text=mensagem,
            text_color=cor,
            font=font("text", "bold")
        )
        msg_label.pack(pady=10)
        
        # Remove a mensagem após 3 segundos
        self.after(3000, lambda: msg_label.pack_forget())
