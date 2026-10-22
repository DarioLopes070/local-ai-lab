import json
from unittest.mock import MagicMock

from src.tool_calling import (
    solicitar_ferramenta,
    validar_tool_call,
    executar_tool_call,
    responder_com_ferramenta,
)
import pytest


def simular_resposta_ollama(monkeypatch, mensagem):
    """Simula uma resposta da API do Ollama."""

    resposta_api = {"message": mensagem}

    resposta_simulada = MagicMock()
    resposta_simulada.read.return_value = json.dumps(resposta_api).encode("utf-8")

    contexto = MagicMock()
    contexto.__enter__.return_value = resposta_simulada

    def urlopen_simulado(request, timeout):
        payload = json.loads(request.data.decode("utf-8"))

        assert payload["tools"][0]["function"]["name"] == "listar_arquivos"
        assert timeout == 120

        return contexto

    monkeypatch.setattr(
        "src.tool_calling.urllib.request.urlopen",
        urlopen_simulado,
    )


def test_solicitar_ferramenta_retorna_tool_call(monkeypatch):
    simular_resposta_ollama(
        monkeypatch,
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "listar_arquivos",
                        "arguments": {},
                    }
                }
            ],
        },
    )

    resultado = solicitar_ferramenta("Quais arquivos existem no projeto?")

    assert resultado["tool_calls"][0]["function"]["name"] == "listar_arquivos"


def test_solicitar_ferramenta_sem_tool_call(monkeypatch):
    simular_resposta_ollama(
        monkeypatch,
        {
            "role": "assistant",
            "content": "Olá! Como posso ajudar?",
        },
    )

    resultado = solicitar_ferramenta("Olá!")

    assert resultado["content"] == "Olá! Como posso ajudar?"
    assert resultado["tool_calls"] == []


def test_validar_tool_call_permitido():
    chamada = {
        "function": {
            "name": "listar_arquivos",
            "arguments": {},
        }
    }

    nome, argumentos = validar_tool_call(chamada)

    assert nome == "listar_arquivos"
    assert argumentos == {}


def test_validar_tool_call_rejeita_ferramenta_desconhecida():
    chamada = {
        "function": {
            "name": "executar_comando",
            "arguments": {},
        }
    }

    with pytest.raises(ValueError, match="não autorizada"):
        validar_tool_call(chamada)


def test_validar_tool_call_rejeita_argumentos_invalidos():
    chamada = {
        "function": {
            "name": "listar_arquivos",
            "arguments": {"diretorio": "C:/Users"},
        }
    }

    with pytest.raises(ValueError, match="não aceita argumentos"):
        validar_tool_call(chamada)


def test_executar_tool_call_lista_arquivos_autorizados(tmp_path):
    """Executa a listagem somente dentro da raiz permitida."""

    (tmp_path / "README.md").write_text(
        "# Projeto de teste",
        encoding="utf-8",
    )

    (tmp_path / ".env").write_text(
        "API_KEY=segredo",
        encoding="utf-8",
    )

    chamada = {
        "function": {
            "name": "listar_arquivos",
            "arguments": {},
        }
    }

    resultado = executar_tool_call(
        chamada,
        raiz_autorizada=tmp_path,
    )

    assert resultado == ["README.md"]


def test_executar_tool_call_rejeita_ferramenta_desconhecida(tmp_path):
    """Impede a execução de ferramentas não autorizadas."""

    chamada = {
        "function": {
            "name": "executar_comando",
            "arguments": {},
        }
    }

    with pytest.raises(ValueError, match="não autorizada"):
        executar_tool_call(
            chamada,
            raiz_autorizada=tmp_path,
        )


def test_responder_com_ferramenta_ciclo_completo(monkeypatch, tmp_path):
    """Testa solicitação, execução e resposta final."""

    (tmp_path / "README.md").write_text(
        "# Projeto de teste",
        encoding="utf-8",
    )

    primeira_resposta = {
        "content": "",
        "tool_calls": [
            {
                "function": {
                    "name": "listar_arquivos",
                    "arguments": {},
                }
            }
        ],
    }

    monkeypatch.setattr(
        "src.tool_calling.solicitar_ferramenta",
        lambda pergunta: primeira_resposta,
    )

    resposta_final = {
        "message": {
            "role": "assistant",
            "content": "O projeto contém README.md.",
        }
    }

    resposta_simulada = MagicMock()
    resposta_simulada.read.return_value = json.dumps(resposta_final).encode("utf-8")

    contexto = MagicMock()
    contexto.__enter__.return_value = resposta_simulada

    def urlopen_simulado(request, timeout):
        payload = json.loads(request.data.decode("utf-8"))

        assert timeout == 120

        mensagens = payload["messages"]

        assert mensagens[1]["tool_calls"][0]["function"]["name"] == ("listar_arquivos")
        assert mensagens[2]["role"] == "tool"
        assert json.loads(mensagens[2]["content"]) == ["README.md"]

        return contexto

    monkeypatch.setattr(
        "src.tool_calling.urllib.request.urlopen",
        urlopen_simulado,
    )

    resposta = responder_com_ferramenta(
        "Quais arquivos existem neste projeto?",
        raiz_autorizada=tmp_path,
    )

    assert resposta == "O projeto contém README.md."


def test_responder_com_ferramenta_rejeita_multiplas_chamadas(monkeypatch, tmp_path):
    """Impede a execução de múltiplas ferramentas nesta versão."""

    chamada = {
        "function": {
            "name": "listar_arquivos",
            "arguments": {},
        }
    }

    monkeypatch.setattr(
        "src.tool_calling.solicitar_ferramenta",
        lambda pergunta: {
            "content": "",
            "tool_calls": [chamada, chamada],
        },
    )

    with pytest.raises(ValueError, match="somente uma chamada"):
        responder_com_ferramenta(
            "Liste os arquivos.",
            raiz_autorizada=tmp_path,
        )


def test_responder_com_ferramenta_rejeita_acao_nao_autorizada(monkeypatch, tmp_path):
    """Impede que o modelo solicite ferramentas desconhecidas."""

    monkeypatch.setattr(
        "src.tool_calling.solicitar_ferramenta",
        lambda pergunta: {
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "executar_comando",
                        "arguments": {},
                    }
                }
            ],
        },
    )

    with pytest.raises(ValueError, match="não autorizada"):
        responder_com_ferramenta(
            "Execute uma ação no sistema.",
            raiz_autorizada=tmp_path,
        )


@pytest.mark.parametrize(
    "mensagem_invalida",
    [
        None,
        "resposta inesperada",
        {"content": 123},
        {"content": "Olá", "tool_calls": "listar_arquivos"},
    ],
)
def test_solicitar_ferramenta_rejeita_resposta_invalida(monkeypatch, mensagem_invalida):
    """Rejeita respostas malformadas da API do Ollama."""

    simular_resposta_ollama(
        monkeypatch,
        mensagem_invalida,
    )

    with pytest.raises(ValueError):
        solicitar_ferramenta("Liste os arquivos do projeto.")
