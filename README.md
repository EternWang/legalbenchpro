# LegalBenchPro

LegalBenchPro is an EMNLP-targeted research benchmark for evaluating large language
models on open-ended legal reasoning. The project asks whether models that perform well
on scalable public legal-exam tasks also transfer to de-identified, practice-oriented
case analysis.

The benchmark separates two evaluation settings:

- public legal-exam tasks with reference answers;
- de-identified Chinese civil judgment prompts that require stance-aware,
  statute-grounded legal analysis.

This repository is a public research snapshot. It exposes the dataset schema, scoring
protocol, audit workflow, manuscript materials, expanded content samples, and full
metadata indexes while keeping the complete workbook private until licensing, privacy,
and redistribution review are complete.

## Snapshot

| Component | Current count | Evaluation design |
| --- | ---: | --- |
| Chinese real-case split | 76 issue-stance prompts | Citation-aware rubric with human validation in progress |
| Source judgments | 15 de-identified civil judgments | Paired support/opposition issue prompts |
| Public-exam split | 868 instances | Reference-answer consistency scoring |
| Model configurations | 22 | Standard, reasoning-enabled, and step-by-step prompting modes |
| Human validation pilots | 10 real-case rows; 80 public-exam rows | Staged for reviewer calibration and agreement analysis |

The public snapshot includes 24 excerpted Chinese real-case rows, 80 excerpted
public-exam rows, full metadata indexes for the 76 real-case prompts and 868 public-exam
instances, model-configuration metadata, and source/domain distribution tables. It does
not include the full prompt matrix, full reference answers, full model outputs, or human
review sheets.

## Research Contribution

LegalBenchPro is designed around a gap in current legal LLM evaluation: public legal
benchmarks are scalable and convenient, but legal practice often requires working from
long facts, contested interpretations, jurisdiction-specific authorities, and
defensible argument structure. This project contributes:

- a two-part benchmark that separates public-exam evaluation from real-case legal
  analysis;
- a curated Chinese civil judgment split with paired issue-stance prompts;
- a multimodel evaluation matrix spanning 22 model configurations;
- a scoring protocol that distinguishes answer matching from citation-aware legal
  reasoning;
- a reproducible public workflow for sample extraction, metadata generation, and
  manuscript tracking.

## What To Inspect

For a quick review of the project, start with:

- `paper/introduction_revised.tex` for the current manuscript introduction;
- `docs/DATA_CARD.md` for scope, counts, intended uses, and release constraints;
- `docs/ANNOTATION_PROTOCOL.md` for human-validation and scoring design;
- `docs/AI_WORKFLOW.md` for auditability and AI-assistance safeguards;
- `data/sample/legalbenchpro_cn_judgments_sample.csv` for real-case content excerpts;
- `data/sample/legalbenchpro_public_exam_sample.csv` for public-exam content excerpts;
- `data/metadata/cn_judgments_index.csv` and `data/metadata/public_exam_index.csv`
  for full-row metadata indexes;
- `scripts/extract_public_sample.py` for the reproducible sample-export workflow.

## Repository Map

```text
paper/
  LegalBenchPro_intro_draft.pdf       # Overleaf PDF snapshot of the current draft
  introduction_revised.tex            # Dataset-aligned introduction ready for Overleaf
  manuscript_working_draft.md         # Working paper skeleton for GitHub readers
docs/
  DATA_CARD.md                        # Dataset scope, fields, release status, risks
  ANNOTATION_PROTOCOL.md              # Human validation plan and scoring dimensions
  AI_WORKFLOW.md                      # AI-assisted research workflow and safeguards
  SCORING_RUBRIC.md                   # Compact scoring rubric
  MANUSCRIPT_STATUS.md                # What is complete and what remains
data/
  sample/legalbenchpro_cn_judgments_sample.csv
  sample/legalbenchpro_public_exam_sample.csv
  sample/legalbenchpro_public_sample.csv
  metadata/cn_judgments_index.csv
  metadata/public_exam_index.csv
  metadata/dataset_summary.json
  metadata/model_configurations.csv
  metadata/source_distribution.csv
scripts/
  extract_public_sample.py            # Rebuilds the public sample and metadata
src/legalbenchpro/
  workbook.py                         # Small workbook helpers used by scripts
tests/
  test_workbook.py                    # Lightweight smoke tests for public utilities
```

## Reproduce The Public Snapshot

The full workbook is not committed. To regenerate the public sample from a local
private workbook:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "$PWD\src"
python .\scripts\extract_public_sample.py `
  --workbook "C:\path\to\Data Set.xlsx" `
  --out-dir data `
  --cn-sample-size 24 `
  --bar-sample-size 80
```

## Validation

The repository includes a small test suite:

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m unittest discover -s tests
python -m compileall scripts src
```

## Release Status

This is a research preview, not a final benchmark release. The public content samples
are excerpted and do not include the full prompt matrix, full reference answers, full
model outputs, or human review sheets. The full dataset will require a final licensing,
privacy, and source-distribution review before release.

## Author

Hongyu Wang. Manuscript and benchmark in preparation.

## Disclaimer

This repository is for research on model evaluation. It is not legal advice, a legal
research product, or a substitute for jurisdiction-specific legal review.
