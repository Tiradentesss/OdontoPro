import json
import os

ARQUIVO = "permissoes.json"


def carregar_permissoes():
    if not os.path.exists(ARQUIVO):
        return {}

    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_permissoes(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
