# Local AI Lab

Laboratório pessoal para executar, testar e avaliar modelos de IA localmente usando Ollama e Python.

## Objetivos

- Avaliar modelos locais e seu desempenho.
- Desenvolver um assistente em Python integrado ao Ollama.
- Criar testes automatizados.
- Registrar benchmarks e documentar os experimentos.

## Ambiente

- Sistema operacional: Windows
- Runtime de modelos: Ollama
- Modelo inicial: qwen3:4b-instruct
- Linguagem: Python
- Testes: pytest

## Primeiro benchmark

**Modelo:** qwen3:4b-instruct  
**Prompt:** Explique o que é uma API REST em no máximo duas frases.  
**Temperatura:** 0  
**Limite de geração:** 150 tokens  
**Repetições:** 3

### Resultados

- Tokens gerados: 80 por execução.
- Velocidade média observada: aproximadamente 93,66 tokens/s.
- Encerramento: stop nas três execuções.
- As três respostas foram idênticas.
- O tempo total medido pelo PowerShell variou entre 0,89 s e 3,17 s.

### Observações

O modelo produziu respostas completas e consistentes neste teste.
O tempo medido pelo cliente pode diferir do tempo informado pelo Ollama.
São necessárias mais execuções para investigar essa diferença e obter
uma estimativa mais confiável do desempenho.

## Assistente Python — primeira versão

O projeto agora possui um assistente de terminal integrado ao Ollama
por meio de sua API HTTP local.

### Funcionalidades

- Envio de perguntas ao modelo qwen3:4b-instruct.
- Conversa contínua pelo terminal até o usuário digitar sair.
- Configuração de temperatura e limite de tokens.
- Tratamento de erros HTTP, conexão, timeout e respostas inesperadas.
- Aviso quando a geração termina por atingir o limite de tokens.

### Testes automatizados

Os testes são executados com pytest.

- 3 testes para a integração do assistente com respostas simuladas.
- 4 testes para a função de cálculo de média.
- Resultado da última execução: **7 testes aprovados**.

### Tecnologias

- Python 3.13
- Ollama
- Qwen3 4B Instruct
- urllib e json
- pytest
- unittest.mock

## Memória de conversa

O assistente utiliza o endpoint /api/chat do Ollama para manter
o contexto das mensagens durante uma sessão.

### Funcionamento

- O histórico é armazenado em uma lista Python.
- Cada nova pergunta é enviada junto com as mensagens anteriores.
- Perguntas e respostas são adicionadas ao histórico após uma resposta válida.
- Em caso de erro na requisição, o histórico não é atualizado.
- O histórico é mantido apenas em memória RAM e é perdido ao encerrar o programa.
- O histórico utiliza uma janela deslizante limitada a 6 mensagens anteriores (3 pares de pergunta e resposta).
- As mensagens mais antigas são descartadas quando o limite é ultrapassado, reduzindo o crescimento do contexto enviado ao modelo.
- O comando `limpar` reinicia o histórico da conversa sem encerrar o assistente.
- O comando é processado localmente, sem enviar uma requisição ao Ollama.

### Seleção de modelos

O assistente permite selecionar diferentes modelos instalados no Ollama diretamente pela linha de comando, sem modificar o código Python.

**Executar com o modelo padrão (`qwen3:4b-instruct`):**

```powershell
python src/assistant.py
```

**Executar com um modelo específico:**

```powershell
python src/assistant.py --model qwen3:4b-instruct
```

**Consultar as opções disponíveis:**

```powershell
python src/assistant.py --help
```

Para visualizar os modelos instalados no Ollama:

```powershell
ollama list
```

> **Observação:** cada modelo pode apresentar comportamentos diferentes. Durante os testes, o `qwen3:4b` consumiu o limite de 500 tokens com raciocínio e não concluiu a resposta. Por isso, mantemos o `qwen3:4b-instruct` como modelo padrão.

### Configuração dos parâmetros de geração

O Local AI Lab permite personalizar o comportamento dos modelos diretamente pela linha de comando.

Os parâmetros disponíveis são:

| Parâmetro | Descrição | Valor padrão |
| --- | --- | --- |
| `--temperature` | Controla a aleatoriedade das respostas. | `0.0` |
| `--max-tokens` | Define o número máximo de tokens gerados por resposta. | `500` |

**Exemplo de execução:**

```powershell
python src/assistant.py --model qwen3:4b-instruct --temperature 0.3 --max-tokens 800
```

Para utilizar os valores padrão:

```powershell
python src/assistant.py
```

Para visualizar todos os argumentos disponíveis:

```powershell
python src/assistant.py --help
```

### Memória persistente com SQLite

O Local AI Lab utiliza SQLite para armazenar o histórico de conversas localmente, permitindo recuperar mensagens mesmo após encerrar e reiniciar o assistente.

A implementação utiliza a biblioteca `sqlite3`, disponível na biblioteca padrão do Python, sem necessidade de instalar um servidor de banco de dados.

#### (Funcionalidades)

- Criação automática do banco SQLite e da tabela `messages`.
- Armazenamento das perguntas e respostas após cada interação bem-sucedida.
- Recuperação do histórico ao iniciar o assistente.
- Utilização das últimas 6 mensagens como contexto para o modelo.
- Comando `limpar` para excluir o histórico em memória e no SQLite.
- Testes automatizados com bancos temporários, sem alterar os dados reais.

#### Executando o assistente

A partir da raiz do projeto:

```powershell
python -m src.assistant
```

Também é possível personalizar o modelo e os parâmetros de geração:

```powershell
python -m src.assistant --model qwen3:4b-instruct --temperature 0.3 --max-tokens 800
```

**Comandos disponíveis durante a conversa:**

| Comando | Descrição |
| --- | --- |
| `sair` | Encerra o programa, preservando o histórico salvo. |
| `limpar` | Exclui todas as mensagens armazenadas no SQLite e limpa o contexto atual. |

#### Armazenamento local

O banco é criado em:

```text
data/conversations.db
```

Esse arquivo está protegido pelo `.gitignore` e não é enviado ao GitHub.

**Atenção:** o armazenamento local não significa que o conteúdo esteja criptografado. Evite inserir senhas, tokens de acesso e outras informações sensíveis.

#### Testes Automatizados

Execute a suíte completa com:

```powershell
python -m pytest -v
```

Na conclusão desta etapa, o projeto possui **22 testes automatizados aprovados**, incluindo testes específicos para criação, leitura, escrita e limpeza da memória persistente.

### Validação

Foi realizado um teste manual em que o assistente recebeu
informações sobre o nome do usuário e a linguagem estudada.
Nas perguntas seguintes, recuperou corretamente ambas as informações.

Os testes automatizados foram adaptados ao formato da API /api/chat.

Também foi realizado um teste de esquecimento com o identificador
LAB-73921. Após interações suficientes para remover a mensagem
original da janela de histórico, o assistente não conseguiu
recuperar o identificador.

A suíte automatizada possui 12 testes aprovados, incluindo
testes específicos para o limite e a preservação do histórico.

O comando `limpar` foi validado manualmente e por um teste
automatizado que confirma que mensagens anteriores não são
enviadas ao modelo após a limpeza do histórico.

### Próximas melhorias

- Criar testes específicos para a atualização do histórico.
- Implementar um comando para limpar a conversa.
- Aprimorar o gerenciamento de contexto com limites baseados em tokens.
- Avaliar persistência do histórico em arquivo ou banco de dados.
- Implementar um comando para limpar a conversa.
