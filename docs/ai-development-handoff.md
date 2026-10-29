# Local AI Lab — AI Development Handoff

**Atualizado em:** 29/10/2026  
**Repositório:** <https://github.com/DarioLopes070/local-ai-lab>
**Branch principal:** `main`  
**Idioma de trabalho:** português do Brasil (`pt-BR`)

## 1. Finalidade deste documento

Este documento permite que outro assistente de IA (como Gemini) continue o desenvolvimento do **Local AI Lab** sem reconstruir as decisões e o histórico de cada conversa. **Antes de propor alterações, consulte o estado real do repositório**, porque o projeto pode ter evoluído desde esta versão.

## 2. Objetivo do projeto

Construir progressivamente um **assistente de programação com modelos locais via Ollama**, executado em um computador Windows, com foco em:

- Conversação com um modelo local;
- Memória persistente de conversas;
- Ferramentas controladas para listar e ler arquivos do projeto;
- Análise estática de código, identificação de possíveis defeitos e suporte a QA;
- Avaliação mensurável da qualidade das respostas;
- Baixo custo recorrente e documentação pública dos experimentos.

**Estado atual:** protótipo experimental, ainda não um agente autônomo de programação. Não executa comandos de shell nem altera arquivos a pedido do modelo.

## 3. Ambiente do desenvolvedor

- **Sistema:** Windows 11, VS Code e PowerShell.
- **Diretório local:** `D:\projeto\local-ai-lab`.
- **Python verificado nos testes:** 3.15.0, instalado em `C:\Python315\python.exe`.
- **Testes:** pytest 9.1.1 na última saída verificada.
- **IA local:** Ollama, usando `qwen3:4b-instruct` nas demonstrações de Tool Calling.
- **Computador:** notebook com Ryzen 7 5800H, 32 GB de RAM e NVIDIA RTX 3060 com 6 GB de VRAM.
- **Controle de versão:** Git e GitHub, branch `main`.
- **Custo:** priorizar componentes locais e bibliotecas gratuitas, sem APIs pagas obrigatórias.

As versões de Ollama/modelos devem ser confirmadas no ambiente antes de depender de detalhes específicos.

## 4. Estrutura relevante do projeto

```text
local-ai-lab/
├── README.md                         # Visão geral, uso e documentação
├── docs/
│   ├── development-log.md            # Diário técnico das entregas
│   └── ai-development-handoff.md     # Este documento
├── results/
│   ├── qa-evaluation.md              # Avaliações manuais de análise de código
│   └── benchmark.csv                 # Resultados de experimentos anteriores
├── src/
│   ├── assistant.py                  # Assistente CLI; chamada ao Ollama
│   ├── memory.py                     # Conversas persistidas em SQLite
│   ├── tool_calling.py               # Solicitação, validação e execução de ferramentas
│   ├── code_review.py                # Validação estrutural de relatórios JSON
│   └── tools/
│       └── file_tools.py             # Acesso controlado a arquivos
└── tests/
    ├── test_tool_calling.py
    ├── test_code_review.py
    └── test_file_tools.py
```

Esta é uma **visão parcial** dos arquivos importantes, não uma listagem exaustiva. Confira os diretórios no GitHub para obter a versão vigente.

## 5. Funcionalidades implementadas

### 5.1 Assistente CLI e memória

- `src/assistant.py`: integração com a API `/api/chat` do Ollama; parâmetros de modelo, temperatura e limites de geração; comandos como `sair` e `limpar`.
- `src/memory.py`: armazenamento de conversas em SQLite e recuperação de histórico recente.
- O comando de execução do assistente utiliza importações de pacote:

```powershell
python -m src.assistant
```

### 5.2 Ferramentas para arquivos

Em `src/tools/file_tools.py`:

- `listar_arquivos(...)`: lista arquivos numa raiz autorizada, com limite de resultados, exclusão de diretórios sensíveis e verificações de caminhos.
- `ler_arquivo(...)`: permite leitura de arquivos de texto/código autorizados, com extensões permitidas e limite de tamanho.
- Há verificações de caminhos fora da raiz, arquivos sensíveis, links simbólicos e *junctions* do Windows. **Não tratar isso como uma sandbox completa**: ainda há riscos e testes de segurança a ampliar.

### 5.3 Tool Calling

Em `src/tool_calling.py`:

- `solicitar_ferramenta(pergunta, ...)`: apresenta ao Ollama as ferramentas disponíveis e recebe possíveis `tool_calls`.
- `validar_tool_call(tool_call)`: valida nomes de ferramentas e argumentos, incluindo os caminhos de `ler_arquivo`.
- `executar_tool_call(tool_call, raiz_autorizada)`: executa apenas ferramentas permitidas usando a raiz definida pelo Python, não pelo LLM.
- `responder_com_ferramenta(pergunta, raiz_autorizada)`: completa um ciclo **usuário → Ollama → ferramenta → Ollama → resposta**.

Ferramentas atualmente integradas: `listar_arquivos` e `ler_arquivo`. A implementação experimental admite **uma chamada de ferramenta por pergunta**. Foi aumentado para **1.200 tokens** o limite da resposta final do ciclo, para reduzir truncamento de relatórios longos. Confirmar o código real antes de alterar limites.

### 5.4 Validação estrutural de relatórios de análise de código

Em `src/code_review.py`:

- `validar_achado(achado)`: verifica exatamente os campos `arquivo`, `funcao`, `problema`, `evidencia`, `severidade`, `sugestao`. Todos exigem texto não vazio.
- Severidades aceitas: `baixa`, `media`, `alta` (sem acentos, conforme implementação).
- `validar_relatorio(relatorio)`: valida `{"achados": [...]}`, permitindo lista vazia e rejeitando campos inesperados.
- `processar_resposta_json(resposta)`: converte texto JSON em dados Python e aplica validação estrutural, levantando `ValueError` quando inválido.
- **Ainda não há integração operacional desse módulo com a resposta real do Ollama** na última etapa documentada.

Exemplo válido:

```json
{
  "achados": [
    {
      "arquivo": "calculadora.py",
      "funcao": "calcular_media",
      "problema": "Divisão por zero com lista vazia",
      "evidencia": "sum(notas) / len(notas)",
      "severidade": "media",
      "sugestao": "Tratar explicitamente entradas vazias."
    }
  ]
}
```

**Atenção:** validação JSON não comprova que o bug existe, nem valida automaticamente evidências, severidade ou qualidade da sugestão.

## 6. Testes e marco de estabilidade

**Última execução relatada pelo desenvolvedor em 27/10/2026:**

```text
95 passed, 1 skipped
```

Desses, **24 testes** foram desenvolvidos para `tests/test_code_review.py`. O teste ignorado já existia em etapas anteriores (há condições específicas de ambiente para certos testes Windows).

Comandos de verificação:

```powershell
cd D:\projeto\local-ai-lab
python -m pytest -q
git status --short
```

Na última verificação compartilhada, a branch `main` estava sincronizada com `origin/main`, sem alterações pendentes. Essa informação pode mudar; sempre verificar novamente.

## 7. Experimentos de QA e limitações observadas

- O modelo leu e explicou uma função de média em um arquivo Python real usando `ler_arquivo`.
- Em um cenário de quatro defeitos conhecidos, o Qwen3 identificou **2 de 4 (50%) em uma execução específica**. Isso **não** é uma métrica geral do modelo.
- O modelo identificou corretamente o desrespeito ao requisito de ignorar `None` e a ausência de validação de desconto entre 0% e 100%.
- Omitiu outros casos em certas respostas, como lista vazia e entrada não numérica.
- Cometeu erro de explicação técnica: afirmou que `sum([8, None, 10])` retornaria `None` ou `0`. Em Python essa operação produz `TypeError`.
- O modelo às vezes solicitou caminho inexistente (`src/calculadora.py` em vez de `calculadora.py`) e o código encerrou com `FileNotFoundError`; tratamento gracioso de erro de ferramenta ainda é melhoria pendente.
- Respostas longas foram truncadas quando o limite era 500 tokens; aumento para 1.200 ajudou no cenário verificado, sem garantir completude em todos os casos.

Detalhamento em `results/qa-evaluation.md` e `docs/development-log.md`.

## 8. Segurança e decisões arquiteturais

1. O modelo **nunca escolhe a raiz autorizada**; o programa hospedeiro define essa raiz.
2. O modelo não deve receber ferramenta de comando do sistema, escrita ou execução de código neste estágio.
3. Validar argumentos antes de qualquer execução de ferramenta e aplicar controles adicionais na própria ferramenta.
4. Não conceder acesso irrestrito à máquina; preferir diretórios de teste isolados.
5. Considerar conteúdo de arquivos e respostas do LLM como dados não confiáveis; evitar seguir instruções embutidas em arquivos analisados.
6. Evitar expor credenciais, `.env`, arquivos pessoais e dados de produção.
7. Tratar erros de leitura/caminho de forma clara, preservando segurança e auditabilidade.
8. Novas integrações exigem testes automatizados e validação prática antes de commits.

## 9. Próxima tarefa exata — Integração com Ollama

**Objetivo da próxima sessão:** fazer o Qwen3 retornar um relatório JSON que `src/code_review.py` consiga interpretar e validar, mantendo ferramentas de arquivos somente de leitura.

Sequência sugerida, em incrementos pequenos:

1. Inspecionar `src/tool_calling.py`, `src/code_review.py` e os testes atuais, sem reescrever componentes existentes.
2. Definir como solicitar ao modelo **somente JSON** com `{"achados": [...]}`. Avaliar compatibilidade com a API de Ollama instalada; não presumir suporte sem conferir.
3. Começar com testes simulados do payload e da conversão/validação da resposta, antes de chamar o modelo real.
4. Integrar uma única função que reaproveite a execução autorizada de `ler_arquivo`, devolva o conteúdo ao Ollama e valide o JSON produzido.
5. Tratar JSON malformado, resposta vazia, truncamento, segunda chamada de ferramenta inesperada e caminhos inexistentes.
6. Executar `python -m pytest -q` e comparar com a linha de base de 95 testes aprovados/1 ignorado.
7. Registrar o experimento no Development Log e no README; depois fazer commit e push somente após validação.

**Importante:** não confundir **resultado em formato estruturado** com **acerto técnico dos achados**. A medição de acurácia de QA fica para o próximo ciclo.

## 10. Plano semanal original (26/10 a 01/11)

| Dia | Planejamento | Situação na última conversa |
| --- | --- | --- |
| Seg 26/10 | Prompt e avaliação estruturada de revisão de código | Concluído |
| Ter 27/10 | Módulo JSON e testes | Concluído; 95 testes aprovados no projeto |
| Qua 28/10 | Integrar validação JSON ao Ollama/Tool Calling | Pendente na última conversa |
| Qui 29/10 | Avaliação quantitativa de QA | Replanejar após integração |
| Sex 30/10 | Revisar testes, documentação e publicar | Planejado; concluir antes do pôr do sol |
| Sáb 31/10 | Sem trabalho no projeto | Descanso religioso |
| Dom 01/11 | Revisão semanal e próximas prioridades | Planejado |

Este planejamento é uma referência, não uma obrigação rígida. Priorizar concluir a integração pendente com segurança em vez de apressar as tarefas seguintes.

## Atualização — 29/10/2026

### Estado atual

O Local AI Lab possui uma integração experimental entre Tool Calling e análise estruturada de código.

O módulo `src/code_review.py` contém:

- `validar_achado()`
- `validar_relatorio()`
- `processar_resposta_json()`
- `validar_resposta_code_review()`
- `analisar_codigo()`
- `validar_funcoes_relatorio()`
- `analisar_codigo_com_validacao()`

### Experimento relevante

O Qwen3 retornou um relatório JSON válido mencionando uma função inexistente (`dividir`).

A ferramenta de leitura foi verificada separadamente e retornou corretamente o conteúdo de `calculadora.py`, contendo `calcular_media()`.

Foram implementadas verificações adicionais para rejeitar funções e evidências inexistentes.

### Testes

Última validação geral:

- 102 testes aprovados.
- 1 teste ignorado.

### Próxima atividade

Executar um experimento real com `analisar_codigo_com_validacao()`, verificando se o Python rejeita automaticamente achados inconsistentes produzidos pelo Qwen3.

### Regras de continuidade

- Desenvolver uma etapa por vez.
- Criar testes automatizados antes de ampliar funcionalidades.
- Preservar o acesso somente de leitura.
- Não executar código sugerido pelo modelo automaticamente.
- Atualizar README, Development Log e este documento ao concluir cada etapa.

## Atualização — 29/10/2026 — JSON no Tool Calling

### Implementação

O módulo `src/tool_calling.py` agora permite solicitar respostas JSON na segunda chamada ao Ollama:

```python
responder_com_ferramenta(
    pergunta,
    raiz_autorizada,
    formato_json=True,
)
```

O modo JSON é utilizado por `analisar_codigo()` em `src/code_review.py`.

O modo tradicional continua disponível por padrão, utilizando `formato_json=False`.

### Experimentos e resultados

- O Qwen3 conseguiu solicitar `ler_arquivo()` corretamente.
- A ferramenta retornou o conteúdo real de `calculadora.py`.
- O parâmetro `format: "json"` foi testado na segunda requisição ao Ollama.
- O modelo identificou defeitos conhecidos em alguns experimentos.
- Foram observados relatórios vazios e interpretações tecnicamente incorretas.
- A validação estrutural e textual não garante que um bug seja verdadeiro.

### Testes_

Última validação:

- 104 testes aprovados.
- 1 teste ignorado.
- Nenhuma falha.

### Próxima atividade_

Desenvolver avaliações quantitativas de QA para medir a capacidade do modelo de identificar defeitos conhecidos.

Prioridades:

1. Criar um conjunto controlado de arquivos Python com bugs.
2. Definir os resultados esperados para cada cenário.
3. Comparar os achados do Qwen3 com os defeitos conhecidos.
4. Medir acertos, omissões e falsos positivos.
5. Registrar os resultados em `results/qa-evaluation.md`.

### Regras de continuidade_

- Trabalhar uma implementação e um teste por vez.
- Preservar o acesso somente de leitura.
- Não executar automaticamente código fornecido pelo modelo.
- Manter README, Development Log e este documento sincronizados.
- Utilizar o GitHub como fonte principal de continuidade.

## 11. Como o assistente deve colaborar

- **Responder em português do Brasil**, de forma objetiva e didática.
- **Uma etapa por vez**: informar exatamente qual arquivo abrir, onde inserir o código, entregar trecho pronto para copiar e o comando PowerShell do teste.
- **Esperar o resultado do terminal** antes de propor a próxima mudança; não despejar todo o projeto de uma só vez.
- Explicar brevemente o propósito de cada mudança, sem prolixidade excessiva.
- Nunca afirmar que testes, push ou integrações funcionaram sem evidência de execução.
- Ao encontrar teste quebrado, investigar e corrigir a causa; não remover testes para fazer a suíte passar.
- Manter `README.md`, `docs/development-log.md` e o GitHub como registros duráveis.
- Não agendar tarefas na sexta após o pôr do sol nem no sábado, salvo pedido expresso do desenvolvedor.
- Distinguir observação, hipótese e resultado confirmado; não apresentar percentuais experimentais como precisão geral.

## 12. Mensagem inicial para outro assistente

> Estou desenvolvendo o projeto open source Local AI Lab, em Python, no Windows 11, com Ollama e Qwen3 local. Leia integralmente este handoff e consulte o código atual do repositório <https://github.com/DarioLopes070/local-ai-lab> antes de sugerir mudanças. A linha de base verificada foi 95 testes aprovados e 1 ignorado. A próxima tarefa é integrar a saída JSON de análise de código com o fluxo de Tool Calling existente, reaproveitando `src/code_review.py` e mantendo acesso apenas de leitura. Trabalhe comigo passo a passo: forneça somente a primeira alteração, seu teste e o comando exato no PowerShell; espere o resultado antes de avançar. Não invente código ou arquivos que não tenha verificado.
