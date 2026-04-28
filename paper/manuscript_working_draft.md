# LegalBenchPro: Legal Reasoning Benchmarks Beyond Public Exams

Status: working manuscript skeleton. The current Overleaf PDF snapshot is
`LegalBenchPro_intro_draft.pdf`.

## Abstract

We introduce LegalBenchPro, a two-part benchmark for evaluating large language models
on open-ended legal reasoning. The benchmark contrasts scalable public legal-exam tasks
with de-identified real-case Chinese civil judgment prompts. The public-exam split
supports reference-based scoring across multiple legal systems, while the real-case
split tests stance-aware, statute-grounded legal analysis over curated factual
backgrounds. The current research snapshot contains 76 real-case issue-stance prompts,
868 public-exam instances, 22 model configurations, and 20,768 LLM-generated response
cells in the main multimodel sheets. Human validation is in progress.

## 1. Introduction

Large language models are now routinely evaluated on legal tasks. They summarize legal
documents, answer bar-style questions, retrieve legal authorities, and perform strongly
on public legal benchmarks. These results are informative, but they leave open a
practical question: does strong performance on public and standardized legal tasks carry
over to de-identified case analysis derived from real court judgments?

LegalBenchPro is a two-part benchmark designed around this gap. The first part is a
public-exam split containing 868 standardized open-ended legal exam instances from
Australia, China, the United Kingdom, and the United States. The second part is a
de-identified real-case split containing 76 issue-stance prompts derived from 15 Chinese
civil judgments and 38 legal issues. Each real-case prompt is built from a curated case
background and asks the model to produce a statute-grounded analysis either supporting
or opposing the court's conclusion.

This paired design allows the same factual setting to be evaluated under competing
analytic positions. It also allows the benchmark to ask whether model rankings on
scalable public legal tasks transfer to more practice-oriented legal analysis. The
current workbook snapshot evaluates 22 model configurations across standard modes,
reasoning-enabled modes, and explicit step-by-step prompting setups, yielding 20,768
LLM-generated response cells across the two main evaluation splits.

The public-exam split is scored by reference-based answer consistency. The real-case
split is scored with a citation-aware rubric that focuses on legal authority selection,
constraint extraction, and rule-to-fact reasoning. Human validation is in progress, with
pilot rows staged for both the Chinese real-case split and the public-exam split.

## 2. Dataset

### 2.1 Public-Exam Split

The public-exam split contains open-ended legal exam instances with reference answers.
The current workbook snapshot contains 868 rows from multiple jurisdictions and legal
systems. These rows support reference-based answer-match scoring.

### 2.2 Chinese Real-Case Split

The real-case split contains 76 issue-stance prompts derived from de-identified Chinese
civil judgments. Each prompt is built from a curated case background and issue-specific
court result. Paired stance prompts keep the case background fixed while asking the
model to support or oppose the court's conclusion.

## 3. Models And Prompting Conditions

The current workbook snapshot contains 22 model configurations spanning commercial,
open-weight, and reasoning-enabled systems. The final manuscript should document model
versions, access route, temperature, maximum output length, and prompt mode.

## 4. Scoring

The public-exam split uses a reference-based 0-4 answer-match score. The Chinese
real-case split uses a three-dimensional rubric:

- citation relevance;
- constraint extraction and compliance;
- reasoning effectiveness.

Human validation is staged in separate human review sheets and is currently in
progress.

## 5. Analysis Plan

The final analysis will compare:

- model rankings across public-exam and real-case settings;
- reasoning-enabled modes against ordinary modes;
- explicit step-by-step prompting against model-native reasoning;
- model-based or automated scoring against human validation.

## 6. Limitations

The real-case split currently focuses on Chinese civil cases and should not be treated
as representative of all legal domains. The public-exam and real-case splits also differ
in source format, reference-answer availability, and evaluation regime.

## 7. Ethics

This benchmark is for model evaluation, not legal advice. Real-case prompts require
careful de-identification and source review. Public release of the full data requires
licensing and privacy review.
