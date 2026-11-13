import pytest
from src.code_review import (
    validar_achado,
    validar_relatorio,
    processar_resposta_json,
    validar_resposta_code_review,
    analisar_codigo,
    validar_funcoes_relatorio,
    analisar_codigo_com_validacao,
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
    """Rejeita relatórios sem achados."""

    with pytest.raises(ValueError, match="pelo menos um achado"):
        validar_relatorio({"achados": []})

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


def test_validar_resposta_code_review():
    """Rejeita uma resposta sem achados."""

    with pytest.raises(ValueError, match="pelo menos um achado"):
        validar_resposta_code_review('{"achados": []}')

def test_analisar_codigo_retorna_relatorio_validado(monkeypatch, tmp_path):
    """Testa a integração sem chamar o Ollama."""

    def resposta_simulada(pergunta, raiz_autorizada, formato_json=False):
        assert "exclusivamente" in pergunta
        assert "calculadora.py" in pergunta
        assert raiz_autorizada == tmp_path
        assert formato_json is True
        return (
            '{"achados":[{"arquivo":"calculadora.py",'
            '"funcao":"calcular_media",'
            '"problema":"Divisão por zero",'
            '"evidencia":"return sum(notas) / len(notas)",'
            '"severidade":"media",'
            '"sugestao":"Tratar listas vazias."}]}'
        )

    monkeypatch.setattr(
        "src.tool_calling.responder_com_ferramenta",
        resposta_simulada,
    )

    resultado = analisar_codigo(
        "Leia calculadora.py e identifique possíveis bugs.",
        raiz_autorizada=tmp_path,
    )

    assert len(resultado["achados"]) == 1
    assert resultado["achados"][0]["funcao"] == "calcular_media"

def test_validar_funcoes_relatorio_rejeita_funcao_inexistente():
    """Rejeita uma função inventada pelo modelo."""

    codigo = """
def calcular_media(notas):
    return sum(notas) / len(notas)
"""

    relatorio = {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "dividir",
                "problema": "Divisão por zero",
                "evidencia": "return a / b",
                "severidade": "alta",
                "sugestao": "Validar o divisor.",
            }
        ]
    }

    with pytest.raises(
        ValueError,
        match="Função não encontrada",
    ):
        validar_funcoes_relatorio(relatorio, codigo)


def test_validar_funcoes_relatorio_aceita_funcao_existente():
    """Aceita um relatório que menciona uma função real."""

    codigo = """
def calcular_media(notas):
    return sum(notas) / len(notas)
"""

    relatorio = {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "calcular_media",
                "problema": "Divisão por zero com lista vazia",
                "evidencia": "return sum(notas) / len(notas)",
                "severidade": "media",
                "sugestao": "Tratar listas vazias.",
            }
        ]
    }

    resultado = validar_funcoes_relatorio(
        relatorio,
        codigo_fonte=codigo,
    )

    assert resultado == relatorio


def test_validar_funcoes_relatorio_rejeita_evidencia_inventada():
    """Rejeita uma evidência que não existe no código-fonte."""

    codigo = """
def calcular_media(notas):
    return sum(notas) / len(notas)
"""

    relatorio = {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "calcular_media",
                "problema": "Divisão por zero",
                "evidencia": "return a / b",
                "severidade": "media",
                "sugestao": "Tratar listas vazias.",
            }
        ]
    }

    with pytest.raises(
        ValueError,
        match="Evidência não encontrada",
    ):
        validar_funcoes_relatorio(relatorio, codigo)


def test_analisar_codigo_com_validacao_rejeita_funcao_inventada(monkeypatch, tmp_path):
    """Rejeita função inexistente mesmo com JSON válido."""

    arquivo = tmp_path / "calculadora.py"
    arquivo.write_text(
        "def calcular_media(notas):\n" "    return sum(notas) / len(notas)\n",
        encoding="utf-8",
    )

    relatorio_simulado = {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "dividir",
                "problema": "Divisão por zero",
                "evidencia": "return a / b",
                "severidade": "alta",
                "sugestao": "Validar o divisor.",
            }
        ]
    }

    monkeypatch.setattr(
        "src.code_review.analisar_codigo",
        lambda pergunta, raiz_autorizada: relatorio_simulado,
    )

    with pytest.raises(ValueError, match="Função não encontrada"):
        analisar_codigo_com_validacao(
            pergunta="Analise calculadora.py.",
            raiz_autorizada=tmp_path,
            caminho_arquivo="calculadora.py",
        )


def test_analisar_codigo_com_validacao_aceita_relatorio_valido(monkeypatch, tmp_path):
    """Aceita uma análise com função e evidência existentes."""

    arquivo = tmp_path / "calculadora.py"
    arquivo.write_text(
        "def calcular_media(notas):\n" "    return sum(notas) / len(notas)\n",
        encoding="utf-8",
    )

    relatorio_simulado = {
        "achados": [
            {
                "arquivo": "calculadora.py",
                "funcao": "calcular_media",
                "problema": "Divisão por zero com lista vazia",
                "evidencia": "return sum(notas) / len(notas)",
                "severidade": "media",
                "sugestao": "Tratar listas vazias.",
            }
        ]
    }

    def analisar_simulada(pergunta, raiz_autorizada):
        assert "def calcular_media(notas):" in pergunta
        assert "return sum(notas) / len(notas)" in pergunta
        return relatorio_simulado

    monkeypatch.setattr(
        "src.code_review.analisar_codigo",
        analisar_simulada,
    )

    resultado = analisar_codigo_com_validacao(
        pergunta="Analise calculadora.py.",
        raiz_autorizada=tmp_path,
        caminho_arquivo="calculadora.py",
    )

    assert resultado == relatorio_simulado
    assert len(resultado["achados"]) == 1
    assert resultado["achados"][0]["funcao"] == "calcular_media"


def test_processar_resposta_json_rejeita_relatorio_vazio():
    """Rejeita JSON válido cuja lista de achados está vazia."""

    with pytest.raises(ValueError, match="pelo menos um achado"):
        processar_resposta_json('{"achados": []}')


def test_validar_funcoes_relatorio_rejeita_evidencia_parcial():
    """Rejeita um trecho que não corresponde à linha completa."""

    codigo = "def calcular_media(notas):\n    return sum(notas) / len(notas)\n"
    relatorio = {
        "achados": [{
            "arquivo": "calculadora.py",
            "funcao": "calcular_media",
            "problema": "Divisão por zero",
            "evidencia": "sum(notas) / len(notas)",
            "severidade": "media",
            "sugestao": "Tratar listas vazias.",
        }]
    }

    with pytest.raises(ValueError, match="linhas completas"):
        validar_funcoes_relatorio(relatorio, codigo)


def test_validar_funcoes_relatorio_rejeita_evidencia_de_outra_funcao():
    """Rejeita linha existente no arquivo, mas fora da função citada."""

    codigo = (
        "def calcular_media(notas):\n"
        "    return sum(notas) / len(notas)\n"
        "\n"
        "def multiplicar(a, b):\n"
        "    return a * b\n"
    )
    relatorio = {
        "achados": [{
            "arquivo": "calculadora.py",
            "funcao": "calcular_media",
            "problema": "Problema alegado",
            "evidencia": "return a * b",
            "severidade": "media",
            "sugestao": "Revisar a função.",
        }]
    }

    with pytest.raises(ValueError, match="linhas completas"):
        validar_funcoes_relatorio(relatorio, codigo)
