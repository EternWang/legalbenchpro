# AI-Assisted Research Workflow

LegalBenchPro is also a case study in AI-assisted research engineering. The workflow is
designed to use LLMs as productivity tools while preserving auditability and human
control.

## Pipeline Overview

1. Curate source materials and convert them into structured workbook rows.
2. Generate model prompts from standardized templates.
3. Run model outputs across multiple model configurations.
4. Score outputs with structured rubrics.
5. Audit missing answers, malformed outputs, score gaps, and authority-use patterns.
6. Stage human validation samples.
7. Compare public-exam scoring, real-case scoring, and human judgments.

## Where AI Assistance Is Used

AI tools may assist with:

- code generation for workbook transformation and audit scripts;
- drafting prompt templates;
- producing candidate summaries for human review;
- generating model outputs under controlled prompt settings;
- identifying likely failure modes for manual inspection.

AI tools do not replace:

- source selection decisions;
- de-identification review;
- final legal scoring decisions;
- manuscript claims;
- release and licensing decisions.

## Safeguards

The workflow uses several safeguards:

- closed-book prompts for model-answer generation;
- separate scorer-side fields for hidden authorities and supported propositions;
- explicit review constraints against invented facts and external lookup;
- audit files for workbook transformations;
- human validation staging before final claims about benchmark performance.

## Reproducibility Practices

The public repo keeps:

- scripts used to regenerate the public sample;
- machine-readable dataset metadata;
- scoring and annotation protocol documents;
- a manuscript-status file separating completed work from work in progress.

The private workspace keeps:

- full workbooks;
- full model-output matrices;
- private or licensing-sensitive source material;
- intermediate batch outputs and logs.

## Known Risks

- LLM-generated code can silently mishandle encodings, merged spreadsheet headers, or
  row alignment.
- Model-based scoring can over-credit fluent but legally weak answers.
- Public legal exam materials may not be distributable in full.
- Real-case prompts require careful de-identification and source review.

The repo is structured so these risks are visible rather than hidden.

