# Manuscript Status

## Current State

The Overleaf PDF snapshot in `paper/LegalBenchPro_intro_draft.pdf` contains:

- abstract placeholder;
- introduction;
- contribution framing;
- section headings for related work, dataset, analysis, limitations, ethics, and rubric.

## Immediate Next Sections

The next writing priority is:

1. Dataset construction.
2. Model and prompt settings.
3. Scoring and human validation protocol.
4. Preliminary descriptive statistics.
5. Limitations and ethical considerations.

## Count Reconciliation

The current workbook snapshot reports:

- 76 Chinese real-case issue-stance prompts;
- 15 de-identified Chinese civil judgments;
- 38 Chinese real-case legal issues, paired into support/opposition stance prompts;
- 868 public-exam instances;
- 22 model configurations in the main multimodel sheets;
- 20,768 LLM-generated response cells in the main multimodel sheets
  (1,672 Chinese real-case responses and 19,096 public-exam responses).

The older Overleaf PDF used stale counts in the introduction, including 971 public-exam
instances and 18 models. Those should be replaced with the current workbook counts above
unless the dataset is intentionally expanded again before submission.

## EMNLP-Readiness Checklist

- Finalize dataset counts and source taxonomy.
- Freeze model list and prompt conditions.
- Complete a human-validation pilot.
- Add agreement statistics or clearly mark them as future work.
- Add model ranking tables and split-transfer analysis.
- Add source-distribution and de-identification details.
- Decide whether the full dataset is releasable or only available by request.
