"""
Teste visual/interativo das máscaras com CustomTkinter.
Abre uma janela simples para testar as máscaras em tempo real.
"""

import customtkinter as ctk
from SistemaDesktop.services.campos_mascarados import CampoMascarado, GerenciadorMascaras


class TesteVisualMascaras:
    """Interface gráfica para testar as máscaras de digitação."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🧪 Teste Visual de Máscaras")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Container principal
        main_frame = ctk.CTkFrame(root, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(
            main_frame,
            text="🧪 Teste Visual de Máscaras de Digitação",
            font=("Arial", 18, "bold"),
            text_color="#00BFFF"
        )
        titulo.pack(pady=(0, 20))
        
        # Descrição
        desc = ctk.CTkLabel(
            main_frame,
            text="Digite números para ver as máscaras sendo aplicadas em tempo real",
            font=("Arial", 12),
            text_color="#CCCCCC"
        )
        desc.pack(pady=(0, 20))
        
        # Gerenciador de máscaras
        self.mascaras = GerenciadorMascaras()
        
        # ===== CPF =====
        self._criar_secao(main_frame, "CPF (000.000.000-00)", "cpf_label", "cpf_entry", "cpf")
        
        # ===== DATA =====
        self._criar_secao(main_frame, "Data (DD/MM/AAAA)", "data_label", "data_entry", "data")
        
        # ===== TELEFONE =====
        self._criar_secao(main_frame, "Telefone (10 ou 11 dígitos)", "tel_label", "tel_entry", "telefone")
        
        # Botão de informações
        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=20)
        
        info_btn = ctk.CTkButton(
            info_frame,
            text="📋 Mostrar Valores",
            command=self._mostrar_valores,
            fg_color="#00BFFF",
            text_color="black",
            font=("Arial", 12, "bold")
        )
        info_btn.pack(side="left", padx=(0, 10))
        
        limpar_btn = ctk.CTkButton(
            info_frame,
            text="🗑️ Limpar Tudo",
            command=self._limpar_tudo,
            fg_color="#FF6B6B",
            text_color="white",
            font=("Arial", 12, "bold")
        )
        limpar_btn.pack(side="left")
        
        # Label de informações
        self.info_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=("Arial", 11),
            text_color="#FFD700",
            justify="left"
        )
        self.info_label.pack(fill="x", pady=10)
    
    def _criar_secao(self, parent, titulo, label_id, entry_id, tipo_mascara):
        """Cria uma seção com label, entry e status."""
        # Container
        container = ctk.CTkFrame(parent, fg_color="#2d2d2d", corner_radius=8)
        container.pack(fill="x", pady=10)
        
        # Título
        titulo_label = ctk.CTkLabel(
            container,
            text=titulo,
            font=("Arial", 12, "bold"),
            text_color="#00BFFF"
        )
        titulo_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Entry
        entry = ctk.CTkEntry(
            container,
            placeholder_text=f"Digite números...",
            height=40,
            font=("Arial", 13),
            fg_color="#1a1a1a",
            border_color="#00BFFF",
            border_width=1,
            text_color="#FFFFFF",
            placeholder_text_color="#666666"
        )
        entry.pack(fill="x", padx=15, pady=(0, 5))
        
        # Aplicar máscara
        self.mascaras.adicionar_campo(entry_id, entry, tipo_mascara)
        
        # Status/Info
        status_label = ctk.CTkLabel(
            container,
            text="",
            font=("Arial", 10),
            text_color="#999999"
        )
        status_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Bind para atualizar status
        def atualizar_status(event=None):
            campo = self.mascaras.obter_campo(entry_id)
            formatado = campo.obter_valor_formatado()
            numerico = campo.obter_valor_numerico()
            caracteres = len(formatado)
            numeros = len(numerico)
            
            status_text = f"📝 {caracteres} caracteres | 🔢 {numeros} números"
            if numerico:
                status_text += f" | Valor: {numerico}"
            
            status_label.configure(text=status_text)
        
        entry.bind("<KeyRelease>", atualizar_status)
    
    def _mostrar_valores(self):
        """Mostra todos os valores formatados e numéricos."""
        valores_formatados = self.mascaras.obter_valores()
        valores_numericos = self.mascaras.obter_valores_numericos()
        
        info_text = "📊 VALORES CAPTURADOS:\n\n"
        
        info_text += "✨ CPF:\n"
        info_text += f"  Formatado: {valores_formatados.get('cpf_entry', '')}\n"
        info_text += f"  Números: {valores_numericos.get('cpf_entry', '')}\n\n"
        
        info_text += "📅 DATA:\n"
        info_text += f"  Formatado: {valores_formatados.get('data_entry', '')}\n"
        info_text += f"  Números: {valores_numericos.get('data_entry', '')}\n\n"
        
        info_text += "📞 TELEFONE:\n"
        info_text += f"  Formatado: {valores_formatados.get('tel_entry', '')}\n"
        info_text += f"  Números: {valores_numericos.get('tel_entry', '')}\n"
        
        self.info_label.configure(text=info_text)
    
    def _limpar_tudo(self):
        """Limpa todos os campos."""
        self.mascaras.limpar_tudo()
        self.info_label.configure(text="")


def main():
    """Executa a aplicação de teste."""
    root = ctk.CTk()
    app = TesteVisualMascaras(root)
    root.mainloop()


if __name__ == "__main__":
    main()
