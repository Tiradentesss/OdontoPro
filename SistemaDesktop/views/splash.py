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
                self.logo = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(120, 120)
                )
        except Exception:
            self.logo = None

        if self.logo:
            ctk.CTkLabel(
                frame,
                image=self.logo,
                text=""
            ).pack(pady=(45, 10))

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

        threading.Thread(
            target=self.load_system,
            daemon=True
        ).start()

    def update_progress(self, value, texto):
        self.after(0, lambda: self.progress.set(value))
        self.after(0, lambda: self.status.configure(text=texto))

    def load_system(self):
        self.update_progress(0.08, "Conectando ao banco...")
        try:
            conn = get_connection()
            conn.close()
        except Exception:
            pass

        self.update_progress(0.18, "Carregando permissões...")
        try:
            GerenciamentoController.inicializar_permissoes_padrao()
        except Exception:
            pass

        self.update_progress(0.30, f"Carregando usuário {self.usuario_nome}...")
        try:
            if self.usuario_nome:
                self.master.update_idletasks()
        except Exception:
            pass

        self.update_progress(0.45, "Carregando médicos...")
        try:
            ConsultaController.listar_medicos(self.clinica_id)
        except Exception:
            pass

        self.update_progress(0.60, "Carregando especialidades...")
        try:
            ConsultaController.listar_especialidades()
        except Exception:
            pass

        self.update_progress(0.70, "Carregando Agenda...")
        try:
            ConsultaController.listar_opcoes_filtro(self.clinica_id)
        except Exception:
            pass

        self.update_progress(0.80, "Carregando Financeiro...")
        try:
            from controllers.financeiro_controller import FinanceiroController
            FinanceiroController.obter_resumo_financeiro(self.clinica_id)
        except Exception:
            pass

        self.update_progress(0.88, "Carregando imagens...")
        try:
            if os.path.exists(self.caminho):
                with Image.open(self.caminho) as img:
                    img.load()
        except Exception:
            pass

        self.update_progress(0.94, "Inicializando componentes...")
        try:
            self.master.update_idletasks()
        except Exception:
            pass

        self.update_progress(1.0, "Preparando interface...")
        self.after(0, self.finish)

    def finish(self):
        # Chamar on_finish primeiro; se ocorrer erro, fechar splash e mostrar erro sem corromper imagens do login
        try:
            self.on_finish()
        except Exception as e:
            try:
                self.destroy()
            except Exception:
                pass
            try:
                import tkinter.messagebox as mb
                mb.showerror("Erro ao iniciar aplicação", f"Ocorreu um erro ao inicializar o aplicativo:\n{e}")
            except Exception:
                pass
            return

        # Se on_finish ocorreu sem exceções, então podemos fechar o splash
        try:
            self.destroy()
        except Exception:
            pass
