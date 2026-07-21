"""Logger leve para consultas SQL usado pelo projeto.

Este módulo fornece funções compatíveis com as importações existentes em
controllers e services, sem depender de bibliotecas externas.
"""

from __future__ import annotations

from typing import Any, Callable

_query_count = 0


def reset_query_count() -> None:
    global _query_count
    _query_count = 0


def get_query_count() -> int:
    return _query_count


def inc_query_count(amount: int = 1) -> None:
    global _query_count
    _query_count += amount


def timed_sql(label: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Executa a função informada e contabiliza uma consulta.

    O parâmetro ``label`` é mantido apenas para compatibilidade com os
    pontos de chamada existentes. Parâmetros extras como ``sql`` são
    ignorados porque eles são usados apenas para logging/diagnóstico.
    """
    kwargs.pop("sql", None)
    inc_query_count()
    return func(*args, **kwargs)
