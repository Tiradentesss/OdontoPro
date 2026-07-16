"""
Classe auxiliar para aplicar máscaras a campos CTkEntry.
Gerencia a aplicação de máscaras mantendo o comportamento natural da entrada.
"""

from services.mascaras_service import MascarasService


class CampoMascarado:
    """
    Classe para aplicar máscaras a um CTkEntry mantendo a experiência do usuário.
    
    Exemplo:
        campo_cpf = CampoMascarado(entry_cpf, 'cpf')
        campo_telefone = CampoMascarado(entry_tel, 'telefone')
    """
    
    def __init__(self, entry, tipo_mascara):
        """
        Inicializa o campo mascarado.
        
        Args:
            entry: Widget CTkEntry do CustomTkinter
            tipo_mascara (str): 'cpf', 'data', ou 'telefone'
        """
        self.entry = entry
        self.tipo_mascara = tipo_mascara
        self.atualizando = False  # Flag para evitar loops infinitos
        
        # Mapeia tipos de máscaras para funções
        self.funcoes_mascara = {
            'cpf': MascarasService.formatar_cpf,
            'data': MascarasService.formatar_data,
            'telefone': MascarasService.formatar_telefone
        }
        
        if tipo_mascara not in self.funcoes_mascara:
            raise ValueError(f"Tipo de máscara inválido: {tipo_mascara}")
        
        # Vincula o evento de tecla liberada
        self.entry.bind("<KeyRelease>", self._ao_teclar)
    
    def _ao_teclar(self, event):
        """
        Callback para evento de tecla liberada.
        Aplica a máscara mantendo o cursor na posição correta.
        """
        if self.atualizando:
            return
        
        try:
            self.atualizando = True
            
            # Obtém o valor atual
            valor_atual = self.entry.get()
            
            # Aplica a formatação
            funcao = self.funcoes_mascara[self.tipo_mascara]
            valor_formatado, cursor_pos = funcao(valor_atual)
            
            # Atualiza o entry
            self.entry.delete(0, "end")
            self.entry.insert(0, valor_formatado)
            
            # Reposiciona o cursor
            self.entry.icursor(cursor_pos)
            
        except Exception as e:
            print(f"Erro ao aplicar máscara {self.tipo_mascara}: {e}")
        finally:
            self.atualizando = False
    
    def obter_valor_formatado(self):
        """Retorna o valor formatado do campo."""
        return self.entry.get()
    
    def obter_valor_numerico(self):
        """Retorna apenas os dígitos do campo."""
        valor = self.entry.get()
        return MascarasService.extrair_numeros(valor)
    
    def limpar(self):
        """Limpa o campo."""
        self.entry.delete(0, "end")


class GerenciadorMascaras:
    """
    Gerenciador centralizado de campos mascarados.
    Facilita a aplicação de máscaras a múltiplos campos.
    """
    
    def __init__(self):
        """Inicializa o gerenciador."""
        self.campos = {}
    
    def adicionar_campo(self, nome, entry, tipo_mascara):
        """
        Adiciona um novo campo mascarado ao gerenciador.
        
        Args:
            nome (str): Nome identificador do campo
            entry: Widget CTkEntry
            tipo_mascara (str): 'cpf', 'data', ou 'telefone'
        """
        self.campos[nome] = CampoMascarado(entry, tipo_mascara)
    
    def obter_campo(self, nome):
        """
        Retorna o campo mascarado pelo nome.
        
        Args:
            nome (str): Nome do campo
            
        Returns:
            CampoMascarado: Campo mascarado
        """
        return self.campos.get(nome)
    
    def obter_valores(self):
        """
        Retorna um dicionário com todos os valores dos campos.
        
        Returns:
            dict: {nome: valor_formatado}
        """
        return {nome: campo.obter_valor_formatado() 
                for nome, campo in self.campos.items()}
    
    def obter_valores_numericos(self):
        """
        Retorna um dicionário com valores numéricos (sem formatação).
        
        Returns:
            dict: {nome: apenas_numeros}
        """
        return {nome: campo.obter_valor_numerico() 
                for nome, campo in self.campos.items()}
    
    def obter_valor_numerico(self):
        """
        Compatibilidade com chamadas existentes.
        Retorna um dicionário com valores numéricos de todos os campos.
        """
        return self.obter_valores_numericos()

