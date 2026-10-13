import json
import urllib.error
import urllib.request

# DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3:4b-instruct"

MAX_HISTORY_MESSAGES = 6


def ask_model(messages, url=DEFAULT_OLLAMA_URL, model=DEFAULT_MODEL, timeout=120):
    """Envia o histórico ao Ollama e retorna a resposta e o motivo do fim."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 500},
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        result = json.loads(response.read().decode("utf-8"))

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("message"), dict)
        or not isinstance(result["message"].get("content"), str)
    ):
        raise ValueError("O Ollama retornou uma resposta inesperada.")

    return result["message"]["content"], result.get("done_reason")


def limitar_historico(historico, max_messages=MAX_HISTORY_MESSAGES):
    """Mantém apenas as mensagens mais recentes do histórico."""
    return historico[-max_messages:] if max_messages > 0 else []


def main():
    print(f"Assistente IA Local ({DEFAULT_MODEL})")
    print("Digite 'sair' para encerrar ou 'limpar' para reiniciar a conversa.\n")

    historico = []

    while True:
        try:
            pergunta = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAssistente: Até mais!")
            break

        if pergunta.lower() == "sair":
            print("Assistente: Até mais!")
            break

        if pergunta.lower() == "limpar":
            historico.clear()
            print("\nAssistente: Histórico da conversa limpo!\n")
            continue

        if not pergunta:
            continue

        try:
            mensagens = historico + [{"role": "user", "content": pergunta}]

            resposta, motivo = ask_model(mensagens)

            historico.append({"role": "user", "content": pergunta})
            historico.append({"role": "assistant", "content": resposta})

            historico = limitar_historico(historico)

            if motivo == "length":
                print(
                    "\nAviso: a resposta pode estar incompleta "
                    "porque atingiu o limite de tokens."
                )

            print(f"\nAssistente: {resposta}\n")

        except urllib.error.HTTPError as error:
            print(f"\nErro HTTP do Ollama: {error.code}. Tente novamente.\n")

        except urllib.error.URLError as error:
            if isinstance(error.reason, TimeoutError):
                print("\nA solicitação demorou demais. Tente novamente.\n")
            else:
                print(
                    "\nNão foi possível conectar ao Ollama. "
                    "Verifique se ele está em execução e tente novamente.\n"
                )

        except TimeoutError:
            print("\nA solicitação demorou demais. Tente novamente.\n")

        except (json.JSONDecodeError, ValueError) as error:
            print(f"\nErro ao interpretar a resposta: {error}\n")


if __name__ == "__main__":
    main()
