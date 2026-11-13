
# QA Evaluation — Local AI Lab

## Experiment 1 — Static Code Analysis

**Date:** 2026-10-23  
**Model:** qwen3:4b-instruct  
**Tool:** ler_arquivo  
**Target:** calculadora.py

### Test cases

| ID | Input | Expected behavior | Status |
| --- | --- | --- | --- |
| QA-001 | [8, 9, 10] | Returns 9.0 | Correctly identified |
| QA-002 | [] | Raises ZeroDivisionError | Identified in experiment 1 |
| QA-003 | [8, None, 10] | Raises TypeError; violates requirement to ignore None | Identified in experiment 1 |
| QA-004 | [8, "abc", 10] | Raises TypeError | Identified in experiment 2 |

### Observations

- The model identified the main defects through static analysis.
- The model recognized a mismatch between documentation and implementation.
- The model incorrectly suggested that the external tool `ler_arquivo` should appear in the analyzed source code.
- One response contained an apparent change to an example input.
- The second response was not fully captured for evaluation.

### Conclusion

The experiment demonstrates promising results for simple Python code review.

However, further evaluation is required to measure reliability,
false positives, input fidelity, and performance on more complex code.

## Experiment 2 — Structured Code Review

**Date:** 2026-10-26
**Model:** qwen3:4b-instruct
**Tool:** ler_arquivo
**Target:** calculadora.py
**Generation limit:** 1200 tokens (final response)

### Expected defects

| ID | Defect | Detected |
| --- | --- | --- |
| QA-005 | Empty list causes ZeroDivisionError | No |
| QA-006 | None values are not ignored | Yes |
| QA-007 | Non-numeric inputs cause TypeError | No |
| QA-008 | Discount percentage is not validated | Yes |

### Results

- 2 of 4 predefined defects identified (50% coverage).
- Both functions were analyzed.
- The response followed the requested structure.
- The model incorrectly stated that sum() returns None or 0 when given None.
- The model suggested returning 0 for missing values without a defined business rule.
- Increasing the final response limit from 500 to 1200 tokens allowed the report to finish.

### Conclusion_

The model can identify some genuine defects and produce
structured review reports, but technical accuracy and coverage
remain inconsistent.

Further tests are needed before using these results in
automated QA workflows.

### 2026-11-12 — Revisão direta do modelo (exploratória, não pontuável)

Foram feitas três chamadas diretas a `ask_model` com `qwen3:4b-instruct`. A saída impressa confirmou que o código de `calculadora.py` foi incluído na pergunta enviada ao modelo. Essas chamadas não avaliaram o fluxo completo de ferramentas do revisor.

Menções na resposta bruta:

- Lista vazia em `calcular_media`: 3 de 3 execuções.
- Valores `None` em `calcular_media`: 2 de 3.
- Entradas não numéricas em `calcular_media`: 1 de 3.
- Percentual fora do intervalo de 0 a 100: 3 de 3.

Nenhuma execução passou pela validação: nas duas primeiras respostas, o campo `arquivo` veio vazio; na terceira, o modelo escreveu `severiadade` em vez de `severidade`. Também houve evidência truncada e duplicação de achado em respostas anteriores. Portanto, essas contagens são observações exploratórias da resposta bruta, não uma pontuação válida do modelo nem do fluxo.

### 2026-11-12 — Repetibilidade da revisão direta com código incluído

Foram feitas duas execuções consecutivas, sem alterar o comando, da revisão de `teste-json-review-20261112/calculadora.py` com `qwen3:4b-instruct`. Nas duas, o relatório passou pela validação e foi idêntico: apontou o tratamento ausente para valores `None` em `calcular_media`.

Em cada execução, identificou 1 dos 4 defeitos conhecidos. Não apontou a média de lista vazia, as entradas não numéricas nem o percentual de desconto fora do intervalo. As duas respostas também usaram a mesma evidência: `return sum(notas) / len(notas)`.

Resultado: consistência observada em 2/2 execuções, com alcance limitado a esse caso e a essa amostra. Isso não avalia o fluxo encadeado de ferramentas do revisor.

### 2026-11-13 — Verificação instrumentada de solicitação de ferramenta

Em uma execução instrumentada de `analisar_codigo_com_validacao()` com `qwen3:4b-instruct`, a saída registrou `Ferramentas solicitadas pelo modelo: []`. Portanto, nesta execução, o modelo não solicitou nem executou `ler_arquivo`; respondeu sem chamada de ferramenta.

O relatório foi aceito pela validação e apontou o tratamento ausente para valores `None` em `calcular_media`, usando como evidência `return sum(notas) / len(notas)`. O conteúdo do arquivo havia sido lido localmente por `analisar_codigo_com_validacao()` e incluído na pergunta enviada ao modelo.

Este resultado confirma uma execução sem solicitação de ferramenta. Não comprova o comportamento em outras execuções nem substitui um teste do fluxo em que o modelo precise solicitar `ler_arquivo`.

### 2026-11-13 — Solicitação explícita de leitura via ferramenta

Em uma chamada direta a `analisar_codigo()`, a pergunta instruiu o modelo a usar `ler_arquivo` para ler `teste-json-review-20261112/calculadora.py`. A instrumentação registrou `Ferramentas solicitadas pelo modelo: ['listar_arquivos']`; portanto, o modelo não solicitou `ler_arquivo`.

A resposta final foi `{'achados': []}`. Como não houve leitura do arquivo pela ferramenta, esse resultado não confirma que o conteúdo foi analisado nem que o arquivo não contém problemas. Trata-se de uma observação exploratória desta execução.

### 2026-11-13 — Tentativa de leitura com resposta curta

Em uma chamada direta a `analisar_codigo()`, a pergunta solicitou o uso de `ler_arquivo` e pediu apenas a primeira linha do arquivo. A instrumentação registrou `Ferramentas solicitadas pelo modelo: []`; portanto, nenhuma ferramenta foi solicitada. A resposta retornada foi `{'achados': []}`, que não contém a linha pedida e não comprova leitura do arquivo.

Esta é uma observação exploratória de uma execução, não uma conclusão sobre todas as chamadas do modelo.

### 2026-11-13 — Leitura controlada com ler_arquivo

Em uma chamada direta a `solicitar_ferramenta()`, com `ler_arquivo` como única ferramenta disponível, o modelo solicitou `ler_arquivo` com o caminho `teste-json-review-20261112/calculadora.py`.

Em seguida, `responder_com_ferramenta()` completou o ciclo e retornou `def calcular_media(notas):`.

Com as duas ferramentas originais disponíveis, uma nova chamada a `solicitar_ferramenta()` também solicitou `ler_arquivo` com o caminho esperado; `responder_com_ferramenta()` completou o ciclo e retornou a mesma primeira linha.

Esses resultados confirmam o funcionamento nesses testes controlados, mas não determinam a causa das execuções anteriores em que nenhuma ferramenta foi solicitada ou foi escolhida `listar_arquivos`.

### 2026-11-13 — Comparação de seleção de ferramenta na revisão

Foram feitas cinco execuções por condição, com o mesmo prompt e o mesmo arquivo de teste.

- `qwen3:4b-instruct`, somente `ler_arquivo`: solicitou a ferramenta e o caminho esperados nas 5 execuções. Os relatórios mencionaram problemas com valores `None` e validação do percentual, mas não cobriram todos os casos pedidos.
- `qwen3:4b-instruct`, `listar_arquivos` e `ler_arquivo` disponíveis: escolheu `listar_arquivos` nas 5 execuções e retornou `{"achados": []}`.
- `qwen3.5:4b`, ambas as ferramentas disponíveis: escolheu `ler_arquivo` com o caminho esperado nas 5 execuções e produziu relatórios.

O resultado indica dificuldade do `qwen3:4b-instruct` em selecionar a ferramenta adequada neste prompt quando ambas estão disponíveis, mas não incapacidade geral de solicitar ferramentas. A condição com apenas `ler_arquivo` comprova que ele consegue solicitá-la quando é a única opção.

Os relatórios incluíram a evidência parcial `return preco - (preco * percentual / 10`. No código de validação consultado, a evidência é aceita por correspondência de substring; como esse trecho é prefixo da linha que usa `/100`, isso não demonstra que o modelo tenha interpretado o cálculo como divisão por 10. Demonstra, porém, que a validação aceita evidências incompletas. A validação textual não comprova a correção semântica dos achados.

As cinco repetições por condição tiveram saídas idênticas neste experimento. Como o fluxo configura temperatura 0, elas não devem ser interpretadas como amostras independentes nem como medida de variabilidade.


### 2026-11-13 — Suíte de testes após os experimentos

Execução local de `python -m pytest -q`: **104 passed, 1 skipped** em **2.47s**.

### 2026-11-13 — Reexecução da suíte após limpeza

Após a remoção dos arquivos e da pasta temporária dos experimentos, `python -m pytest -q` foi executado novamente: **104 passed, 1 skipped** em **1.48s**. `git diff --check` não apontou erros; permaneceu apenas o aviso do Git sobre conversão de LF para CRLF.
