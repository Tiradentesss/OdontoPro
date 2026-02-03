from .base import BaseScreen
import customtkinter as ctk

class Cadastro(BaseScreen):
    def __init__(self, parent):
        super().__init__(parent, "Cadastro")

        # =============================
        # CONTAINER PRINCIPAL
        # =============================
        container = ctk.CTkFrame(
            self.content_card,
            fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=30, pady=20)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # =============================
        # CARD - CADASTRO DE PACIENTES
        # =============================
        card_paciente = ctk.CTkFrame(
            container,
            corner_radius=20,
            fg_color="#FFFFFF"
        )
        card_paciente.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        self._titulo(card_paciente, "Cadastro de Pacientes")

        self._entry(card_paciente, "Nome completo")
        self._entry(card_paciente, "Data de nascimento")
        self._entry(card_paciente, "Endereço")
        self._entry(card_paciente, "CPF")
        self._entry(card_paciente, "Telefone / WhatsApp")
        self._entry(card_paciente, "Email")
        self._entry(card_paciente, "Senha", show="*")

        self._botao_salvar(card_paciente)

        # =============================
        # CARD - CADASTRO DE PROFISSIONAL
        # =============================
        card_profissional = ctk.CTkFrame(
            container,
            corner_radius=20,
            fg_color="#FFFFFF"
        )
        card_profissional.grid(row=0, column=1, sticky="nsew")

        self._titulo(card_profissional, "Cadastro de Profissional")

        self._entry(card_profissional, "Nome completo")

        ctk.CTkOptionMenu(
            card_profissional,
            values=["Selecione", "Dentista", "Auxiliar", "Recepcionista"],
            height=40,
            fg_color="#F9FAFB",
            button_color="#E5E7EB",
            text_color="#111827"
        ).pack(fill="x", padx=30, pady=(10, 5))

        linha = ctk.CTkFrame(card_profissional, fg_color="transparent")
        linha.pack(fill="x", padx=30, pady=5)

        ctk.CTkEntry(linha, placeholder_text="CRO", height=40)\
            .pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkEntry(linha, placeholder_text="Telefone", height=40)\
            .pack(side="left", expand=True, fill="x")

        self._entry(card_profissional, "Email")
        self._entry(card_profissional, "Senha", show="*")

        self._botao_salvar(card_profissional)

    # =====================================================
    # COMPONENTES REUTILIZÁVEIS
    # =====================================================
    def _titulo(self, parent, texto):
        ctk.CTkLabel(
            parent,
            text=texto,
            font=("Poppins", 18, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=30, pady=(25, 15))

    def _entry(self, parent, placeholder, show=None):
        ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40,
            show=show,
            fg_color="#F9FAFB",
            border_color="#E5E7EB",
            text_color="#111827"
        ).pack(fill="x", padx=30, pady=5)

    def _botao_salvar(self, parent):
        ctk.CTkButton(
            parent,
            text="Salvar",
            height=42,
            fg_color="#06D6D6",
            hover_color="#04B4B4",
            text_color="#0F172A",
            corner_radius=20
        ).pack(pady=25)

    pass
