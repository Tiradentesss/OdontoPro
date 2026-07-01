import customtkinter as ctk
import os
from PIL import Image

from views.painel import Painel
from views.agenda import Agenda
from views.financeiro import Financeiro
from views.cadastro import Cadastro
from views.configuracoes import Configuracoes
from views.gerenciamento import Gerenciamento
from views.permissao import Permissoes
from controllers.gerenciamento_controller import GerenciamentoController
from views.theme import COLORS, toggle_dark_mode, load_theme_preference, get_dark_mode, font, ASSETS_DIR, get_brand_logo_path


class App(ctk.CTk):
    def logout(self):
        """Faz logout e volta para a tela de login"""
        # Se houver um callback de logout, usar ele
        if hasattr(self, 'on_logout') and self.on_logout:
            # Limpar todos os frames
            for frame in self.frames.values():
                frame.pack_forget()
                frame.destroy()
            
            # Chamar o callback
            self.on_logout()
        else:
            # Fallback: fechar normalmente
            self.destroy()

    def toggle_theme(self):
        """Alterna tema e recria TODOS os frames com as novas cores"""
        # Atualizar tema global
        toggle_dark_mode()
        
        # Atualizar cores da aplicação
        self.configure(fg_color=COLORS["bg"])
        self.sidebar.configure(fg_color=COLORS["card"], border_color=COLORS["border"])
        
        
        # Atualizar botão de Sair com cores do tema
        self.logout_button.configure(
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger"],
            border_color=COLORS["danger"]
        )
        
        # Atualizar cores dos botões do menu
        for name, btn in self.buttons.items():
            if name == self.current_frame_name:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="white",
                    hover_color=COLORS["primary_dark"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["hover"]
                )
        
        # Guardar o nome do frame atual antes de destruir
        current_frame_name = self.current_frame_name
        
        # Destruir todos os frames antigos
        for frame in self.frames.values():
            frame.pack_forget()
            frame.destroy()
        
        # Recriar TODOS os frames com as novas cores
        self.frames = {
            "painel": Painel(self.container, self.clinica_id, self.usuario_id, self.tipo_usuario),
            "agenda": Agenda(self.container, self.clinica_id),
            "financeiro": Financeiro(self.container, self.clinica_id),
            "config": Configuracoes(self.container, self.tipo_usuario, self.clinica_id, self.usuario_id, self),
            "cadastro": Cadastro(self.container, self.clinica_id),
            "gerenciamento": Gerenciamento(self.container, self.clinica_id),
            "permissao": Permissoes(self.container, self.clinica_id),
        }
        
        # Mostrar o frame que estava ativo
        if current_frame_name in self.frames:
            self.show_frame(current_frame_name)
            self.current_frame.pack(expand=True, fill="both")
        # Atualizar a logo imediatamente após a mudança de tema
        try:
            self.update_logo()
        except Exception:
            pass


    def _toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def _exit_fullscreen(self, event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.attributes("-fullscreen", False)

    def _carregar_permissoes_usuario(self):
        """Carrega as permissões do gerente logado"""
        try:
            perms_bd = GerenciamentoController.obter_permissoes_gerente(self.usuario_id)
            perms = {p['codigo']: True for p in perms_bd}
            
            # Se gerente não tem permissões no BD, dar todas as permissões padrão
            if not perms:
                print(f"[PERMISSÕES] Gerente {self.usuario_id} sem permissões no BD. Concedendo todas...")
                permissoes_padrao = ["Painel", "Agenda", "Financeiro", "Configurações", "Cadastro", "Gerenciamento", "Permissões"]
                return {p: True for p in permissoes_padrao}
            
            return perms
        except Exception as e:
            print(f"Erro ao carregar permissões: {e}")
            return {}

    def tem_permissao(self, tela):
        """Verifica se o usuário tem permissão para acessar uma tela"""
        if self.tipo_usuario == "clinica":
            # Usuários de clínica têm acesso a tudo
            return True
        
        # Para gerentes, verificar a permissão
        # Mapear nome da tela para nome da permissão no BD
        mapa_permissoes = {
            "painel": "Painel",
            "agenda": "Agenda",
            "financeiro": "Financeiro",
            "config": "Configurações",
            "cadastro": "Cadastro",
            "permissao": "Permissões",
            "gerenciamento": "Gerenciamento"
        }
        
        perm_necessaria = mapa_permissoes.get(tela)
        return perm_necessaria in self.permissoes_usuario if perm_necessaria else False

    def __init__(self, usuario_nome="Usuário", usuario_id=None, tipo_usuario=None, clinica_id=None, on_logout=None):
        self.clinica_id = clinica_id
        self.usuario_id = usuario_id
        self.tipo_usuario = tipo_usuario
        self.on_logout = on_logout
        
        super().__init__()

        # Carregar preferência de tema
        load_theme_preference()

        self.usuario_nome = usuario_nome
        
        # Inicializar permissões padrão no BD (se não existirem)
        resultado_perms = GerenciamentoController.inicializar_permissoes_padrao()
        if not resultado_perms.get("sucesso"):
            print(f"[AVISO APP] Falha ao inicializar permissões: {resultado_perms.get('mensagem')}")
        
        # Carregar permissões do gerente se for tipo "gerenciamento"
        self.permissoes_usuario = {}
        if tipo_usuario == "gerenciamento" and usuario_id:
            self.permissoes_usuario = self._carregar_permissoes_usuario()

        self.title("OdontoPro - Sistema de Gerenciamento")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()

        self.geometry(f"{largura}x{altura}+0+0")
        self.fullscreen = False
        self.bind("<F11>", self._toggle_fullscreen)
        self.bind("<Escape>", self._exit_fullscreen)
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS["bg"])

        # Grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= Sidebar =================
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"]
        )
        
        # Modo CTk - usar grid
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Header: centered logo
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=(16, 8), padx=8, fill="x")

# Carrega a logo OdontoHub da sidebar usando apenas os arquivos corretos para cada tema
        self.brand_logo_img = None
        try:
            if get_dark_mode():
                brand_logo_path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf (1).png")
            else:
                brand_logo_path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf.png")

            if os.path.exists(brand_logo_path):
                pil = Image.open(brand_logo_path)
                prop = pil.width / pil.height if pil.height else 1
                w = 200
                h = int(w / prop)
                self.brand_logo_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(w, h))
        except Exception:
            self.brand_logo_img = None

        # Criar widget da logo e manter referência para atualizações dinâmicas
        self.brand_logo_label = ctk.CTkLabel(
            brand_frame,
            text="",
            image=self.brand_logo_img
        )
        self.brand_logo_label.pack(pady=12, padx=8, anchor="center")
        # subtítulo (pode existir quando não há imagem)
        self.brand_subtitle_label = None
        if not self.brand_logo_img:
            # exibir texto como fallback quando não há imagem
            self.brand_logo_label.configure(text="OdontoHub", font=font("large_title", "bold"), text_color=COLORS["primary"], image=None)
            self.brand_subtitle_label = ctk.CTkLabel(
                brand_frame,
                text="Clinical Management",
                font=font("small"),
                text_color=COLORS["text_secondary"]
            )
            self.brand_subtitle_label.pack(pady=(0, 16), anchor="center")

        # Menu
        self.buttons = {}
        if self.tipo_usuario == "gerenciamento":
            # Para gerentes, mostrar todos os itens possíveis
            todos_itens = [
                ("📊  Painel", "painel"),
                ("📅  Agenda", "agenda"),
                ("💳  Financeiro", "financeiro"),
                ("🏢  Gerenciamento", "gerenciamento"),
                ("🔐  Permissões", "permissao"),
                ("👥  Cadastro", "cadastro"),
                ("⚙️  Configurações", "config"),
            ]
            # Filtrar apenas os que o gerente tem permissão
            self.menu_items = [item for item in todos_itens if self.tem_permissao(item[1])]
        else:  # clinica
            self.menu_items = [
                ("📊  Painel", "painel"),
                ("📅  Agenda", "agenda"),
                ("💳  Financeiro", "financeiro"),
                ("🏢  Gerenciamento", "gerenciamento"),
                ("🔐  Permissões", "permissao"),
                ("👥  Cadastro", "cadastro"),
                ("⚙️  Configurações", "config"),
            ]

        for text, name in self.menu_items:
            self.buttons[name] = self.create_menu_button(text, name)

        # Frame para os botões inferiores com melhor espaçamento
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=12, pady=20)

        # Cores para o botão de Sair (responsivo ao tema)
        logout_color = "#DC2626" if not get_dark_mode() else "#EF4444"
        logout_hover = "#991B1B" if not get_dark_mode() else "#7F1D1D"
        logout_border = "#7F1D1D" if not get_dark_mode() else "#DC2626"

        # Botão de Sair do Sistema
        self.logout_button = ctk.CTkButton(
            bottom_frame,
            text="⎋  Sair do Sistema",
            fg_color=logout_color,
            text_color="white",
            hover_color=logout_hover,
            font=font("button", "bold"),
            height=40,
            border_width=2,
            border_color=logout_border,
            corner_radius=8,
            command=self.logout
        )
        self.logout_button.pack(fill="x")

        # ================= Área Principal =================
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)

        self.frames = {
            "painel": Painel(self.container, self.clinica_id, self.usuario_id, self.tipo_usuario),
            "agenda": Agenda(self.container, self.clinica_id),
            "financeiro": Financeiro(self.container, self.clinica_id),
            "config": Configuracoes(self.container, self.tipo_usuario, self.clinica_id, self.usuario_id, self),
            "cadastro": Cadastro(self.container, self.clinica_id),
            "gerenciamento": Gerenciamento(self.container, self.clinica_id),
            "permissao": Permissoes(self.container, self.clinica_id),
        }

        # ================= Configuração de Padding/Espaçamento da Agenda =================
        # Ajustar espaçamento INDIVIDUAL de cada coluna (esquerda, direita)
        # Os números representam pixels de espaço dentro de cada célula
        self.frames["agenda"].set_column_padding('nome', padx_left=2, padx_right=2)
        self.frames["agenda"].set_column_padding('especialidade', padx_left=2, padx_right=2)
        self.frames["agenda"].set_column_padding('medico', padx_left=2, padx_right=2)
        self.frames["agenda"].set_column_padding('data', padx_left=2, padx_right=2)
        self.frames["agenda"].set_column_padding('hora', padx_left=2, padx_right=2)

        self.current_frame = None
        self.current_frame_name = None
        self.show_frame("painel")

    def create_menu_button(self, text, name):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            anchor="w",
            fg_color="transparent",
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["hover"],
            height=52,
            corner_radius=10,
            font=font("subtitle", "bold"),
            command=lambda: self.show_frame(name)
        )
        btn.pack(fill="x", padx=12, pady=8)
        return btn

    def show_frame(self, name):
        # Verificar se o usuário tem permissão para acessar esta tela
        if not self.tem_permissao(name):
            from tkinter import messagebox
            messagebox.showerror("Acesso Negado", f"Você não tem permissão para acessar esta tela: {name}")
            return
        
        if self.current_frame:
            self.current_frame.pack_forget()

        self.current_frame = self.frames[name]
        self.current_frame_name = name
        self.current_frame.pack(expand=True, fill="both")
        self.update_active_button(name)

    def update_active_button(self, active):
        for name, btn in self.buttons.items():
            if name == active:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="white",
                    hover_color=COLORS["primary_dark"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["hover"]
                )

    def update_logo(self):
        """Atualiza a logo do sidebar de acordo com o tema atual, sem recriar widgets."""
        try:
            # Usar apenas os arquivos de logo corretos para cada tema
            if get_dark_mode():
                path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf (1).png")
            else:
                path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf.png")

            new_img = None
            if os.path.exists(path):
                pil = Image.open(path)
                prop = pil.width / pil.height if pil.height else 1
                w = 200
                h = int(w / prop)
                new_img = ctk.CTkImage(light_image=pil, dark_image=pil, size=(w, h))

            # Guardar referência e aplicar no widget existente
            self.brand_logo_img = new_img
            if hasattr(self, 'brand_logo_label'):
                if new_img:
                    # remover subtítulo se existir
                    if getattr(self, 'brand_subtitle_label', None):
                        try:
                            self.brand_subtitle_label.pack_forget()
                        except Exception:
                            pass
                        self.brand_subtitle_label = None
                    self.brand_logo_label.configure(image=new_img, text="")
                    # manter referência para GC
                    self.brand_logo_label.image = new_img
                else:
                    # exibir fallback textual
                    self.brand_logo_label.configure(image=None, text="OdontoHub", font=font("large_title", "bold"), text_color=COLORS["primary"])
                    if not getattr(self, 'brand_subtitle_label', None):
                        parent = self.brand_logo_label.master
                        self.brand_subtitle_label = ctk.CTkLabel(parent, text="Clinical Management", font=font("small"), text_color=COLORS["text_secondary"])
                        self.brand_subtitle_label.pack(pady=(0, 16), anchor="center")
        except Exception as e:
            print(f"Erro ao atualizar logo: {e}")

    pass

if __name__ == "__main__":
    from main import MainWindow
    MainWindow()
