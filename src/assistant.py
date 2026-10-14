import argparse
import json
import urllib.error
import urllib.request

# DEFAULT_OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3:4b-instruct"

MAX_HISTORY_MESSAGES = 6


def ask_model(
    messages,
    url=DEFAULT_OLLAMA_URL,
    model=DEFAULT_MODEL,
    timeout=120,
    temperature=0.0,
    max_tokens=500,
):
    """Envia o histórico ao Ollama e retorna a resposta e o motivo do fim."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
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


def main(
    model=DEFAULT_MODEL,
    temperature=0.0,
    max_tokens=500,
):
    print(f"Assistente IA Local ({model})")
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

            resposta, motivo = ask_model(
                mensagens,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

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
    parser = argparse.ArgumentParser(
        description="Assistente de IA local utilizando Ollama."
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Modelo do Ollama (padrão: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperatura de geração (padrão: 0.0)",
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=500,
        help="Número máximo de tokens gerados (padrão: 500)",
    )

    args = parser.parse_args()

    if not 0.0 <= args.temperature <= 2.0:
        parser.error("--temperature deve estar entre 0.0 e 2.0.")

    if args.max_tokens < 1:
        parser.error("--max-tokens deve ser maior que zero.")

    main(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
