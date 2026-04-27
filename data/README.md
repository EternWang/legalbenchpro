# Data Preview

This folder contains a compact public preview of LegalBenchPro. The full workbook is
not included in the repository while licensing, privacy, redistribution, and human
validation review are still in progress.

## What Is Public

| File | Rows | Purpose |
| --- | --- | --- |
| sample/legalbenchpro_cn_judgments_sample.csv | 10 | Short excerpts from the Chinese civil judgment split |
| sample/legalbenchpro_public_exam_sample.csv | 20 | Short excerpts from the public legal-exam split |
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
| 医疗损害责任纠纷 | 50 |
| 买卖合同纠纷 | 6 |
| 机动车交通事故责任纠纷 | 6 |
| 房屋买卖合同纠纷 | 4 |
| 承揽 / 供货安装合同纠纷 | 4 |
| 生命权、身体权、健康权纠纷 | 4 |
| 排除妨害纠纷 | 2 |

## Public-Exam Legal Domains

| Law category | Rows |
| --- | --- |
| Tort | 243 |
| Business Organizations / Agency | 126 |
| Foundations of Legal Knowledge | 68 |
| Secured Transactions / Commercial Law | 67 |
| Succession / Trusts / Estates | 61 |
| Family | 58 |
| Professional Responsibility / Legal Ethics | 38 |
| Civil Procedure | 26 |

## Release Note

This is a research preview for manuscript and application review. The complete dataset
is available only after final source-distribution, privacy, and human-validation checks.
