import sys

print("=" * 80)
print("PYTHON:", sys.executable)
print("VERSÃO:", sys.version)
print("=" * 80)

import customtkinter as ctk
import os
from PIL import Image, ImageDraw, ImageFont

from views.painel import Painel
from views.agenda import Agenda
from views.relatorios import Relatorios
from views.cadastro import Cadastro
from views.configuracoes import Configuracoes
from views.gerenciamento import Gerenciamento
from views.permissao import MAPA_PERMISSOES, Permissoes
from controllers.gerenciamento_controller import GerenciamentoController
from controllers.consulta_controller import ConsultaController
from views.theme import COLORS, toggle_dark_mode, load_theme_preference, get_dark_mode, font, ASSETS_DIR, get_brand_logo_path


class App(ctk.CTkToplevel):
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
        
        # Atualizar cores dos botões do menu e seus ícones
        for name, btn in self.buttons.items():
            if name == self.current_frame_name:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="white",
                    hover_color=COLORS["primary_dark"],
                    image=getattr(btn, "_icon_active", None)
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["hover"],
                    image=getattr(btn, "_icon_inactive", None)
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
            "relatorios": Relatorios(self.container, self.clinica_id),
            "config": Configuracoes(self.container, self.tipo_usuario, self.clinica_id, self.usuario_id, self),
            "cadastro": Cadastro(self.container, self.clinica_id),
            "gerenciamento": Gerenciamento(self.container, self.clinica_id),
            "permissao": Permissoes(self.container, self.clinica_id, self.usuario_id, self.tipo_usuario),
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
            return perms
        except Exception as e:
            print(f"Erro ao carregar permissões: {e}")
            return {}

    def tem_permissao(self, tela):
        """Verifica se o usuário tem permissão para acessar uma tela"""
        if self.tipo_usuario == "clinica":
            # Usuários de clínica têm acesso a tudo
            return True
        
        mapa_abas = {
            "painel": "Painel",
            "agenda": "Agenda",
            "relatorios": "Financeiro",
            "config": "Configurações",
            "cadastro": "Cadastro",
            "gerenciamento": "Gerenciamento"
        }

        nome_permissao = mapa_abas.get(tela)
        codigo_real = MAPA_PERMISSOES.get(nome_permissao)
        return codigo_real in self.permissoes_usuario if codigo_real else False

    def __init__(
        self,
        parent=None,
        usuario_nome="Usuário",
        usuario_id=None,
        tipo_usuario=None,
        clinica_id=None,
        on_logout=None,
        on_initialization_complete=None,
        on_initialization_error=None
    ):
        self.clinica_id = clinica_id
        self.usuario_id = usuario_id
        self.tipo_usuario = tipo_usuario
        self.on_logout = on_logout
        self._on_initialization_complete = on_initialization_complete
        self._on_initialization_error = on_initialization_error
        self._initialization_error = None
        self._initialization_notified = False

        if self.clinica_id:
            try:
                print(f"[APP] Atualizando consultas pendentes como falta para clínica {self.clinica_id}")
                ConsultaController.marcar_consultas_pendentes_como_falta(self.clinica_id)
            except Exception as e:
                print(f"[APP] Falha ao atualizar faltas para clínica {self.clinica_id}: {e}")

        print("[SPLASH] App criado; cargas assíncronas não críticas não bloqueiam a prontidão")
        
        if parent is None:
            raise RuntimeError("App requer a raiz Tk existente como parent")
        super().__init__(master=parent)
        self.withdraw()

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

        self.title("OdontoHub - Sistema de Gerenciamento")
        largura = self.winfo_screenwidth()
        altura = self.winfo_screenheight()

        self.geometry(f"{largura}x{altura}+0+0")
        self.fullscreen = False
        self.bind("<F11>", self._toggle_fullscreen)
        self.bind("<Escape>", self._exit_fullscreen)
        self.minsize(1200, 650)
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
        brand_frame.pack(pady=(16, 8), padx=20, fill="x")

# Carrega a logo OdontoHub da sidebar usando apenas os arquivos corretos para cada tema
        self.brand_logo_img = None
        try:
            if get_dark_mode():
                brand_logo_path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf (1).png")
            else:
                brand_logo_path = os.path.join(ASSETS_DIR, "clinicas", "logo", "logo-odontohub (1).pdf.png")

            if os.path.exists(brand_logo_path):
                pil = Image.open(brand_logo_path)
                self._brand_logo_pil = pil
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
        self.brand_logo_label.image = self.brand_logo_img
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
                ("Painel", "painel"),
                ("Agenda", "agenda"),
                ("Relatórios", "relatorios"),
                ("Gerenciamento", "gerenciamento"),
                ("Permissões", "permissao"),
                ("Cadastro", "cadastro"),
                ("Configurações", "config"),
            ]
            # Filtrar apenas os que o gerente tem permissão
            self.menu_items = [item for item in todos_itens if self.tem_permissao(item[1])]
        else:  # clinica
            self.menu_items = [
                ("Painel", "painel"),
                ("Agenda", "agenda"),
                ("Relatórios", "relatorios"),
                ("Gerenciamento", "gerenciamento"),
                ("Permissões", "permissao"),
                ("Cadastro", "cadastro"),
                ("Configurações", "config"),
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
        self.container.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)

        self.frames = {
            "painel": Painel(self.container, self.clinica_id, self.usuario_id, self.tipo_usuario),
            "agenda": Agenda(self.container, self.clinica_id),
            "relatorios": Relatorios(
                self.container,
                self.clinica_id,
                on_initialization_complete=self._on_relatorios_initialized
            ),
            "config": Configuracoes(self.container, self.tipo_usuario, self.clinica_id, self.usuario_id, self),
            "cadastro": Cadastro(self.container, self.clinica_id),
            "gerenciamento": Gerenciamento(self.container, self.clinica_id),
            "permissao": Permissoes(self.container, self.clinica_id, self.usuario_id, self.tipo_usuario),
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

        config_error = getattr(self.frames["config"], "initialization_error", None)
        if config_error:
            self._report_initialization_error(config_error)
        else:
            print("[SPLASH] Telas principais criadas")
            self.after(0, self._check_initialization_complete)

    def _on_relatorios_initialized(self, error=None):
        if error:
            print(f"[AVISO APP] Relatórios continuarão carregando após a abertura: {error}")
            return
        print("[SPLASH] Relatórios concluídos em segundo plano")

    def _check_initialization_complete(self):
        if self._initialization_error or self._initialization_notified:
            return

        self._initialization_notified = True
        print("[SPLASH] App pronto; inicialização crítica concluída")
        if callable(self._on_initialization_complete):
            self._on_initialization_complete()

    def _report_initialization_error(self, error):
        if self._initialization_error:
            return
        self._initialization_error = error
        print(f"[ERRO APP] Falha crítica durante a inicialização: {error}")
        if callable(self._on_initialization_error):
            self._on_initialization_error(error)

    def _hex_to_rgba(self, color, alpha=255):
        if not color:
            return (255, 255, 255, alpha)
        color = color.lstrip("#")
        if len(color) == 3:
            color = "".join(ch * 2 for ch in color)
        try:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            a = int(color[6:8], 16) if len(color) >= 8 else alpha
            return (r, g, b, a)
        except Exception:
            return (255, 255, 255, alpha)

    def _create_menu_icon(self, glyph, color, size=20):
        try:
            font_path = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "segmdl2.ttf")
            if not os.path.exists(font_path):
                return None

            canvas_size = size + 8
            image = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(font_path, int(size * 1.3))
            bbox = draw.textbbox((0, 0), glyph, font=font)
            glyph_w = bbox[2] - bbox[0]
            glyph_h = bbox[3] - bbox[1]
            x = (canvas_size - glyph_w) / 2 - bbox[0]
            y = (canvas_size - glyph_h) / 2 - bbox[1] + 1
            draw.text((x, y), glyph, font=font, fill=self._hex_to_rgba(color))
            image = image.resize((size, size), Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
        except Exception:
            return None

    def _get_menu_icon(self, name, color):
        glyphs = {
            "painel": "\uE7F4",
            "agenda": "\uE787",
            "relatorios": "\uE9D2",
            "gerenciamento": "\uE716",
            "permissao": "\uEA18",
            "cadastro": "\uE8FA",
            "config": "\uE713",
        }
        return self._create_menu_icon(glyphs.get(name, "•"), color)

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
            compound="left",
            border_spacing=10,
            command=lambda: self.show_frame(name)
        )
        btn._icon_inactive = self._get_menu_icon(name, COLORS["text_secondary"])
        btn._icon_active = self._get_menu_icon(name, "white")
        btn.configure(image=btn._icon_inactive)
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

        pending_refresh = getattr(self, "_pending_frame_refresh_id", None)
        if pending_refresh is not None:
            try:
                self.after_cancel(pending_refresh)
            except Exception:
                pass

        frame = self.current_frame

        def refresh_frame():
            self._pending_frame_refresh_id = None
            if self.current_frame is not frame or self.current_frame_name != name:
                return

            if hasattr(frame, "refresh"):
                try:
                    frame.refresh()
                except Exception as e:
                    print(f"Erro ao atualizar frame {name}: {e}")
            elif hasattr(frame, "render"):
                try:
                    frame.render()
                except Exception as e:
                    print(f"Erro ao renderizar frame {name}: {e}")

        self._pending_frame_refresh_id = self.after_idle(refresh_frame)

    def update_active_button(self, active):
        for name, btn in self.buttons.items():
            if name == active:
                btn.configure(
                    fg_color=COLORS["primary"],
                    text_color="white",
                    hover_color=COLORS["primary_dark"],
                    image=getattr(btn, "_icon_active", None)
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["hover"],
                    image=getattr(btn, "_icon_inactive", None)
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
                self._brand_logo_pil = pil
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
