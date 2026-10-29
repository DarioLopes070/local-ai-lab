import json
import ast

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


def validar_resposta_code_review(resposta_modelo):
    """Processa e valida um relatório JSON produzido pelo modelo."""

    return processar_resposta_json(resposta_modelo)


def analisar_codigo(pergunta, raiz_autorizada):
    """Solicita uma análise ao Ollama e valida o relatório JSON."""

    from src.tool_calling import responder_com_ferramenta

    instrucoes = """
Responda exclusivamente com um objeto JSON válido.

Estrutura obrigatória:
{
    "achados": [
        {
            "arquivo": "nome_do_arquivo.py",
            "funcao": "nome_da_funcao",
            "problema": "descricao do problema",
            "evidencia": "trecho do codigo",
            "severidade": "baixa",
            "sugestao": "correcao recomendada"
        }
    ]
}

Use somente as severidades: baixa, media ou alta.
Se nenhum problema for identificado, retorne {"achados": []}.
Não utilize Markdown nem blocos de código.
Não execute ou modifique arquivos.
"""

    pergunta_completa = f"{instrucoes}\n\n{pergunta}"

    resposta = responder_com_ferramenta(
        pergunta_completa,
        raiz_autorizada=raiz_autorizada,
    )

    return validar_resposta_code_review(resposta)


def validar_funcoes_relatorio(relatorio, codigo_fonte):
    """Verifica se as funções citadas existem no código analisado."""

    validar_relatorio(relatorio)

    arvore = ast.parse(codigo_fonte)

    funcoes_existentes = {
        node.name
        for node in ast.walk(arvore)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    for achado in relatorio["achados"]:
        nome_funcao = achado["funcao"]

        if nome_funcao not in funcoes_existentes:
            raise ValueError(f"Função não encontrada no código: {nome_funcao}")

        evidencia = achado["evidencia"]

        if evidencia.strip() not in codigo_fonte:
            raise ValueError(f"Evidência não encontrada no código: {evidencia}")

    return relatorio


def analisar_codigo_com_validacao(
    pergunta,
    raiz_autorizada,
    caminho_arquivo,
):
    """Analisa código e valida os achados contra o arquivo real."""

    from src.tools.file_tools import ler_arquivo

    # O caminho é definido por quem utiliza a função,
    # não pelo modelo de linguagem.
    codigo_fonte = ler_arquivo(
        caminho_arquivo,
        raiz_autorizada=raiz_autorizada,
    )

    relatorio = analisar_codigo(
        pergunta,
        raiz_autorizada=raiz_autorizada,
    )

    for achado in relatorio["achados"]:
        if achado["arquivo"] != caminho_arquivo:
            raise ValueError("O relatório menciona um arquivo diferente do analisado.")

    return validar_funcoes_relatorio(
        relatorio,
        codigo_fonte,
    )
