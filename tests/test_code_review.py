import pytest
from src.code_review import (
    validar_achado,
    validar_relatorio,
    processar_resposta_json,
)


def test_validar_achado_valido():
    """Aceita um achado com todos os campos obrigatórios."""

    achado = {
        "arquivo": "calculadora.py",
        "funcao": "calcular_media",
        "problema": "Divisão por zero com lista vazia",
        "evidencia": "sum(notas) / len(notas)",
        "severidade": "media",
        "sugestao": "Tratar listas vazias.",
    }

    resultado = validar_achado(achado)

    assert resultado == achado


@pytest.mark.parametrize(
    "alteracao",
    [
        {"remover": "evidencia"},
        {"severidade": "critica"},
        {"problema": ""},
        {"campo_extra": "valor inesperado"},
    ],
)
def test_validar_achado_rejeita_dados_invalidos(alteracao):
    """Rejeita achados com estrutura ou valores inválidos."""

    achado = {
        "arquivo": "calculadora.py",
        "funcao": "calcular_media",
        "problema": "Divisão por zero",
        "evidencia": "sum(notas) / len(notas)",
        "severidade": "media",
        "sugestao": "Tratar listas vazias.",
    }

    if "remover" in alteracao:
        achado.pop(alteracao["remover"])
    else:
        achado.update(alteracao)

    with pytest.raises(ValueError):
        validar_achado(achado)


def test_validar_relatorio_com_multiplos_achados():
    """Aceita um relatório com dois problemas válidos."""

    relatorio = {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "calcular_media",
                "problema": "Divisão por zero",
                "evidencia": "sum(notas) / len(notas)",
                "severidade": "media",
                "sugestao": "Tratar listas vazias.",
            },
            {
                "arquivo": "calculadora.py",
                "funcao": "calcular_desconto",
                "problema": "Percentual não validado",
                "evidencia": "preco * percentual / 100",
                "severidade": "media",
                "sugestao": "Validar percentual entre 0 e 100.",
            },
        ]
    }

    resultado = validar_relatorio(relatorio)

    assert resultado == relatorio
    assert len(resultado["achados"]) == 2


def test_validar_relatorio_sem_achados():
    """Aceita um relatório sem problemas identificados."""

    relatorio = {"achados": []}

    resultado = validar_relatorio(relatorio)

    assert resultado == relatorio


@pytest.mark.parametrize(
    "relatorio",
    [
        None,
        "Nenhum problema encontrado",
        {},
        {"achados": "sem problemas"},
        {"achados": None},
        {"achados": [], "status": "concluido"},
        {"achados": [None]},
        {"achados": [{"problema": "Divisão por zero"}]},
    ],
)
def test_validar_relatorio_rejeita_dados_invalidos(relatorio):
    """Rejeita relatórios malformados ou com achados inválidos."""

    with pytest.raises(ValueError):
        validar_relatorio(relatorio)


def test_processar_resposta_json_valida():
    """Converte JSON válido em um relatório Python."""

    resposta = """
    {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "calcular_media",
                "problema": "Divisão por zero",
                "evidencia": "sum(notas) / len(notas)",
                "severidade": "media",
                "sugestao": "Tratar listas vazias."
            }
        ]
    }
    """

    resultado = processar_resposta_json(resposta)

    assert len(resultado["achados"]) == 1
    assert resultado["achados"][0]["funcao"] == "calcular_media"
    assert resultado["achados"][0]["severidade"] == "media"


@pytest.mark.parametrize(
    "resposta",
    [
        "",
        "   ",
        None,
        "Nenhum problema encontrado.",
        '{"achados": [}',
        '{"achados": "nenhum"}',
        '{"achados": [{"problema": "Divisão por zero"}]}',
        '{"achados": [], "campo_extra": true}',
    ],
)
def test_processar_resposta_json_rejeita_dados_invalidos(resposta):
    """Rejeita respostas vazias, JSON inválido e relatórios incorretos."""

    with pytest.raises(ValueError):
        processar_resposta_json(resposta)
