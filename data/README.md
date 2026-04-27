# Data Preview

This folder contains a compact public preview of LegalBenchPro. The full workbook is
not included in the repository while licensing, privacy, redistribution, and human
validation review are still in progress.

## Content Preview Files

| File | Rows | Purpose |
| --- | --- | --- |
| sample/legalbenchpro_cn_judgments_sample.csv | 10 | Short excerpts from the Chinese civil judgment split |
| sample/legalbenchpro_public_exam_sample.csv | 20 | Short excerpts from the public legal-exam split |

## Summary Metadata Files

| File | Rows | Purpose |
| --- | --- | --- |
| metadata/model_configurations.csv | 22 | Model names and workbook sheet coverage |
| metadata/source_distribution.csv | 55 | Top source, law-category, and case-type counts |
| metadata/dataset_summary.json | 1 | Machine-readable snapshot summary |

All preview CSV cells are capped at 180 characters so that GitHub's table view
stays readable. The preview does not include full prompts, full reference answers, full
model-output matrices, or human review sheets.

## Snapshot Counts

| Component | Count |
| --- | --- |
| Chinese real-case issue-stance prompts | 76 |
| Public legal-exam instances | 868 |
| Model configurations | 22 |
| Human validation pilot rows | 10 Chinese real-case rows; 80 public-exam rows |

## Public-Exam Country Coverage

| Source country | Rows |
| --- | --- |
| United States | 604 |
| China | 100 |
| United Kingdom | 86 |
| Australia | 78 |

## Chinese Real-Case Coverage

| Case type | Rows |
| --- | --- |
| Medical malpractice liability dispute | 50 |
| Motor vehicle accident liability dispute | 6 |
| Sales contract dispute | 6 |
| Life, bodily integrity, and health-rights dispute | 4 |
| Real-estate sales contract dispute | 4 |
| Work/service and supply-installation contract dispute | 4 |
| Removal-of-obstruction dispute | 2 |

## Public-Exam Legal Domain Summary

The repository preview intentionally shows only the top legal-domain counts. The
summary below explains why the visible top-domain rows do not add up to 868.

| Group | Rows |
| --- | --- |
| Top legal domains listed in source_distribution.csv | 687 |
| Other legal domains | 181 |
| Total public-exam instances | 868 |

Top examples:

| Law category | Rows |
| --- | --- |
| Tort | 243 |
| Business Organizations / Agency | 126 |
| Foundations of Legal Knowledge | 68 |
| Secured Transactions / Commercial Law | 67 |

## Release Note

This is a research preview for manuscript and application review. The complete dataset
is available only after final source-distribution, privacy, and human-validation checks.
