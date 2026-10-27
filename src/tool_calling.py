import json
import urllib.request

from src.assistant import DEFAULT_MODEL, DEFAULT_OLLAMA_URL
from pathlib import Path

from src.tools.file_tools import listar_arquivos, ler_arquivo
from pathlib import PureWindowsPath

FERRAMENTAS = [
    {
        "type": "function",
        "function": {
            "name": "listar_arquivos",
            "description": "Lista arquivos de um projeto autorizado.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "ler_arquivo",
            "description": (
                "Lê o conteúdo de um arquivo de texto ou código "
                "dentro do projeto autorizado. Informe o caminho "
                "relativo à raiz do projeto."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "caminho_arquivo": {
                        "type": "string",
                        "description": (
                            "Caminho relativo do arquivo, "
                            "por exemplo: src/assistant.py"
                        ),
                    },
                },
                "required": ["caminho_arquivo"],
                "additionalProperties": False,
            },
        },
    },
]


def validar_tool_call(tool_call):
    """Valida uma solicitação de ferramenta retornada pelo LLM."""

    if not isinstance(tool_call, dict):
        raise ValueError("A solicitação de ferramenta deve ser um objeto.")

    funcao = tool_call.get("function")

    if not isinstance(funcao, dict):
        raise ValueError("A solicitação não contém uma função válida.")

    nome = funcao.get("name")
    argumentos = funcao.get("arguments")

    ferramentas_permitidas = {
        ferramenta["function"]["name"] for ferramenta in FERRAMENTAS
    }

    if nome not in ferramentas_permitidas:
        raise ValueError(f"Ferramenta não autorizada: {nome}")

    if not isinstance(argumentos, dict):
        raise ValueError("Os argumentos da ferramenta devem ser um objeto.")

    if nome == "listar_arquivos":
        if argumentos:
            raise ValueError("A ferramenta listar_arquivos não aceita argumentos.")

    elif nome == "ler_arquivo":
        if set(argumentos) != {"caminho_arquivo"}:
            raise ValueError(
                "A ferramenta ler_arquivo exige somente " "o argumento caminho_arquivo."
            )

        caminho = argumentos["caminho_arquivo"]

        if not isinstance(caminho, str) or not caminho.strip():
            raise ValueError("O caminho do arquivo deve ser um texto não vazio.")

        if "\x00" in caminho:
            raise ValueError("O caminho contém caracteres inválidos.")

        caminho_windows = PureWindowsPath(caminho)

        if caminho_windows.is_absolute() or caminho_windows.drive:
            raise ValueError("Caminhos absolutos não são permitidos.")

        partes = caminho.replace("\\", "/").split("/")

        if ".." in partes:
            raise ValueError("Não é permitido navegar para fora do projeto.")

    return nome, argumentos


def solicitar_ferramenta(pergunta, model=DEFAULT_MODEL):
    """Consulta o Ollama e retorna solicitações de ferramentas."""

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": pergunta}],
        "tools": FERRAMENTAS,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 500,
        },
    }

    dados = json.dumps(payload).encode("utf-8")

    requisicao = urllib.request.Request(
        DEFAULT_OLLAMA_URL,
        data=dados,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(requisicao, timeout=120) as resposta:
        resultado = json.loads(resposta.read().decode("utf-8"))

    if not isinstance(resultado, dict):
        raise ValueError("Resposta inválida do Ollama.")

    mensagem = resultado.get("message")

    if not isinstance(mensagem, dict):
        raise ValueError("O Ollama não retornou uma mensagem válida.")

    conteudo = mensagem.get("content", "")
    chamadas = mensagem.get("tool_calls", [])

    if not isinstance(conteudo, str):
        raise ValueError("Conteúdo inválido na resposta do Ollama.")

    if not isinstance(chamadas, list):
        raise ValueError("Lista de ferramentas inválida.")

    return {
        "content": conteudo,
        "tool_calls": chamadas,
    }


def executar_tool_call(tool_call, raiz_autorizada):
    """Executa somente ferramentas previamente autorizadas."""

    nome, argumentos = validar_tool_call(tool_call)

    raiz = Path(raiz_autorizada).resolve(strict=True)

    if not raiz.is_dir():
        raise NotADirectoryError(f"A raiz autorizada não é um diretório: {raiz}")

    if nome == "listar_arquivos":
        return listar_arquivos(
            raiz,
            raiz_autorizada=raiz,
            max_arquivos=100,
        )

    if nome == "ler_arquivo":
        caminho = argumentos["caminho_arquivo"]

        return ler_arquivo(
            caminho,
            raiz_autorizada=raiz,
        )

    raise ValueError(f"Ferramenta sem executor: {nome}")


def responder_com_ferramenta(pergunta, raiz_autorizada):
    """Executa um ciclo controlado de tool calling com o Ollama."""

    # Primeiro, o modelo decide se precisa de uma ferramenta.
    primeira_resposta = solicitar_ferramenta(pergunta)

    chamadas = primeira_resposta["tool_calls"]

    if not chamadas:
        return primeira_resposta["content"]

    # Nesta primeira versão, aceitamos exatamente uma chamada.
    if len(chamadas) != 1:
        raise ValueError("Esta versão aceita somente uma chamada de ferramenta.")

    chamada = chamadas[0]

    # Valida e executa somente a ferramenta autorizada.
    resultado = executar_tool_call(
        chamada,
        raiz_autorizada=raiz_autorizada,
    )

    # Preserva a solicitação de ferramenta do assistente.
    mensagem_assistente = {
        "role": "assistant",
        "content": primeira_resposta["content"],
        "tool_calls": [chamada],
    }

    mensagens = [
        {"role": "user", "content": pergunta},
        mensagem_assistente,
        {
            "role": "tool",
            "tool_name": chamada["function"]["name"],
            "content": json.dumps(resultado, ensure_ascii=False),
        },
    ]

    # Segunda consulta: o modelo recebe o resultado da ferramenta.
    payload = {
        "model": DEFAULT_MODEL,
        "messages": mensagens,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 1200,
        },
    }

    requisicao = urllib.request.Request(
        DEFAULT_OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(requisicao, timeout=120) as resposta:
        dados = json.loads(resposta.read().decode("utf-8"))

    mensagem_final = dados.get("message", {})

    if not isinstance(mensagem_final, dict):
        raise ValueError("Resposta inválida do Ollama.")

    conteudo = mensagem_final.get("content")

    if not isinstance(conteudo, str):
        raise ValueError("O Ollama não retornou texto válido.")

    if mensagem_final.get("tool_calls"):
        raise ValueError("O modelo solicitou outra ferramenta após a execução.")

    return conteudo
