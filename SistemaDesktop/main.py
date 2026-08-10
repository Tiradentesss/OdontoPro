import customtkinter as ctk
from views.login import Login
from app import App
from views.splash import SplashScreen as Splash
from views.theme import load_theme_preference


class MainWindow:
    """Gerenciador central que controla Login e App"""
    
    def __init__(self):
        try:
            # Carregar preferência de tema
            load_theme_preference()
            
            self.root = ctk.CTk()
            self.root.withdraw()
            self.current_app = None
            self.app_instance = None
            # Iniciar sem auto-login; exigirá clique no botão 'ENTRAR'
            self.show_login(auto_login_enabled=False)
        except Exception as e:
            print(f"Erro na inicialização: {e}")
            import traceback
            traceback.print_exc()
    
    def show_login(self, auto_login_enabled=False):
        """Exibe a tela de login
        
        Args:
            auto_login_enabled: Se True, permite auto-login com credenciais salvas.
                              Se False (logout), apenas pré-preenche os campos.
        """
        try:
            # Se houver app aberto, destruir
            if self.current_app:
                try:
                    if self.current_app.winfo_exists():
                        self.current_app.destroy()
                except:
                    pass
            self.app_instance = None
            
            # Criar e exibir login com flag de auto-login
            self.current_app = Login(self.root, on_success=self.show_app, auto_login_enabled=auto_login_enabled)
            self.current_app.mainloop()
        except Exception as e:
            print(f"Erro ao exibir login: {e}")
            import traceback
            traceback.print_exc()
    
    def show_app(self, usuario_nome, usuario_id, tipo_usuario, clinica_id):
        """Exibe a tela do aplicativo após login bem-sucedido"""
        try:
            print(f"✅ Login bem-sucedido para: {usuario_nome}")
            parent = self.current_app
            splash = None

            def _on_splash_finish():
                try:
                    app = self.app_instance
                    if not app or not app._initialization_notified:
                        return

                    if splash and splash.winfo_exists():
                        splash.grab_release()
                        splash.destroy()
                        print("[SPLASH] Splash destruída")

                    if parent and parent.winfo_exists():
                        parent.destroy()
                        print("[SPLASH] Login destruído após App pronto")

                    self.current_app = app
                    app.deiconify()
                    print("[SPLASH] App exibido")
                    app.mainloop()
                except Exception as e:
                    print(f"Erro na finalização da Splash: {e}")

            def _on_app_ready():
                print("[SPLASH] App pronto recebido pela MainWindow")
                if splash and splash.winfo_exists():
                    splash.set_initialization_result(True)

            def _on_app_error(error):
                if splash and splash.winfo_exists():
                    splash.set_initialization_result(False, error)

            try:
                splash = Splash(parent, on_finish=_on_splash_finish, usuario_nome=usuario_nome, clinica_id=clinica_id)
                splash.transient(parent)
                splash.grab_set()
                splash.focus_force()
            except Exception as e:
                print(f"Erro ao exibir Splash: {e}")
                return

            try:
                self.app_instance = App(
                    parent=self.root,
                    usuario_nome=usuario_nome,
                    usuario_id=usuario_id,
                    tipo_usuario=tipo_usuario,
                    clinica_id=clinica_id,
                    on_logout=lambda: self.show_login(auto_login_enabled=False),
                    on_initialization_complete=_on_app_ready,
                    on_initialization_error=_on_app_error
                )
            except Exception as e:
                print(f"Erro ao preparar App: {e}")
                if splash and splash.winfo_exists():
                    splash.set_initialization_result(False, e)
        except Exception as e:
            print(f"Erro ao exibir app: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main = MainWindow()


