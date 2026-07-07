"""
Serviço de formatação e busca de endereço com integração ViaCEP.
Fornece funções reutilizáveis para formatação de CEP, UF, Cidade e busca automática.
"""

import json
import threading
import urllib.error
import urllib.request
from typing import Optional, Dict, Callable


class EnderecoService:
    """Serviço centralizado para operações de endereço e CEP."""
    
    # URL da API ViaCEP (sem HTTPS para compatibilidade)
    VIACEP_URL = "https://viacep.com.br/ws/{cep}/json/"
    
    @staticmethod
    def formatar_cep(valor):
        """
        Formata CEP no padrão: 00000-000
        
        Args:
            valor (str): Valor a ser formatado
            
        Returns:
            tuple: (valor_formatado, posicao_cursor)
        """
        # Remove tudo que não é dígito
        apenas_numeros = ''.join(c for c in valor if c.isdigit())
        
        # Limita a exatamente 8 dígitos
        apenas_numeros = apenas_numeros[:8]
        
        # Aplica formatação
        if len(apenas_numeros) == 0:
            return '', 0
        elif len(apenas_numeros) <= 5:
            formatado = apenas_numeros
        else:
            formatado = f"{apenas_numeros[:5]}-{apenas_numeros[5:]}"
        
        # Calcula posição do cursor
        cursor_pos = len(formatado)
        
        return formatado, cursor_pos
    
    @staticmethod
    def formatar_uf(valor):
        """
        Formata UF (Estado): máximo 2 letras, tudo maiúsculo
        
        Args:
            valor (str): Valor a ser formatado
            
        Returns:
            tuple: (valor_formatado, posicao_cursor)
        """
        # Remove números e caracteres especiais, mantém apenas letras
        apenas_letras = ''.join(c for c in valor if c.isalpha())
        
        # Limita a 2 caracteres
        apenas_letras = apenas_letras[:2]
        
        # Converte para maiúsculo
        formatado = apenas_letras.upper()
        
        # Calcula posição do cursor
        cursor_pos = len(formatado)
        
        return formatado, cursor_pos
    
    @staticmethod
    def formatar_cidade(valor):
        """
        Formata Cidade: apenas letras, espaços e acentos. Converte para Title Case
        
        Args:
            valor (str): Valor a ser formatado
            
        Returns:
            tuple: (valor_formatado, posicao_cursor)
        """
        # Remove caracteres inválidos (apenas letras, espaços e acentos)
        # Permite caracteres acentuados e espaços
        formatado = ''
        for c in valor:
            if c.isalpha() or c == ' ' or c in 'áàâãéèêíïóôõöúùûüçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÙÛÜÇÑ':
                formatado += c
        
        # Converter para um formato de nome próprio mais natural para cidades
        formatado = EnderecoService._to_title_case_cidade(formatado)
        
        # Calcula posição do cursor
        cursor_pos = len(formatado)
        
        return formatado, cursor_pos
    
    @staticmethod
    def _to_title_case_cidade(texto):
        """
        Converte texto para um formato de nome próprio mais natural para cidades.
        Capitaliza palavras principais, preserva palavras pequenas como 'de', 'da', 'dos'.
        """
        if not texto:
            return texto

        palavras = texto.split(' ')
        resultado = []
        palavras_pequenas = {"de", "da", "do", "dos", "das", "e", "del", "di", "la", "le", "les"}

        for index, palavra in enumerate(palavras):
            if not palavra:
                resultado.append(palavra)
                continue

            if index == 0 or index == len(palavras) - 1 or palavra.lower() not in palavras_pequenas:
                if palavra.lower() in {"sao", "são"}:
                    formatada = "São"
                else:
                    formatada = palavra[0].upper() + palavra[1:].lower()
            else:
                formatada = palavra.lower()

            resultado.append(formatada)

        return ' '.join(resultado)
    
    @staticmethod
    def extrair_cep_numeros(valor):
        """
        Remove formatação e retorna apenas os 8 dígitos do CEP
        
        Args:
            valor (str): CEP formatado ou não
            
        Returns:
            str: 8 dígitos do CEP, ou vazio se inválido
        """
        apenas_numeros = ''.join(c for c in valor if c.isdigit())
        return apenas_numeros if len(apenas_numeros) == 8 else ''
    
    @staticmethod
    def buscar_cep_async(cep, callback: Callable[[Optional[Dict]], None], 
                        erro_callback: Callable[[str], None] = None):
        """
        Busca informações de CEP via ViaCEP de forma assíncrona
        Não bloqueia a interface
        
        Args:
            cep (str): CEP (com ou sem máscara)
            callback: Função chamada com os dados encontrados: callback(dict) ou callback(None)
            erro_callback: Função chamada se houver erro: erro_callback(mensagem_erro)
        """
        # Remove formatação
        cep_limpo = EnderecoService.extrair_cep_numeros(cep)
        
        if not cep_limpo or len(cep_limpo) != 8:
            if erro_callback:
                erro_callback("CEP inválido (deve ter 8 dígitos)")
            else:
                callback(None)
            return
        
        # Executar em thread separada para não bloquear UI
        def fazer_requisicao():
            try:
                url = EnderecoService.VIACEP_URL.format(cep=cep_limpo)
                req = urllib.request.Request(url, headers={"User-Agent": "OdontoPro/1.0"})

                with urllib.request.urlopen(req, timeout=5) as response:
                    dados = json.loads(response.read().decode("utf-8"))

                # Verificar se é um CEP válido
                if 'erro' in dados:
                    if erro_callback:
                        erro_callback("CEP não encontrado")
                    else:
                        callback(None)
                else:
                    # Transformar os dados para o formato esperado
                    endereco = {
                        'cep': dados.get('cep', cep),
                        'rua': dados.get('logradouro', ''),
                        'bairro': dados.get('bairro', ''),
                        'cidade': dados.get('localidade', ''),
                        'estado': dados.get('uf', ''),
                        'complemento': dados.get('complemento', '')
                    }
                    callback(endereco)

            except urllib.error.URLError as exc:
                if erro_callback:
                    erro_callback("Erro de conexão (verifique sua internet)")
                else:
                    callback(None)

            except urllib.error.HTTPError as exc:
                if erro_callback:
                    erro_callback("CEP não encontrado")
                else:
                    callback(None)

            except Exception as e:
                if erro_callback:
                    erro_callback(f"Erro ao buscar CEP: {str(e)}")
                else:
                    callback(None)
        
        # Iniciar thread
        thread = threading.Thread(target=fazer_requisicao, daemon=True)
        thread.start()
    
    @staticmethod
    def buscar_cep_sync(cep) -> Optional[Dict]:
        """
        Busca informações de CEP via ViaCEP de forma síncrona (bloqueante)
        
        Args:
            cep (str): CEP (com ou sem máscara)
            
        Returns:
            dict: Dados do endereço ou None se não encontrado
        """
        # Remove formatação
        cep_limpo = EnderecoService.extrair_cep_numeros(cep)
        
        if not cep_limpo or len(cep_limpo) != 8:
            return None
        
        try:
            url = EnderecoService.VIACEP_URL.format(cep=cep_limpo)
            req = urllib.request.Request(url, headers={"User-Agent": "OdontoPro/1.0"})

            with urllib.request.urlopen(req, timeout=5) as response:
                dados = json.loads(response.read().decode("utf-8"))

            # Verificar se é um CEP válido
            if 'erro' in dados:
                return None

            # Transformar os dados
            return {
                'cep': dados.get('cep', cep),
                'rua': dados.get('logradouro', ''),
                'bairro': dados.get('bairro', ''),
                'cidade': dados.get('localidade', ''),
                'estado': dados.get('uf', ''),
                'complemento': dados.get('complemento', '')
            }

        except Exception as e:
            print(f"Erro ao buscar CEP: {str(e)}")
            return None


def formatar_cep(valor):
    return EnderecoService.formatar_cep(valor)


def formatar_uf(valor):
    return EnderecoService.formatar_uf(valor)


def formatar_cidade(valor):
    return EnderecoService.formatar_cidade(valor)


def buscar_cep(cep):
    return EnderecoService.buscar_cep_sync(cep)
