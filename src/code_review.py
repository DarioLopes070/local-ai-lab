import json

"""Estruturas e validações para análises de código com IA."""

SEVERIDADES_PERMITIDAS = {"baixa", "media", "alta"}

CAMPOS_OBRIGATORIOS = {
    "arquivo",
    "funcao",
    "problema",
    "evidencia",
    "severidade",
    "sugestao",
}


def validar_achado(achado):
    """Valida um problema identificado durante a análise de código."""

    if not isinstance(achado, dict):
        raise ValueError("O achado deve ser um objeto JSON.")

    if set(achado) != CAMPOS_OBRIGATORIOS:
        raise ValueError("O achado possui campos ausentes ou inesperados.")

    for campo in CAMPOS_OBRIGATORIOS:
        valor = achado[campo]

        if not isinstance(valor, str) or not valor.strip():
            raise ValueError(f"O campo '{campo}' deve ser um texto não vazio.")

    if achado["severidade"] not in SEVERIDADES_PERMITIDAS:
        raise ValueError("A severidade deve ser baixa, media ou alta.")

    return achado


def validar_relatorio(relatorio):
    """Valida um relatório contendo múltiplos achados."""

    if not isinstance(relatorio, dict):
        raise ValueError("O relatório deve ser um objeto JSON.")

    if set(relatorio) != {"achados"}:
        raise ValueError("O relatório deve conter somente o campo 'achados'.")

    achados = relatorio["achados"]

    if not isinstance(achados, list):
        raise ValueError("O campo 'achados' deve ser uma lista.")

    for achado in achados:
        validar_achado(achado)

    return relatorio


def processar_resposta_json(resposta):
    """Converte uma resposta JSON em um relatório validado."""

    if not isinstance(resposta, str) or not resposta.strip():
        raise ValueError("A resposta do modelo deve ser um texto não vazio.")

    try:
        relatorio = json.loads(resposta)
    except json.JSONDecodeError as erro:
        raise ValueError("O modelo retornou um JSON inválido.") from erro

    return validar_relatorio(relatorio)
