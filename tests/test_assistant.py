import json
from urllib.error import URLError
from unittest.mock import patch

import pytest

from src.assistant import ask_model, limitar_historico, main


@patch("src.assistant.urllib.request.urlopen")
def test_ask_model_returns_response(mock_urlopen):
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = json.dumps(
        {
            "message": {"role": "assistant", "content": "Uma API REST usa HTTP."},
            "done_reason": "stop",
        }
    ).encode("utf-8")

    mensagens = [{"role": "user", "content": "O que é uma API REST?"}]

    resposta, motivo = ask_model(mensagens)

    assert resposta == "Uma API REST usa HTTP."
    assert motivo == "stop"


@patch("src.assistant.urllib.request.urlopen")
def test_ask_model_rejects_unexpected_response(mock_urlopen):
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = json.dumps({"unexpected": "data"}).encode("utf-8")

    mensagens = [{"role": "user", "content": "Teste"}]

    with pytest.raises(ValueError):
        ask_model(mensagens)


@patch("src.assistant.urllib.request.urlopen")
def test_ask_model_propagates_connection_error(mock_urlopen):
    mock_urlopen.side_effect = URLError("Conexão recusada")

    mensagens = [{"role": "user", "content": "Teste"}]

    with pytest.raises(URLError):
        ask_model(mensagens)


def test_limitar_historico_menor_que_limite():
    historico = [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Oi!"},
    ]

    resultado = limitar_historico(historico)

    assert resultado == historico


def test_limitar_historico_maior_que_limite():
    historico = []

    for i in range(5):
        historico.append({"role": "user", "content": f"Pergunta {i}"})
        historico.append({"role": "assistant", "content": f"Resposta {i}"})

    resultado = limitar_historico(historico)

    assert len(resultado) == 6
    assert resultado == historico[-6:]
    assert resultado[0]["content"] == "Pergunta 2"
    assert resultado[-1]["content"] == "Resposta 4"


def test_limitar_historico_vazio():
    assert limitar_historico([]) == []


def test_limitar_historico_nao_modifica_original():
    historico = [{"role": "user", "content": str(i)} for i in range(10)]

    original = historico.copy()

    limitar_historico(historico)

    assert historico == original


def test_limitar_historico_igual_ao_limite():
    historico = [{"role": "user", "content": str(i)} for i in range(6)]

    resultado = limitar_historico(historico)

    assert len(resultado) == 6
    assert resultado == historico


def test_comando_limpar_reinicia_historico(monkeypatch, capsys):
    entradas = iter(
        [
            "Meu código secreto é LAB-48296",
            "Qual é meu código secreto?",
            "limpar",
            "Qual é meu código secreto?",
            "sair",
        ]
    )

    chamadas = []

    def fake_input(prompt):
        return next(entradas)

    def fake_ask_model(messages, **kwargs):
        chamadas.append([mensagem.copy() for mensagem in messages])
        return "Resposta simulada", "stop"

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("src.assistant.ask_model", fake_ask_model)

    main()

    # O Ollama deve ser chamado apenas para as três perguntas.
    assert len(chamadas) == 3

    # Antes de limpar, o histórico deve estar disponível.
    assert chamadas[1] == [
        {"role": "user", "content": "Meu código secreto é LAB-48296"},
        {"role": "assistant", "content": "Resposta simulada"},
        {"role": "user", "content": "Qual é meu código secreto?"},
    ]

    # Depois de limpar, somente a nova pergunta deve ser enviada.
    assert chamadas[2] == [{"role": "user", "content": "Qual é meu código secreto?"}]

    saida = capsys.readouterr().out
    assert "Histórico da conversa limpo!" in saida


def test_main_utiliza_modelo_selecionado(monkeypatch, capsys):
    entradas = iter(
        [
            "Olá!",
            "sair",
        ]
    )

    chamadas = []

    def fake_input(prompt):
        return next(entradas)

    def fake_ask_model(messages, model, temperature, max_tokens):
        chamadas.append(
            {
                "messages": [mensagem.copy() for mensagem in messages],
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        return "Olá! Como posso ajudar?", "stop"

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr("src.assistant.ask_model", fake_ask_model)

    main(
        model="qwen3:4b",
        temperature=0.3,
        max_tokens=800,
    )

    assert len(chamadas) == 1
    assert chamadas[0]["model"] == "qwen3:4b"
    assert chamadas[0]["messages"] == [{"role": "user", "content": "Olá!"}]

    saida = capsys.readouterr().out
    assert "Assistente IA Local (qwen3:4b)" in saida
    assert chamadas[0]["model"] == "qwen3:4b"
    assert chamadas[0]["temperature"] == 0.3
    assert chamadas[0]["max_tokens"] == 800


def test_ask_model_envia_parametros_de_geracao(monkeypatch):
    import json
    from unittest.mock import MagicMock

    from src.assistant import ask_model

    resposta_api = {
        "message": {"content": "Resposta de teste"},
        "done_reason": "stop",
    }

    resposta_simulada = MagicMock()
    resposta_simulada.read.return_value = json.dumps(resposta_api).encode("utf-8")

    contexto_simulado = MagicMock()
    contexto_simulado.__enter__.return_value = resposta_simulada

    def urlopen_simulado(request, timeout):
        payload = json.loads(request.data.decode("utf-8"))

        assert payload["model"] == "qwen3:4b-instruct"
        assert payload["options"]["temperature"] == 0.3
        assert payload["options"]["num_predict"] == 800
        assert timeout == 120

        return contexto_simulado

    monkeypatch.setattr(
        "src.assistant.urllib.request.urlopen",
        urlopen_simulado,
    )

    resposta, motivo = ask_model(
        [{"role": "user", "content": "Olá"}],
        model="qwen3:4b-instruct",
        temperature=0.3,
        max_tokens=800,
    )

    assert resposta == "Resposta de teste"
    assert motivo == "stop"
