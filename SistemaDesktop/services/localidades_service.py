import json
import os
import unicodedata


class LocalidadesService:
    ESTADOS = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    _cidades_por_uf = None

    @classmethod
    def carregar_estados(cls):
        return cls.ESTADOS.copy()

    @classmethod
    def carregar_cidades(cls, uf):
        dados = cls._carregar_dados()
        return dados.get(str(uf or "").upper(), []).copy()

    @classmethod
    def filtrar_cidades(cls, uf, termo):
        cidades = cls.carregar_cidades(uf)
        termo_normalizado = cls._normalizar(termo)
        if not termo_normalizado:
            return cidades

        comeca_com_termo = [
            cidade for cidade in cidades
            if cls._normalizar(cidade).startswith(termo_normalizado)
        ]
        contem_termo = [
            cidade for cidade in cidades
            if termo_normalizado in cls._normalizar(cidade)
            and not cls._normalizar(cidade).startswith(termo_normalizado)
        ]
        return comeca_com_termo + contem_termo

    @classmethod
    def cidade_existe(cls, uf, cidade):
        cidade_normalizada = cls._normalizar(cidade)
        return any(
            cls._normalizar(item) == cidade_normalizada
            for item in cls.carregar_cidades(uf)
        )

    @classmethod
    def selecionar_cidade(cls, uf, cidade):
        cidade_normalizada = cls._normalizar(cidade)
        for item in cls.carregar_cidades(uf):
            if cls._normalizar(item) == cidade_normalizada:
                return item
        return ""

    @classmethod
    def _carregar_dados(cls):
        if cls._cidades_por_uf is None:
            caminho = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "municipios_brasil.json"
            )
            with open(caminho, "r", encoding="utf-8-sig") as arquivo:
                cls._cidades_por_uf = json.load(arquivo)

        return cls._cidades_por_uf

    @staticmethod
    def _normalizar(texto):
        texto = str(texto or "").strip().lower()
        texto = unicodedata.normalize("NFD", texto)
        return "".join(c for c in texto if unicodedata.category(c) != "Mn")
