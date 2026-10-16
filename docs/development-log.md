
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
