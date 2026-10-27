
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
