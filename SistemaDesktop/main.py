import customtkinter as ctk
from views.login import Login
from app import App
from views.theme import load_theme_preference


class MainWindow:
    """Gerenciador central que controla Login e App"""
    
    def __init__(self):
        try:
            # Carregar preferência de tema
            load_theme_preference()
            
            self.current_app = None
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
            
            # Criar e exibir login com flag de auto-login
            self.current_app = Login(on_success=self.show_app, auto_login_enabled=auto_login_enabled)
            self.current_app.mainloop()
        except Exception as e:
            print(f"Erro ao exibir login: {e}")
            import traceback
            traceback.print_exc()
    
    def show_app(self, usuario_nome, usuario_id, tipo_usuario, clinica_id):
        """Exibe a tela do aplicativo após login bem-sucedido"""
        try:
            print(f"✅ Login bem-sucedido para: {usuario_nome}")
            
            # Criar e exibir app
            # Passa lambda para não permitir auto-login ao voltar do logout
            self.current_app = App(
                usuario_nome=usuario_nome,
                usuario_id=usuario_id,
                tipo_usuario=tipo_usuario,
                clinica_id=clinica_id,
                on_logout=lambda: self.show_login(auto_login_enabled=False)
            )
            self.current_app.mainloop()
        except Exception as e:
            print(f"Erro ao exibir app: {e}")
            import traceback
            traceback.print_exc()
            # Tentar voltar para login
            self.show_login(auto_login_enabled=False)


if __name__ == "__main__":
    main = MainWindow()


