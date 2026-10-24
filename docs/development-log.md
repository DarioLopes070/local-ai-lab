
# Local AI Lab — Diário de Desenvolvimento

## Semana de 13 a 16 de outubro de 2026

### Objetivo

Evoluir o assistente local em Python e Ollama, adicionando parâmetros configuráveis e memória persistente para conversas.

### Entregas realizadas

#### 13/10 — Parâmetros de geração

- Configuração de `temperature` por linha de comando.
- Configuração de `max_tokens` por linha de comando.
- Validação de argumentos inválidos com `argparse`.
- Testes automatizados para os parâmetros enviados ao Ollama.
- 15 testes aprovados.
- Commit: `900783f`.

#### 14/10 — Módulo SQLite

- Criação do módulo `src/memory.py`.
- Inicialização automática do banco.
- Funções para salvar e recuperar mensagens.
- Testes com bancos temporários.
- Proteção dos dados locais no `.gitignore`.
- 20 testes aprovados.
- Commit: `9f7c23f`.

#### 15/10 — Integração da memória

- Carregamento de mensagens ao iniciar o assistente.
- Salvamento automático das perguntas e respostas.
- Recuperação do contexto após reiniciar o programa.
- Integração do comando `limpar` ao SQLite.
- Isolamento do banco de dados nos testes.
- 22 testes automatizados aprovados.
- Padronização da execução com `python -m src.assistant`.

### Decisões técnicas

- Utilizar SQLite por ser leve e não exigir serviços externos.
- Manter as últimas seis mensagens no contexto enviado ao modelo.
- Preservar o histórico completo no banco local até a limpeza.
- Não versionar bancos SQLite contendo conversas.
- Manter `qwen3:4b-instruct` como modelo padrão.

### Melhorias futuras identificadas

- Salvar pares de mensagens em uma única transação SQLite.
- Melhorar o tratamento de erros de persistência.
- Criar identificadores para diferentes conversas.
- Adicionar gerenciamento de histórico e sessões.
- Implementar ferramentas locais para leitura de arquivos e análise de código.

### Próxima fase

Preparar a arquitetura de um agente local de programação com ferramentas controladas, mantendo o foco em testes automatizados, segurança e baixo consumo de recursos.

## Semana de 19 a 23 de outubro de 2026

### 19/10 — Primeira ferramenta de arquivos

Iniciada a evolução do assistente conversacional para um agente local de programação.

#### Implementações

- Criação do pacote `src/tools/`.
- Implementação da função `listar_arquivos()`.
- Filtros para diretórios internos e arquivos sensíveis conhecidos.
- Limite configurável para a quantidade de arquivos retornados.
- Exigência de uma raiz autorizada.
- Bloqueio de caminhos externos.
- Proteção contra links simbólicos e junctions do Windows.

#### Testes e aprendizados

Durante os testes, foi identificado que uma junction do Windows permitia listar arquivos externos ao projeto.

A implementação foi corrigida para controlar a travessia de diretórios e verificar os caminhos resolvidos antes de acessar seu conteúdo.

Resultado da suíte completa: **36 testes aprovados, 1 ignorado e nenhuma falha**.

#### Próximos passos

- Implementar leitura controlada de arquivos.
- Adicionar restrições de extensão e tamanho.
- Revisar as proteções antes da integração com o Ollama.
- Investigar o suporte do modelo local a tool calling.

### 20/10 — Leitura controlada de arquivos

Implementada a segunda ferramenta do futuro agente local de programação: `ler_arquivo()`.

#### Implementações_

- Leitura de arquivos `.py`, `.md`, `.json` e `.txt`.
- Validação de caminhos dentro de uma raiz autorizada.
- Bloqueio de acessos externos ao projeto.
- Restrição de links simbólicos e junctions do Windows.
- Bloqueio de diretórios internos e arquivos sensíveis conhecidos.
- Limitação de arquivos a 100.000 bytes.
- Leitura de conteúdo em UTF-8.

#### Testes e resultados

Foram criados testes automatizados para verificar:

- Leitura de arquivos permitidos.
- Rejeição de caminhos externos.
- Bloqueio de arquivos `.env`.
- Rejeição de extensões inválidas.
- Rejeição de arquivos acima do limite.
- Bloqueio de junctions externas.
- Bloqueio de diretórios protegidos.

Resultado da suíte completa: **47 testes aprovados, 1 ignorado e nenhuma falha**.

#### Próximos passos_

- Revisar as proteções das ferramentas de arquivos.
- Investigar o suporte do Ollama a tool calling.
- Integrar as ferramentas ao assistente.
- Testar análise de código com informações reais do projeto.

A integração com o modelo de IA permanece pendente.

### 21–22/10 — Primeiro Tool Calling com Ollama

Implementada uma integração experimental entre o modelo local `qwen3:4b-instruct` e ferramentas Python.

#### Implementações__

- Criação do módulo `src/tool_calling.py`.
- Definição de ferramentas disponíveis para o Ollama.
- Recebimento e interpretação de `tool_calls`.
- Validação de nomes e argumentos das ferramentas solicitadas.
- Execução controlada da ferramenta `listar_arquivos()`.
- Envio dos resultados das ferramentas de volta ao modelo.
- Rejeição de ferramentas desconhecidas e múltiplas chamadas.
- Validação de respostas malformadas da API.

#### Experimento realizado

Foi criado um diretório temporário contendo dois arquivos:

- `README.md`
- `exemplo.py`

O modelo solicitou a ferramenta `listar_arquivos()`, recebeu os nomes dos arquivos encontrados e respondeu corretamente à pergunta.

Esse experimento validou o primeiro ciclo completo:

**Usuário → Ollama → ferramenta Python → Ollama → resposta final.**

#### Testes automatizados

Foram criados 14 testes relacionados ao módulo de Tool Calling.

Resultado da suíte completa: **61 testes aprovados, 1 ignorado e nenhuma falha**.

#### Limitações atuais

- A integração ainda está separada do assistente principal.
- Apenas `listar_arquivos()` está disponível no Tool Calling.
- O sistema permite somente uma chamada de ferramenta por pergunta.
- Não existem permissões para editar arquivos ou executar comandos.
- O tratamento de erros e os controles de segurança ainda serão aprimorados.

#### Próximos passos__

- Fortalecer a validação e o isolamento das ferramentas.
- Integrar `ler_arquivo()` ao Tool Calling.
- Criar testes para análise de código-fonte.
- Planejar a integração com o assistente principal e sua memória SQLite.

### 22/10 — Integração de leitura de arquivos ao Tool Calling

#### Objetivo_

Permitir que o modelo local Qwen3 solicite a leitura de arquivos Python e produza explicações baseadas no conteúdo real dos arquivos.

#### Implementações___

- Registro da ferramenta `ler_arquivo()` na definição de ferramentas do Ollama.
- Validação do argumento obrigatório `caminho_arquivo`.
- Rejeição de caminhos absolutos, navegação com `..` e argumentos inesperados.
- Integração de `ler_arquivo()` ao executor controlado.
- Preservação das restrições existentes de acesso a arquivos.
- Correção de uma regressão identificada pelos testes de `listar_arquivos()`.

#### Experimento prático

Foi criado um arquivo Python contendo a função `calcular_media(notas)`.

O modelo `qwen3:4b-instruct` solicitou a leitura do arquivo e explicou corretamente:

- A utilização de `sum()` para somar os valores.
- A utilização de `len()` para contar os elementos.
- O cálculo da média aritmética.
- O resultado 9 para as notas `[8, 9, 10]`.

#### Validação

Resultado da suíte completa:

- 71 testes aprovados.
- 1 teste ignorado.
- Nenhuma falha.

#### Próximos passos___

- Ampliar os testes de segurança das ferramentas.
- Experimentar análises de código para identificação de possíveis bugs.
- Avaliar respostas do modelo em diferentes arquivos Python.
- Planejar a integração gradual ao assistente principal.

### 23/10 — Primeira avaliação de análise estática com Qwen3

#### Objetivo__

Avaliar a capacidade do agente local de identificar possíveis bugs em código Python utilizando a ferramenta `ler_arquivo()`.

#### Experimento

Foi criado um arquivo temporário `calculadora.py`, contendo uma função de cálculo de média com defeitos intencionais.

Os cenários avaliados incluíram:

- Lista vazia, causando `ZeroDivisionError`.
- Valores `None`, causando `TypeError` e descumprindo a documentação.
- Valores não numéricos, causando `TypeError`.
- Entradas numéricas válidas.

#### Resultados

- O modelo identificou corretamente os principais problemas apresentados.
- Reconheceu a inconsistência entre a docstring e a implementação.
- Demonstrou limitações na interpretação do contexto da ferramenta.
- Uma resposta apresentou alteração aparente de um valor de entrada.

#### Documentação

Criado `results/qa-evaluation.md` para registrar os cenários, resultados e limitações observadas.

#### Próximos passos____

- Definir critérios quantitativos de avaliação.
- Investigar falsos positivos e problemas de fidelidade.
- Criar novos cenários de análise de código.
- Comparar resultados de modelos locais.
