import json
from urllib.error import URLError
from unittest.mock import patch

import pytest

from src.assistant import ask_model


@patch("src.assistant.urllib.request.urlopen")
def test_ask_model_returns_response(mock_urlopen):
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = json.dumps({
        "message": {
            "role": "assistant",
            "content": "Uma API REST usa HTTP."
        },
        "done_reason": "stop"
    }).encode("utf-8")

    mensagens = [
        {"role": "user", "content": "O que é uma API REST?"}
    ]

    resposta, motivo = ask_model(mensagens)

    assert resposta == "Uma API REST usa HTTP."
    assert motivo == "stop"


@patch("src.assistant.urllib.request.urlopen")
def test_ask_model_rejects_unexpected_response(mock_urlopen):
    mock_response = mock_urlopen.return_value.__enter__.return_value
    mock_response.read.return_value = json.dumps({
        "unexpected": "data"
    }).encode("utf-8")

    mensagens = [
        {"role": "user", "content": "Teste"}
    ]

    with pytest.raises(ValueError):
        ask_model(mensagens)


@patch("src.assistant.urllib.request.urlopen")
def test_ask_model_propagates_connection_error(mock_urlopen):
    mock_urlopen.side_effect = URLError("Conexão recusada")

    mensagens = [
        {"role": "user", "content": "Teste"}
    ]

    with pytest.raises(URLError):
        ask_model(mensagens)