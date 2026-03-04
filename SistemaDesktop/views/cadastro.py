from .base import BaseScreen
from .theme import font, ICON_SIZE
import customtkinter as ctk

class Cadastro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Cadastro")

        # Configuração de cores - PALETA MAIS MODERNA
        self.cor_fundo_card = "#FFFFFF"
        self.cor_aba_ativa = "#FFFFFF"
        self.cor_aba_inativa = "#F3F4F6"
        self.cor_texto_ativo = "#0EA5E9"
        self.cor_texto_inativo = "#6B7280"
        self.cor_borda = "#E5E7EB"
        self.cor_primaria = "#0EA5E9"
        self.cor_primaria_hover = "#0284C7"
        
        self.padding_lateral = 60

        self.paciente_entries = []
        self.profissional_entries = []

        # =============================
        # 1. BARRA DE ABAS (TOPO) - AUMENTO MODERADO
        # =============================
        self.tab_bar = ctk.CTkFrame(self.content_card, fg_color="transparent", height=44)  # 40 -> 44
        self.tab_bar.pack(fill="x", padx=125, pady=(9, 0), anchor="nw")  # 8 -> 9

        self.btn_pacientes = ctk.CTkButton(
            self.tab_bar, text="👤   Pacientes",  # 2 espaços -> 3 espaços
            font=("Poppins", 15, "bold"),  # 14 -> 15
            width=135, height=37, corner_radius=6,  # 125x34 -> 135x37
            command=lambda: self._trocar_aba("Pacientes")
        )
        self.btn_pacientes.pack(side="left", padx=(0, 5))  # 4 -> 5

        self.btn_profissionais = ctk.CTkButton(
            self.tab_bar, text="📋   Profissionais",  # 2 espaços -> 3 espaços
            font=("Poppins", 15, "bold"),  # 14 -> 15
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
        self.container_outer.pack(fill="both", expand=True, padx=80, pady=(6, 8))

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
            font=("Poppins", 16, "bold"),  # 15 -> 16
            text_color="#374151"
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
            font=("Poppins", 14),  # 13 -> 14
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))  # 2 -> 3

        entry1 = ctk.CTkEntry(
            frame1,
            placeholder_text=f"Digite {label1.lower()}",
            height=44, show=show1,  # 40 -> 44
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,  # 4 -> 5
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        entry1.pack(fill="x")

        frame2 = ctk.CTkFrame(container, fg_color="transparent")
        frame2.pack(side="left", expand=True, fill="x", padx=(5, 0))

        ctk.CTkLabel(
            frame2,
            text=label2,
            font=("Poppins", 14),  # 13 -> 14
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))  # 2 -> 3

        entry2 = ctk.CTkEntry(
            frame2,
            placeholder_text=f"Digite {label2.lower()}",
            height=44, show=show2,  # 40 -> 44
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,  # 4 -> 5
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
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
                font=("Poppins", 14),  # 13 -> 14
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

        self._secao_titulo(frame, "Dados Pessoais")
        entries = []
        e1, e2 = self._campo_duplo(frame, "Nome completo", "Email")
        entries.extend([e1, e2])

        self._secao_titulo(frame, "Tipo de Profissional")
        tipo_container = ctk.CTkFrame(frame, fg_color="transparent")
        tipo_container.pack(fill="x", padx=self.padding_lateral, pady=(0, 10))  # 9 -> 10
        
        ctk.CTkLabel(
            tipo_container, 
            text="Selecione o tipo", 
            font=("Poppins", 14),  # 13 -> 14
            text_color="#4B5563"
        ).pack(anchor="w", pady=(0, 3))  # 2 -> 3
        
        self.tipo_profissional = ctk.CTkOptionMenu(
            tipo_container,
            values=["Dentista", "Auxiliar", "Recepcionista"],
            height=44,  # 40 -> 44
            fg_color="#F9FAFB", 
            button_color="#E5E7EB", 
            button_hover_color="#D1D5DB",
            text_color="#111827", 
            dropdown_fg_color="#FFFFFF", 
            dropdown_text_color="#111827",
            dropdown_font=("Poppins", 14),  # 13 -> 14
            command=self._ao_mudar_tipo_profissional
        )
        self.tipo_profissional.pack(fill="x")

        self.campos_dinamicos_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.campos_dinamicos_container.pack(fill="x", pady=(0, 10))  # 9 -> 10

        self.frame_cro_telefone = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.cro_entry, self.telefone_entry = self._campo_duplo(
            self.frame_cro_telefone, "CRO", "Telefone"
        )
        entries.extend([self.cro_entry, self.telefone_entry])
        
        self.frame_recepcionista = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.recep_entry1, self.recep_entry2 = self._campo_duplo(
            self.frame_recepcionista, "Turno (Manhã/Tarde)", "Telefone"
        )
        entries.extend([self.recep_entry1, self.recep_entry2])
        
        self.frame_auxiliar = ctk.CTkFrame(self.campos_dinamicos_container, fg_color="transparent")
        self.aux_entry = self._entry_unico(
            self.frame_auxiliar, "Especialização em auxílio"
        )
        entries.append(self.aux_entry)

        self._secao_titulo(frame, "Acesso ao Sistema")
        self.senha_entry, self.confirma_senha_entry = self._campo_duplo(
            frame, "Senha", "Confirme a Senha", show1="*", show2="*"
        )
        entries.extend([self.senha_entry, self.confirma_senha_entry])

        self._ao_mudar_tipo_profissional("Dentista")

        self.profissional_entries = entries
        self._botoes_acao(frame, "Salvar Profissional", target_entries=self.profissional_entries)
        return frame

    def _entry_unico(self, parent, placeholder, show=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", padx=self.padding_lateral, pady=5)  # 4 -> 5
        
        ctk.CTkLabel(
            container,
            text=placeholder,
            font=("Poppins", 14),  # 13 -> 14
            text_color="#4B5563",
            anchor="w"
        ).pack(anchor="w", pady=(0, 3))  # 2 -> 3
        
        entry = ctk.CTkEntry(
            container,
            placeholder_text=f"Digite {placeholder.lower()}",
            height=44, show=show,  # 40 -> 44
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            border_width=1,
            corner_radius=5,  # 4 -> 5
            text_color="#111827",
            placeholder_text_color="#9CA3AF"
        )
        entry.pack(fill="x")
        
        return entry

    def _ao_mudar_tipo_profissional(self, choice):
        try:
            self.frame_cro_telefone.pack_forget()
            self.frame_recepcionista.pack_forget()
            self.frame_auxiliar.pack_forget()
        except Exception:
            pass
        
        if choice == "Dentista":
            self.frame_cro_telefone.pack(fill="x")
            self._atualizar_labels_cro_telefone("CRO", "Telefone")
            
        elif choice == "Auxiliar":
            self.frame_auxiliar.pack(fill="x")
            self._atualizar_label_auxiliar("Especialização em auxílio")
            
        elif choice == "Recepcionista":
            self.frame_recepcionista.pack(fill="x")
            self._atualizar_labels_recepcionista("Turno (Manhã/Tarde)", "Telefone")

    def _atualizar_labels_cro_telefone(self, label1, label2):
        pass

    def _atualizar_label_auxiliar(self, label):
        pass

    def _atualizar_labels_recepcionista(self, label1, label2):
        pass

    def _botoes_acao(self, parent, texto_principal, target_entries=None):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="bottom", fill="x", padx=self.padding_lateral, pady=14)  # 12 -> 14

        def _salvar():
            print("Salvar chamado", len(target_entries or []))

        ctk.CTkButton(
            container,
            text=texto_principal.upper(),
            font=("Poppins", 15, "bold"),  # 14 -> 15
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
            font=("Poppins", 15),  # 14 -> 15
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
            parent, text=texto, font=("Poppins", 24, "bold"),  # 22 -> 24
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
            parent, text=texto.upper(), font=("Poppins", 15, "bold"),  # 14 -> 15
            height=44, width=330,  # 40x310 -> 44x330
            fg_color="#06B6D4", hover_color="#0891B2", text_color="#FFFFFF",
            corner_radius=5  # 4 -> 5
        ).pack(pady=22)  # 20 -> 22