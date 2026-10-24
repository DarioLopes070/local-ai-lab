
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
