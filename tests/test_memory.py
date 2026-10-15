import pytest

from src.memory import (
    inicializar_banco,
    salvar_mensagem,
    carregar_mensagens,
)


@pytest.fixture
def banco_temporario(tmp_path):
    """Cria um banco isolado para cada teste."""
    db_path = tmp_path / "test_conversations.db"
    inicializar_banco(db_path)
    return db_path


def test_inicializar_banco(banco_temporario):
    assert banco_temporario.exists()


def test_salvar_e_carregar_mensagem(banco_temporario):
    salvar_mensagem(
        "user",
        "Meu projeto se chama Local AI Lab",
        banco_temporario,
    )

    mensagens = carregar_mensagens(banco_temporario)

    assert mensagens == [
        {
            "role": "user",
            "content": "Meu projeto se chama Local AI Lab",
        }
    ]


def test_carregar_mensagens_mantem_ordem(banco_temporario):
    salvar_mensagem("user", "Olá", banco_temporario)
    salvar_mensagem("assistant", "Olá! Como posso ajudar?", banco_temporario)
    salvar_mensagem("user", "O que é Python?", banco_temporario)

    mensagens = carregar_mensagens(banco_temporario)

    assert [mensagem["role"] for mensagem in mensagens] == [
        "user",
        "assistant",
        "user",
    ]

    assert mensagens[0]["content"] == "Olá"
    assert mensagens[1]["content"] == "Olá! Como posso ajudar?"
    assert mensagens[2]["content"] == "O que é Python?"


def test_salvar_mensagem_rejeita_role_invalido(banco_temporario):
    with pytest.raises(ValueError):
        salvar_mensagem(
            "system",
            "Mensagem inválida",
            banco_temporario,
        )


def test_carregar_banco_vazio(banco_temporario):
    assert carregar_mensagens(banco_temporario) == []
