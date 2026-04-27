# Data Card

## Dataset Name

LegalBenchPro, public research snapshot v0.1.

## Purpose

LegalBenchPro evaluates whether large language models that perform well on scalable
public legal tasks also perform well on practice-oriented legal analysis. The benchmark
separates public-exam evaluation from de-identified real-case analysis so that model
rankings, reasoning modes, and scoring regimes can be compared across settings.

## Current Snapshot Counts

The committed metadata file reports counts extracted from the local workbook:

- Chinese real-case split: 76 issue-stance prompts.
- Public-exam split: 868 instances.
- Model configurations: 22 in the main multimodel sheets.
- Public content previews: 10 English-language Chinese real-case preview rows and 20
  public-exam preview rows.
- Public metadata: model configurations, source/domain distribution summaries, wider
  Markdown case cards, and machine-readable snapshot counts.
- Human validation staging: 10 Chinese judgment rows and 80 public-exam rows.

See `data/metadata/dataset_summary.json` for the machine-readable summary.

## Splits

### Chinese Real-Case Split

This split is derived from de-identified Chinese civil judgments. Each prompt is built
from a curated case background and an issue-specific court result. Many cases are paired
into support/opposition stance prompts so that the same factual setting can be tested
under different analytic positions.

Key fields include:

- review id and document id;
- issue id and issue title;
- de-identified case theme and court-result summary;
- model prompt;
- cited authorities and supported legal proposition for scorer-side reference;
- law category and detail;
- model answer and rubric scores.

### Public-Exam Split

This split uses public legal exam materials and reference answers from multiple legal
systems. It is designed to be scalable and reference-based.

Key fields include:

- review id, document id, issue id, and issue title;
- prompt and reference answer;
- source country / legal system;
- source body and source URL;
- law category and detail;
- model answer and answer-match score.

## Public Snapshot

The public snapshot has two layers.

English-language content previews:

- `data/sample/preview_cases.md`
- `data/sample/legalbenchpro_cn_judgments_sample.csv`
- `data/sample/legalbenchpro_public_exam_sample.csv`

These files show representative schema, task previews, reference-answer previews, and
one example model-answer preview. CSV cells are capped at 420 characters, while
`preview_cases.md` presents the same sample rows as wider case cards for GitHub
reading. These samples are not sufficient for benchmarking models.

Summary metadata:

- `data/metadata/model_configurations.csv`
- `data/metadata/source_distribution.csv`
- `data/metadata/dataset_summary.json`

These files expose source/legal-system structure, law-category coverage, model
configurations, and snapshot counts without publishing row-level full indexes, the full
prompt matrix, full reference answers, complete model outputs, or human review sheets.

## Full Data Release Status

The full workbook is intentionally excluded from this repository. Before public release,
the project needs final review for:

- distribution rights for public exam materials;
- de-identification and privacy of case-derived prompts;
- whether model outputs can be redistributed under the relevant providers' terms;
- whether source references should be included, summarized, or replaced with links.

## Intended Uses

Appropriate uses:

- studying benchmark design for legal reasoning;
- auditing model outputs against structured legal-reasoning rubrics;
- comparing public-exam and real-case evaluation settings;
- demonstrating reproducible AI-assisted research workflows.

Out-of-scope uses:

- legal advice;
- ranking lawyers, judges, institutions, or jurisdictions;
- deployment as a legal decision system;
- training on full case materials without licensing review.

## Known Limitations

- The real-case split currently focuses on Chinese civil cases, with medical and
  contract-related disputes strongly represented.
- Human validation is ongoing.
- The public-exam split and the real-case split differ in source availability,
  reference-answer style, and scoring regime.
- The current manuscript and workbook counts should be reconciled before final
  submission.
