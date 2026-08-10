import customtkinter as ctk
from PIL import Image
import threading
import os

from config.database import get_connection
from controllers.consulta_controller import ConsultaController
from controllers.gerenciamento_controller import GerenciamentoController
from views.theme import COLORS, font


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

        self.configure(fg_color=COLORS["bg"])

        self.attributes("-topmost", True)

        frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=25
        )
        frame.pack(fill="both", expand=True, padx=8, pady=8)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(7, weight=1)

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
            lbl.grid(row=1, column=0, pady=(0, 8))

        ctk.CTkLabel(
            frame,
            text="OdontoHub",
            font=font(28, weight="bold"),
            text_color=COLORS["primary"]
        ).grid(row=2, column=0)

        ctk.CTkLabel(
            frame,
            text="Sistema Inteligente para Clínicas",
            font=font("small"),
            text_color=COLORS["muted"]
        ).grid(row=3, column=0, pady=(4, 24))

        self.status = ctk.CTkLabel(
            frame,
            text="Inicializando...",
            font=font("text_large"),
            text_color=COLORS["text_secondary"]
        )

        self.status.grid(row=4, column=0, pady=(0, 7))

        self.percent = ctk.CTkLabel(
            frame,
            text="0%",
            font=font("small", weight="bold"),
            text_color=COLORS["primary_dark"]
        )
        self.percent.grid(row=5, column=0, pady=(0, 8))

        self.progress = ctk.CTkProgressBar(
            frame,
            width=420,
            height=7,
            corner_radius=4,
            fg_color=COLORS["primary_soft"],
            progress_color=COLORS["primary"]
        )

        self.progress.grid(row=6, column=0, pady=(0, 8))

        self._target_progress = 0.0
        self._display_progress = 0.0
        self._progress_animation_id = None
        self._finish_pending = False
        self.progress.set(0)

        # Estado de controle da inicialização
        self._loading = True
        self._error = None
        self._splash_tasks_complete = False
        self._app_ready = False
        self._after_ids = set()
        print("[SPLASH] Inicialização iniciada")

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
                self._target_progress = max(0.0, min(1.0, value))
                self.status.configure(text=texto)
                self._start_progress_animation()
            except Exception:
                pass

        self._schedule_after(0, _do)

    def _start_progress_animation(self):
        if self._progress_animation_id is None and self.winfo_exists():
            self._progress_animation_id = self._schedule_after(35, self._animate_progress)

    def _animate_progress(self):
        self._progress_animation_id = None
        if not self.winfo_exists():
            return

        if self._display_progress < self._target_progress:
            self._display_progress = min(
                self._display_progress + 0.02,
                self._target_progress
            )
            self.progress.set(self._display_progress)
            self.percent.configure(text=f"{round(self._display_progress * 100)}%")
            self._start_progress_animation()
            return

        if self._finish_pending and self._display_progress >= 1.0:
            self._finish_pending = False
            self._schedule_after(300, self.finish)

    def _schedule_after(self, delay, callback):
        if not self.winfo_exists():
            return

        callback_id = None

        def _guarded_callback():
            if callback_id is not None:
                self._after_ids.discard(callback_id)
            if self.winfo_exists():
                callback()

        try:
            callback_id = self.after(delay, _guarded_callback)
            self._after_ids.add(callback_id)
            return callback_id
        except Exception:
            return None

    def load_system(self):
        # A criação do App é a única etapa de inicialização; as telas carregam
        # seus próprios dados sem bloquear a abertura da janela principal.
        self.update_progress(0.0, "Inicializando...")
        self._splash_tasks_complete = True
        print("[SPLASH] Tarefas próprias da Splash concluídas")
        self._try_finish()

    def set_initialization_result(self, success, error=None):
        """Recebe a confirmação do App antes de liberar o fluxo de login."""
        if not self.winfo_exists():
            return

        if not success:
            self._error = error or RuntimeError("Falha durante a inicialização do App")
            self._loading = True
            self.update_progress(0.0, "Erro durante a inicialização. Aguarde ou verifique os detalhes.")
            print(f"[SPLASH ERROR] Inicialização do App falhou: {self._error}")
            return

        self._app_ready = True
        self.update_progress(1.0, "Sistema pronto")
        self._try_finish()

    def _try_finish(self):
        if not self.winfo_exists() or self._error:
            return
        if not (self._splash_tasks_complete and self._app_ready):
            print(
                f"[SPLASH] Aguardando conclusão: splash={self._splash_tasks_complete}, "
                f"app={self._app_ready}"
            )
            return

        self._loading = False
        print("[SPLASH] Finalizando Splash")
        self._finish_pending = True
        self._start_progress_animation()

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

    def destroy(self):
        for callback_id in tuple(self._after_ids):
            try:
                self.after_cancel(callback_id)
            except Exception:
                pass
        self._after_ids.clear()
        super().destroy()
