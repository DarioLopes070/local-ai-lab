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

### Validação

Foi realizado um teste manual em que o assistente recebeu
informações sobre o nome do usuário e a linguagem estudada.
Nas perguntas seguintes, recuperou corretamente ambas as informações.

Os testes automatizados foram adaptados ao formato da API /api/chat.

Resultado: 7 testes aprovados.

Também foi realizado um teste de esquecimento com o identificador
LAB-73921. Após interações suficientes para remover a mensagem
original da janela de histórico, o assistente não conseguiu
recuperar o identificador.

A suíte automatizada possui 12 testes aprovados, incluindo
testes específicos para o limite e a preservação do histórico.

### Próximas melhorias

- Criar testes específicos para a atualização do histórico.
- Implementar um comando para limpar a conversa.
- Controlar o tamanho do histórico para evitar excesso de contexto.
- Avaliar persistência do histórico em arquivo ou banco de dados.
