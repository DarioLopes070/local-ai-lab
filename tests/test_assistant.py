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

    def fake_ask_model(messages):
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
