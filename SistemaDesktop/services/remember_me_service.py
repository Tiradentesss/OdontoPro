import json
import os

ARQUIVO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "remember_me.json")


def carregar_credenciais():
    if not os.path.exists(ARQUIVO):
        return {}

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def salvar_credenciais(email, senha):
    dados = {
        "email": email,
        "senha": senha
    }
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)


def limpar_credenciais():
    if os.path.exists(ARQUIVO):
        os.remove(ARQUIVO)
