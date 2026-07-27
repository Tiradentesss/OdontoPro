import customtkinter as ctk
from PIL import Image
import threading
import os

from config.database import get_connection
from controllers.consulta_controller import ConsultaController
from controllers.gerenciamento_controller import GerenciamentoController


class SplashScreen(ctk.CTkToplevel):

    def __init__(self, parent, on_finish, usuario_nome=None, clinica_id=None):
        super().__init__(parent)

        self.on_finish = on_finish
        self.usuario_nome = usuario_nome or "usuário"
        self.clinica_id = clinica_id or 1

        self.overrideredirect(True)

        largura = 700
        altura = 430

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        x = int((screen_w - largura) / 2)
        y = int((screen_h - altura) / 2)

        self.geometry(f"{largura}x{altura}+{x}+{y}")

        self.configure(fg_color="#FFFFFF")

        self.attributes("-topmost", True)

        frame = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=25
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.caminho = os.path.join(
            os.path.dirname(__file__),
            "..",
            "assets",
            "clinicas",
            "logo",
            "logo_dente.png"
        )

        self.logo = None
        try:
            if os.path.exists(self.caminho):
                img = Image.open(self.caminho)
                # Manter referência PIL para evitar que a imagem seja finalizada
                self._logo_pil = img
                self.logo = ctk.CTkImage(
                    light_image=self._logo_pil,
                    dark_image=self._logo_pil,
                    size=(120, 120)
                )
        except Exception:
            self.logo = None

        if self.logo:
            lbl = ctk.CTkLabel(
                frame,
                image=self.logo,
                text=""
            )
            # manter referência no widget também
            lbl.image = self.logo
            lbl.pack(pady=(45, 10))

        ctk.CTkLabel(
            frame,
            text="OdontoHub",
            font=("Segoe UI", 30, "bold"),
            text_color="#007AFF"
        ).pack()

        ctk.CTkLabel(
            frame,
            text="Sistema Inteligente para Clínicas",
            font=("Segoe UI", 15),
            text_color="#666666"
        ).pack(pady=(5, 30))

        self.status = ctk.CTkLabel(
            frame,
            text="Inicializando...",
            font=("Segoe UI", 14),
            text_color="#777777"
        )

        self.status.pack()

        self.progress = ctk.CTkProgressBar(
            frame,
            width=420,
            height=8,
            progress_color="#007AFF"
        )

        self.progress.pack(pady=25)

        self.progress.set(0)

        # Estado de controle da inicialização
        self._loading = True
        self._error = None

        # Impedir fechamento da janela enquanto estiver carregando
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        # Iniciar thread de inicialização
        threading.Thread(
            target=self.load_system,
            daemon=True
        ).start()

    def update_progress(self, value, texto):
        # Sempre agendar atualizações na main thread e checar se o widget existe
        def _do():
            try:
                if not self.winfo_exists():
                    return
                self.progress.set(value)
                self.status.configure(text=texto)
            except Exception:
                pass

        try:
            self.after(0, _do)
        except Exception:
            pass

    def load_system(self):
        self.update_progress(0.08, "Conectando ao banco...")
        try:
            conn = get_connection()
            conn.close()
        except Exception as e:
            self._error = e
            print(f"[SPLASH ERROR] Falha ao conectar ao banco: {e}")
            self.update_progress(0.0, "Erro ao conectar ao banco")
            # Não continuar se houver erro crítico
            return

        self.update_progress(0.18, "Carregando permissões...")
        try:
            GerenciamentoController.inicializar_permissoes_padrao()
        except Exception as e:
            self._error = e
            print(f"[SPLASH ERROR] Falha ao inicializar permissões: {e}")
            self.update_progress(0.0, "Erro ao carregar permissões")
            return

        self.update_progress(0.30, f"Carregando usuário {self.usuario_nome}...")
        try:
            if self.usuario_nome:
                self.master.update_idletasks()
        except Exception:
            pass

        self.update_progress(0.45, "Carregando médicos...")
        try:
            ConsultaController.listar_medicos(self.clinica_id)
        except Exception as e:
            # não interromper totalmente por falha em dados não-críticos, apenas logar
            print(f"[SPLASH WARNING] Falha ao carregar médicos: {e}")

        self.update_progress(0.60, "Carregando especialidades...")
        try:
            ConsultaController.listar_especialidades()
        except Exception as e:
            print(f"[SPLASH WARNING] Falha ao carregar especialidades: {e}")

        self.update_progress(0.70, "Carregando Agenda...")
        try:
            ConsultaController.listar_opcoes_filtro(self.clinica_id)
        except Exception as e:
            print(f"[SPLASH WARNING] Falha ao carregar opções da agenda: {e}")

        self.update_progress(0.80, "Carregando Relatórios...")
        try:
            from controllers.relatorios_controller import RelatoriosController
            RelatoriosController.obter_resumo_relatorios(self.clinica_id)
        except Exception as e:
            print(f"[SPLASH WARNING] Falha ao carregar relatórios: {e}")

        self.update_progress(0.88, "Carregando imagens...")
        try:
            if os.path.exists(self.caminho):
                with Image.open(self.caminho) as img:
                    img.load()
        except Exception as e:
            print(f"[SPLASH WARNING] Falha ao carregar imagens: {e}")

        self.update_progress(0.94, "Inicializando componentes...")
        try:
            self.master.update_idletasks()
        except Exception as e:
            print(f"[SPLASH WARNING] Falha em update_idletasks: {e}")
        # Finalizar carregamento
        # (A Splash realiza todas as inicializações necessárias aqui)

        # Finalizar carregamento
        self.update_progress(1.0, "Preparando interface...")
        self._loading = False

        # Chamar finish (on_finish) na UI thread
        try:
            self.after(50, self.finish)
        except Exception:
            self.finish()

    def finish(self):
        # Se ocorreu erro durante a inicialização, não permitir fechamento da splash
        if self._error:
            try:
                print(f"[SPLASH ERROR] Inicialização falhou: {self._error}")
                self.update_progress(0.0, "Erro na inicialização. Verifique o console.")
            except Exception:
                pass
            return

        # Disparar o callback de finalização (o caller é responsável por criar o App e destruir as janelas)
        try:
            if callable(self.on_finish):
                self.on_finish()
        except Exception as e:
            try:
                print(f"[SPLASH ERROR] Erro em on_finish: {e}")
                self.update_progress(0.0, "Erro ao finalizar inicialização. Verifique o console.")
            except Exception:
                pass
            return

    def _on_close(self):
        # Não permitir fechar enquanto estiver carregando
        if getattr(self, '_loading', False):
            try:
                self.update_progress(self.progress.get(), "Inicialização em andamento — aguarde...")
            except Exception:
                pass
            return
        try:
            if self.winfo_exists():
                self.destroy()
        except Exception:
            pass
