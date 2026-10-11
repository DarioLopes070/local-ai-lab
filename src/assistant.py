import json
import urllib.error
import urllib.request

# OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen3:4b-instruct"


def ask_model(messages):
    """Envia o histórico ao Ollama e retorna a resposta e o motivo do fim."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 500},
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("message"), dict)
        or not isinstance(result["message"].get("content"), str)
    ):
        raise ValueError("O Ollama retornou uma resposta inesperada.")

    return result["message"]["content"], result.get("done_reason")


def main():
    print("Assistente IA Local")
    print("Digite 'sair' para encerrar.\n")

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

        if not pergunta:
            continue

        try:
            mensagens = historico + [{"role": "user", "content": pergunta}]

            resposta, motivo = ask_model(mensagens)

            historico.append({"role": "user", "content": pergunta})
            historico.append({"role": "assistant", "content": resposta})

            if motivo == "length":
                print(
                    "\nAviso: a resposta pode estar incompleta "
                    "porque atingiu o limite de tokens."
                )

            print(f"\nAssistente: {resposta}\n")

        except urllib.error.HTTPError as error:
            print(f"\nErro HTTP do Ollama: {error.code}. Tente novamente.\n")

        except urllib.error.URLError:
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
