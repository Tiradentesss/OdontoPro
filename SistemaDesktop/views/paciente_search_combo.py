"""
Componente de pesquisa de pacientes com padrão de dropdown.
Busca em tempo real do banco de dados por Nome ou CPF.
"""

import customtkinter as ctk
from controllers.consulta_controller import ConsultaController
from .theme import COLORS


class PacienteSearchComboBox(ctk.CTkFrame):
    """Dropdown de pesquisa de pacientes com busca em tempo real no banco."""
    
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, fg_color="transparent")
        self.command = command
        self.dropdown = None
        self._close_after_id = None
        self.selected_index = 0
        self.pacientes_filtrados = []
        self.paciente_id_map = {}  # Mapeia índice da lista -> ID do paciente
        
        # StringVar para monitorar alterações
        self.search_var = ctk.StringVar()
        try:
            # tkinter moderno: usa trace_add
            self.search_var.trace_add('write', self._ao_alterar_search)
        except AttributeError:
            # fallback para versões antigas do Tk
            self.search_var.trace('w', self._ao_alterar_search)
        
        # Entry principal
        kwargs['textvariable'] = self.search_var
        self.entry = ctk.CTkEntry(self, **kwargs)
        self.entry.pack(fill="x")
        self.entry.bind("<Button-1>", lambda event: self.abrir_lista())
        self.entry.bind("<FocusIn>", lambda event: self.abrir_lista())
        self.entry.bind("<Down>", self._mover_selecao_baixo)
        self.entry.bind("<Up>", self._mover_selecao_cima)
        self.entry.bind("<Return>", self._selecionar_atual)
        self.entry.bind("<Escape>", lambda event: self.fechar_lista())

    def get(self):
        """Retorna texto do entry."""
        return self.entry.get()

    def set(self, value):
        """Define texto no entry."""
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value or ""))

    def get_paciente_id(self):
        """Retorna ID do paciente selecionado."""
        return self.paciente_id_map.get(self.selected_index)

    def abrir_lista(self):
        """Abre dropdown com lista de pacientes."""
        if self.dropdown is not None:
            try:
                dropdown_existe = bool(self.dropdown.winfo_exists())
                dropdown_visivel = bool(self.dropdown.winfo_viewable())
            except Exception:
                dropdown_existe = False
                dropdown_visivel = False
            if dropdown_existe and dropdown_visivel:
                return
            if dropdown_existe:
                self.dropdown.destroy()
            self.dropdown = None
            self.lista_frame = None

        largura = max(self.winfo_width(), 300)
        altura = 500  # Aumentado para 500
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height() + 2

        # Criar janela flutuante
        self.dropdown = ctk.CTkToplevel(self)
        self.dropdown.overrideredirect(True)
        self.dropdown.geometry(f"{largura}x{altura}+{x}+{y}")
        self.dropdown.configure(fg_color=COLORS["card"])
        self.dropdown.bind("<Escape>", lambda event: self.fechar_lista())
        self.dropdown.bind("<FocusOut>", self._fechar_se_foco_sair)
        if self._close_after_id:
            self.after_cancel(self._close_after_id)
            self._close_after_id = None

        # Frame com scroll para lista
        self.lista_frame = ctk.CTkScrollableFrame(
            self.dropdown,
            height=420,  # Aumentado para 420
            fg_color=COLORS["card"],
            corner_radius=8
        )
        self.lista_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        
        self.selected_index = 0
        self._atualizar_lista([])
        self._buscar_pacientes(self.search_var.get())
        self.entry.focus_set()

    def fechar_lista(self):
        """Fecha dropdown."""
        if self._close_after_id:
            self.after_cancel(self._close_after_id)
            self._close_after_id = None
        if self.dropdown and self.dropdown.winfo_exists():
            self.dropdown.destroy()
        self.dropdown = None
        self.lista_frame = None

    def _ao_alterar_search(self, *args):
        """Callback disparado quando search_var muda (StringVar trace)."""
        # Proteção: verificar se o widget ainda existe (pode ter sido destruído)
        if not self.winfo_exists():
            print("[DEBUG PACIENTE] _ao_alterar_search: widget foi destruído, ignorando evento")
            return
        
        termo = self.search_var.get()
        if not self.dropdown or not self.dropdown.winfo_exists():
            self.abrir_lista()
            return
        self._buscar_pacientes(termo)

    def _buscar_pacientes(self, termo):
        """Busca pacientes no banco com o termo."""
        if len(termo.strip()) < 2:
            self.pacientes_filtrados = []
            self.paciente_id_map = {}
            print("[DEBUG PACIENTE] Termo muito curto, limpando lista")
        else:
            try:
                resultados = ConsultaController.buscar_pacientes_dinamico(termo, limite=20)
                self.pacientes_filtrados = resultados
                print(f"[DEBUG PACIENTE] ✓ Banco retornou {len(resultados)} pacientes para termo '{termo}'")
                # Mapear índice -> ID do paciente
                self.paciente_id_map = {idx: (id_pac, nome, cpf, email, telefone, data_nasc) 
                                       for idx, (id_pac, nome, cpf, email, telefone, data_nasc) in enumerate(resultados)}
            except Exception as e:
                print(f"[DEBUG PACIENTE] ✗ Erro ao buscar pacientes: {e}")
                self.pacientes_filtrados = []
                self.paciente_id_map = {}

        self.selected_index = 0
        self._atualizar_lista(self.pacientes_filtrados)

    def _atualizar_lista(self, pacientes):
        """Atualiza a listagem de pacientes no dropdown."""
        # Proteção: verificar se o widget ainda existe
        if not self.lista_frame.winfo_exists():
            return
        
        print(f"[DEBUG PACIENTE] _atualizar_lista: destruindo {len(self.lista_frame.winfo_children())} widgets antigos")
        
        for child in self.lista_frame.winfo_children():
            child.destroy()

        print(f"[DEBUG PACIENTE] _atualizar_lista: processando {len(pacientes)} pacientes")
        
        if not pacientes:
            no_results_label = ctk.CTkLabel(
                self.lista_frame,
                text="Nenhum paciente encontrado.",
                text_color=COLORS["text_muted"],
                anchor="w",
                height=40
            )
            no_results_label.grid(row=0, column=0, sticky="ew", padx=8, pady=8)
            print("[DEBUG PACIENTE] _atualizar_lista: nenhum paciente encontrado")
            return

        widgets_criados = 0
        for indice, (id_pac, nome, cpf, email, telefone, data_nasc) in enumerate(pacientes):
            try:
                # Formatar CPF
                cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}" if cpf else ""
                
                # Cor de fundo (selecionado ou não)
                fg_color = COLORS["hover"] if indice == self.selected_index else COLORS["input_bg"]
                
                # Frame para cada paciente (usando Frame em vez de Button para melhor controle)
                paciente_item = ctk.CTkFrame(
                    self.lista_frame,
                    fg_color=fg_color,
                    corner_radius=6,
                    height=60
                )
                paciente_item.grid(row=indice, column=0, sticky="ew", padx=2, pady=2, ipady=6)
                paciente_item.columnconfigure(0, weight=1)
                
                # Texto com informações do paciente
                info_text = f"{nome}\nCPF: {cpf_formatado}"
                info_label = ctk.CTkLabel(
                    paciente_item,
                    text=info_text,
                    text_color=COLORS["text"],
                    anchor="w",
                    justify="left",
                    font=("Arial", 10)
                )
                info_label.grid(row=0, column=0, sticky="ew", padx=12, pady=6)
                
                # Bind de clique no frame
                paciente_item.bind(
                    "<Button-1>",
                    lambda event, idx=indice: self._selecionar_por_indice(idx)
                )
                info_label.bind(
                    "<Button-1>",
                    lambda event, idx=indice: self._selecionar_por_indice(idx)
                )
                
                widgets_criados += 1
                
            except Exception as e:
                print(f"[DEBUG PACIENTE] ✗ Erro ao criar widget para paciente {indice}: {e}")
        
        print(f"[DEBUG PACIENTE] ✓ {widgets_criados} widgets criados e adicionados ao frame")
        self.lista_frame.columnconfigure(0, weight=1)

    def _mover_selecao_baixo(self, event=None):
        """Navega para baixo com seta."""
        if not self.dropdown or not self.pacientes_filtrados:
            self.abrir_lista()
            return "break"

        self.selected_index = min(self.selected_index + 1, len(self.pacientes_filtrados) - 1)
        self._atualizar_lista(self.pacientes_filtrados)
        return "break"

    def _mover_selecao_cima(self, event=None):
        """Navega para cima com seta."""
        if not self.dropdown or not self.pacientes_filtrados:
            return "break"

        self.selected_index = max(self.selected_index - 1, 0)
        self._atualizar_lista(self.pacientes_filtrados)
        return "break"

    def _selecionar_atual(self, event=None):
        """Seleciona item atualmente destaquado."""
        if self.pacientes_filtrados and 0 <= self.selected_index < len(self.pacientes_filtrados):
            self._selecionar_por_indice(self.selected_index)
        return "break"

    def _selecionar_por_indice(self, indice):
        """Seleciona paciente por índice."""
        print(f"[DEBUG PACIENTE] _selecionar_por_indice: indice={indice}, total={len(self.pacientes_filtrados)}")
        
        if 0 <= indice < len(self.pacientes_filtrados):
            id_pac, nome, cpf, email, telefone, data_nasc = self.pacientes_filtrados[indice]
            print(f"[DEBUG PACIENTE] ✓ Paciente selecionado: {nome} (ID: {id_pac})")
            
            self.set(nome)
            if self.command:
                print(f"[DEBUG PACIENTE] Chamando callback com dados do paciente")
                self.command(id_pac, nome, cpf, email, telefone, data_nasc)
            self.fechar_lista()
        else:
            print(f"[DEBUG PACIENTE] ✗ Índice inválido: {indice}")

    def _fechar_se_foco_sair(self, event=None):
        """Fecha dropdown se foco sair."""
        if self._close_after_id:
            self.after_cancel(self._close_after_id)
        def fechar_se_foco_externo():
            if not self.dropdown:
                self.fechar_lista()
                return
            foco = self.winfo_toplevel().focus_get()
            if foco is not self.entry and not str(foco).startswith(str(self.dropdown)):
                self.fechar_lista()

        self._close_after_id = self.after(100, fechar_se_foco_externo)
