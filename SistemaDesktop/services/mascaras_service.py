"""
Serviço de máscaras de formatação para campos de entrada.
Fornece funções reutilizáveis para formatação de CPF, Data, Telefone.
"""


class MascarasService:
    """Serviço centralizado para aplicação de máscaras de formatação."""
    
    @staticmethod
    def formatar_cpf(valor):
        """
        Formata CPF no padrão: 000.000.000-00
        
        Args:
            valor (str): Valor a ser formatado
            
        Returns:
            tuple: (valor_formatado, posicao_cursor)
        """
        # Remove tudo que não é dígito
        apenas_numeros = ''.join(c for c in valor if c.isdigit())
        
        # Limita a 11 dígitos
        apenas_numeros = apenas_numeros[:11]
        
        # Aplica formatação
        if len(apenas_numeros) == 0:
            return '', 0
        elif len(apenas_numeros) <= 3:
            formatado = apenas_numeros
        elif len(apenas_numeros) <= 6:
            formatado = f"{apenas_numeros[:3]}.{apenas_numeros[3:]}"
        elif len(apenas_numeros) <= 9:
            formatado = f"{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:]}"
        else:
            formatado = f"{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:9]}-{apenas_numeros[9:]}"
        
        # Calcula posição do cursor
        cursor_pos = len(formatado)
        
        return formatado, cursor_pos
    
    @staticmethod
    def formatar_data(valor):
        """
        Formata data no padrão: DD/MM/AAAA
        
        Args:
            valor (str): Valor a ser formatado
            
        Returns:
            tuple: (valor_formatado, posicao_cursor)
        """
        # Remove tudo que não é dígito
        apenas_numeros = ''.join(c for c in valor if c.isdigit())
        
        # Limita a 8 dígitos
        apenas_numeros = apenas_numeros[:8]
        
        # Aplica formatação
        if len(apenas_numeros) == 0:
            return '', 0
        elif len(apenas_numeros) <= 2:
            formatado = apenas_numeros
        elif len(apenas_numeros) <= 4:
            formatado = f"{apenas_numeros[:2]}/{apenas_numeros[2:]}"
        else:
            formatado = f"{apenas_numeros[:2]}/{apenas_numeros[2:4]}/{apenas_numeros[4:]}"
        
        # Calcula posição do cursor
        cursor_pos = len(formatado)
        
        return formatado, cursor_pos
    
    @staticmethod
    def formatar_telefone(valor):
        """
        Formata telefone automaticamente.
        
        10 dígitos: (00) 0000-0000
        11 dígitos: (00) 00000-0000
        
        Args:
            valor (str): Valor a ser formatado
            
        Returns:
            tuple: (valor_formatado, posicao_cursor)
        """
        # Remove tudo que não é dígito
        apenas_numeros = ''.join(c for c in valor if c.isdigit())
        
        # Limita a 11 dígitos
        apenas_numeros = apenas_numeros[:11]
        
        # Aplica formatação
        if len(apenas_numeros) == 0:
            return '', 0
        elif len(apenas_numeros) <= 2:
            formatado = f"({apenas_numeros}"
        elif len(apenas_numeros) <= 6:
            formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:]}"
        elif len(apenas_numeros) <= 10:
            # Até 10 dígitos: telefone fixo (00) 0000-0000
            if len(apenas_numeros) == 10:
                formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
            else:
                # Entre 7 e 9 dígitos, sem hífen ainda
                formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:]}"
        else:
            # 11 dígitos: telefone celular (00) 00000-0000
            formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
        
        # Calcula posição do cursor
        cursor_pos = len(formatado)
        
        return formatado, cursor_pos
    
    @staticmethod
    def extrair_numeros(valor):
        """
        Remove formatação e retorna apenas números.
        
        Args:
            valor (str): Valor formatado
            
        Returns:
            str: Apenas os dígitos
        """
        return ''.join(c for c in valor if c.isdigit())
